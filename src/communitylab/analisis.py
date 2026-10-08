"""Análisis de sentimiento y temas de un lote con Gemini (vía LangChain).

Una sola llamada por lote (con todas las interacciones), salida estructurada validada
con Pydantic, puntuación de relevancia explicable (sub-puntuaciones del LLM + pesos del
código) y caché local de cada respuesta.

El cliente del LLM se recibe como parámetro para poder simularlo en los tests.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Callable

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import (
    ChatGoogleGenerativeAIError,
    GoogleRateLimitError,
)
from pydantic import ValidationError

from .config import (
    DIRECTORIO_CACHE_LLM,
    ESPERA_MAXIMA_REINTENTO_SEG,
    ESPERA_MINIMA_ENTRE_LLAMADAS_SEG,
    ESPERA_POR_DEFECTO_429_SEG,
    MAX_LLAMADAS_POR_LOTE,
    MAX_REINTENTOS_429,
    MAX_REINTENTOS_CLIENTE,
    MODELOS_MUESTREO_FIJO,
    PESOS_PUNTUACION,
    REINTENTOS_VALIDACION,
    RUTA_PROMPT_ANALISIS,
    TIMEOUT_LLM_SEG,
    Configuracion,
)
from .modelos import (
    InformeAnalisis,
    InteraccionAnalizada,
    LoteEntrada,
    MetadatosInforme,
    PuntuacionRelevancia,
    RespuestaLlmAnalisis,
)

Dormir = Callable[[float], None]


class ErrorAnalisis(Exception):
    """Error claro al analizar un lote con el LLM."""


# --- Cliente del LLM ----------------------------------------------------------

def usa_muestreo_fijo(modelo: str) -> bool:
    """Indica si el modelo ignora los parámetros de muestreo (p. ej. `temperature`)."""
    if not modelo:
        return False
    normalizado = modelo.lower().rsplit("/", 1)[-1]
    return normalizado in MODELOS_MUESTREO_FIJO


def crear_llm(config: Configuracion) -> ChatGoogleGenerativeAI:
    """Crea el modelo de chat de Gemini según la configuración.

    No fija `temperature` en los modelos de muestreo fijo (la ignorarían y LangChain
    emitiría un aviso); en el resto la deja en 0 para que el análisis sea estable.
    El cliente se configura sin reintentos ocultos (`max_retries=1`).
    """
    if not config.gemini_api_key:
        raise ErrorAnalisis("Falta GEMINI_API_KEY en el entorno para llamar al LLM.")

    parametros: dict[str, Any] = {
        "model": config.gemini_model,
        "google_api_key": config.gemini_api_key,
        "max_retries": MAX_REINTENTOS_CLIENTE,
        "timeout": TIMEOUT_LLM_SEG,
    }
    if not usa_muestreo_fijo(config.gemini_model):
        parametros["temperature"] = 0

    return ChatGoogleGenerativeAI(**parametros)


def crear_llm_estructurado(config: Configuracion):
    """Devuelve el LLM listo para devolver `RespuestaLlmAnalisis` (con la salida cruda)."""
    return crear_llm(config).with_structured_output(RespuestaLlmAnalisis, include_raw=True)


# --- Prompt y caché -----------------------------------------------------------

def cargar_prompt(ruta: str | Path = RUTA_PROMPT_ANALISIS) -> str:
    """Lee el prompt de análisis desde `prompts/analisis.md`."""
    camino = Path(ruta)
    try:
        return camino.read_text(encoding="utf-8")
    except OSError as exc:
        raise ErrorAnalisis(f"No se pudo leer el prompt de análisis: {camino.name}") from exc


def version_prompt(texto: str) -> str:
    """Versión corta y estable del prompt (para la clave de la caché)."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


def clave_cache(modelo: str, version: str, lote: LoteEntrada) -> str:
    """Clave de caché: modelo + versión del prompt + hash de la entrada."""
    entrada = json.dumps(lote.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
    base = f"{modelo}|{version}|{entrada}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


# --- Puntuación ---------------------------------------------------------------

def calcular_puntuacion(
    subpuntuaciones: dict[str, int],
    pesos: dict[str, float] | None = None,
) -> PuntuacionRelevancia:
    """Calcula la puntuación final (0-100) a partir de las sub-puntuaciones y los pesos."""
    pesos = dict(pesos or PESOS_PUNTUACION)
    faltan = [nombre for nombre in pesos if nombre not in subpuntuaciones]
    if faltan:
        raise ErrorAnalisis("Faltan sub-puntuaciones: " + ", ".join(faltan))

    final = round(sum(int(subpuntuaciones[nombre]) * peso for nombre, peso in pesos.items()))
    final = max(0, min(100, final))

    return PuntuacionRelevancia(
        subpuntuaciones={nombre: int(subpuntuaciones[nombre]) for nombre in pesos},
        pesos=pesos,
        puntuacion_final=final,
    )


# --- Mensajes -----------------------------------------------------------------

def _texto_lote(lote: LoteEntrada) -> str:
    """Serializa el lote con índices, para que el LLM referencie cada interacción."""
    interacciones = [
        {
            "indice": indice,
            "autor": interaccion.autor,
            "canal": interaccion.canal,
            "tipo": interaccion.tipo,
            "texto": interaccion.texto,
        }
        for indice, interaccion in enumerate(lote.interacciones)
    ]
    return json.dumps(
        {
            "origen_comunidad": lote.origen_comunidad,
            "periodo_referencia": lote.periodo_referencia,
            "interacciones": interacciones,
        },
        ensure_ascii=False,
        indent=2,
    )


def _construir_mensajes(prompt: str, lote: LoteEntrada) -> list[Any]:
    return [SystemMessage(prompt), HumanMessage(_texto_lote(lote))]


def _mensajes_reparacion(prompt: str, lote: LoteEntrada, error: Exception, salida: Any) -> list[Any]:
    return [
        SystemMessage(prompt),
        HumanMessage(_texto_lote(lote)),
        AIMessage(_texto_salida(salida)),
        HumanMessage(
            "Tu respuesta anterior no cumple el esquema solicitado: "
            f"{error}. Devuelve de nuevo SOLO el objeto JSON corregido, con un índice "
            "por cada interacción del lote, sin repetir ni omitir ninguno."
        ),
    ]


def _texto_salida(salida: Any) -> str:
    if isinstance(salida, dict):
        contenido = getattr(salida.get("raw"), "content", None)
        if isinstance(contenido, str):
            return contenido
        if contenido:
            return json.dumps(contenido, ensure_ascii=False)
    return "(sin contenido utilizable)"


# --- Llamada al LLM con presupuesto -------------------------------------------

def _espera_sugerida(exc: Exception) -> float:
    """Espera ante un 429: usa el `retry_delay` sugerido, acotado a un tope."""
    coincidencia = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", str(exc))
    segundos = int(coincidencia.group(1)) if coincidencia else ESPERA_POR_DEFECTO_429_SEG
    return min(max(float(segundos), ESPERA_MINIMA_ENTRE_LLAMADAS_SEG), ESPERA_MAXIMA_REINTENTO_SEG)


def _extraer_parseado(salida: Any) -> tuple[RespuestaLlmAnalisis | None, Exception | None]:
    if isinstance(salida, RespuestaLlmAnalisis):
        return salida, None
    if isinstance(salida, dict):
        parsed = salida.get("parsed")
        if isinstance(parsed, RespuestaLlmAnalisis):
            return parsed, None
        if parsed is not None:
            try:
                return RespuestaLlmAnalisis.model_validate(parsed), None
            except ValidationError as exc:
                return None, exc
        error = salida.get("parsing_error") or ValueError("el LLM no devolvió una respuesta válida")
        return None, error
    try:
        return RespuestaLlmAnalisis.model_validate(salida), None
    except ValidationError as exc:
        return None, exc


def _validar_cobertura(parsed: RespuestaLlmAnalisis | None, lote: LoteEntrada) -> Exception | None:
    if parsed is None:
        return ValueError("no hay análisis que revisar")
    esperados = list(range(len(lote.interacciones)))
    indices = sorted(analisis.indice for analisis in parsed.interacciones)
    if indices != esperados:
        return ValueError(
            f"se esperaban índices {esperados} (uno por interacción, sin repetir) y llegaron {indices}"
        )
    return None


def _obtener_respuesta(
    llm: Any,
    prompt: str,
    lote: LoteEntrada,
    dormir: Dormir,
) -> RespuestaLlmAnalisis:
    """Llama al LLM respetando el tope de llamadas, los reintentos 429 y una reparación."""
    mensajes = _construir_mensajes(prompt, lote)
    llamadas = 0
    reintentos_429 = 0
    reparaciones = 0
    espera_pendiente = 0.0
    ultimo_error: Exception | None = None

    while True:
        if llamadas >= MAX_LLAMADAS_POR_LOTE:
            raise ErrorAnalisis(
                f"Se agotó el presupuesto de {MAX_LLAMADAS_POR_LOTE} llamadas al LLM para este lote."
            ) from ultimo_error

        if llamadas > 0:
            dormir(max(ESPERA_MINIMA_ENTRE_LLAMADAS_SEG, espera_pendiente))
            espera_pendiente = 0.0

        try:
            salida = llm.invoke(mensajes)
        except GoogleRateLimitError as exc:
            llamadas += 1
            ultimo_error = exc
            if reintentos_429 >= MAX_REINTENTOS_429:
                raise ErrorAnalisis(
                    "El LLM alcanzó el límite de solicitudes (429) y se agotaron los reintentos."
                ) from exc
            reintentos_429 += 1
            espera_pendiente = _espera_sugerida(exc)
            continue
        except ChatGoogleGenerativeAIError as exc:
            raise ErrorAnalisis(
                f"El LLM devolvió un error no recuperable ({type(exc).__name__})."
            ) from exc

        llamadas += 1
        parsed, error = _extraer_parseado(salida)
        if error is None:
            error = _validar_cobertura(parsed, lote)
        if error is None:
            return parsed  # type: ignore[return-value]

        ultimo_error = error
        if reparaciones >= REINTENTOS_VALIDACION:
            raise ErrorAnalisis(
                "La salida del LLM siguió sin ser válida tras el reintento de reparación."
            ) from error
        reparaciones += 1
        mensajes = _mensajes_reparacion(prompt, lote, error, salida)


# --- Caché --------------------------------------------------------------------

def _ruta_cache(directorio: str | Path, clave: str) -> Path:
    return Path(directorio) / f"{clave}.json"


def _leer_cache(directorio: str | Path, clave: str) -> RespuestaLlmAnalisis | None:
    camino = _ruta_cache(directorio, clave)
    if not camino.is_file():
        return None
    try:
        datos = json.loads(camino.read_text(encoding="utf-8"))
        return RespuestaLlmAnalisis.model_validate(datos["respuesta"])
    except (OSError, ValueError, KeyError, ValidationError):
        # Caché corrupta o de otro formato: se trata como si no existiera.
        return None


def _escribir_cache(
    directorio: str | Path,
    clave: str,
    config: Configuracion,
    version: str,
    respuesta: RespuestaLlmAnalisis,
) -> None:
    camino = _ruta_cache(directorio, clave)
    camino.parent.mkdir(parents=True, exist_ok=True)
    contenido = {
        "clave": clave,
        "modelo": config.gemini_model,
        "version_prompt": version,
        "respuesta": respuesta.model_dump(mode="json"),
    }
    camino.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")


# --- Orquestación -------------------------------------------------------------

def _construir_informe(
    lote: LoteEntrada,
    config: Configuracion,
    respuesta: RespuestaLlmAnalisis,
    version: str,
    desde_cache: bool,
) -> InformeAnalisis:
    por_indice = {analisis.indice: analisis for analisis in respuesta.interacciones}
    interacciones = [
        InteraccionAnalizada(
            autor=original.autor,
            canal=original.canal,
            tipo=original.tipo,
            texto=original.texto,
            sentimiento=por_indice[indice].sentimiento,
            temas=por_indice[indice].temas,
            puntuacion=calcular_puntuacion(por_indice[indice].subpuntuaciones.model_dump()),
            motivo_puntuacion=por_indice[indice].motivo,
        )
        for indice, original in enumerate(lote.interacciones)
    ]

    return InformeAnalisis(
        origen_comunidad=lote.origen_comunidad,
        periodo_referencia=lote.periodo_referencia,
        total_interacciones_procesadas=len(interacciones),
        sentimiento_predominante=respuesta.resumen.sentimiento_predominante,
        temas_principales=respuesta.resumen.temas_principales,
        interacciones=interacciones,
        metadatos=MetadatosInforme(
            modelo=config.gemini_model,
            version_prompt=version,
            desde_cache=desde_cache,
        ),
    )


def analizar_lote(
    lote: LoteEntrada,
    config: Configuracion,
    *,
    llm: Any | None = None,
    directorio_cache: str | Path | None = None,
    dormir: Dormir | None = None,
) -> InformeAnalisis:
    """Analiza un lote con Gemini, usando la caché local cuando exista.

    `llm` permite inyectar un modelo simulado en los tests; si es `None`, se crea a
    partir de la configuración. `directorio_cache` y `dormir` también se inyectan en
    los tests.
    """
    prompt = cargar_prompt()
    version = version_prompt(prompt)
    directorio = Path(directorio_cache) if directorio_cache is not None else Path(DIRECTORIO_CACHE_LLM)
    clave = clave_cache(config.gemini_model, version, lote)

    respuesta = _leer_cache(directorio, clave)
    if respuesta is not None:
        return _construir_informe(lote, config, respuesta, version, desde_cache=True)

    if llm is None:
        llm = crear_llm_estructurado(config)

    respuesta = _obtener_respuesta(llm, prompt, lote, dormir or time.sleep)
    _escribir_cache(directorio, clave, config, version, respuesta)

    return _construir_informe(lote, config, respuesta, version, desde_cache=False)
