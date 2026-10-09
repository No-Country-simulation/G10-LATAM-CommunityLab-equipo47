"""Utilidades compartidas para llamar al LLM (Gemini) con caché y presupuesto.

Reúne el cliente, la lectura de prompts, la caché local y el bucle de llamada con
reintentos acotados, para que el análisis y los generadores no dupliquen esa lógica.

Los mensajes concretos y la validación de cada caso se inyectan como funciones desde
quien usa el módulo.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Callable, TypeVar

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import (
    ChatGoogleGenerativeAIError,
    GoogleRateLimitError,
)
from pydantic import BaseModel, ValidationError

from .config import (
    ESPERA_MAXIMA_REINTENTO_SEG,
    ESPERA_MINIMA_ENTRE_LLAMADAS_SEG,
    ESPERA_POR_DEFECTO_429_SEG,
    MAX_LLAMADAS_POR_LOTE,
    MAX_REINTENTOS_429,
    MAX_REINTENTOS_CLIENTE,
    MODELOS_MUESTREO_FIJO,
    REINTENTOS_VALIDACION,
    TIMEOUT_LLM_SEG,
    Configuracion,
)

Dormir = Callable[[float], None]

T = TypeVar("T", bound=BaseModel)


class ErrorLlm(Exception):
    """Error claro al llamar al LLM."""


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
    emitiría un aviso); en el resto la deja en 0 para que la salida sea estable. El
    cliente se configura sin reintentos ocultos (`max_retries=1`).
    """
    if not config.gemini_api_key:
        raise ErrorLlm("Falta GEMINI_API_KEY en el entorno para llamar al LLM.")

    parametros: dict[str, Any] = {
        "model": config.gemini_model,
        "google_api_key": config.gemini_api_key,
        "max_retries": MAX_REINTENTOS_CLIENTE,
        "timeout": TIMEOUT_LLM_SEG,
    }
    if not usa_muestreo_fijo(config.gemini_model):
        parametros["temperature"] = 0

    return ChatGoogleGenerativeAI(**parametros)


def crear_llm_estructurado(config: Configuracion, esquema: type[BaseModel]):
    """Devuelve el LLM listo para devolver `esquema` (incluyendo la salida cruda)."""
    return crear_llm(config).with_structured_output(esquema, include_raw=True)


# --- Prompt y versiones -------------------------------------------------------

def leer_prompt(ruta: str | Path) -> str:
    """Lee un prompt de texto en UTF-8."""
    camino = Path(ruta)
    try:
        return camino.read_text(encoding="utf-8")
    except OSError as exc:
        raise ErrorLlm(f"No se pudo leer el prompt: {camino.name}") from exc


def version_prompt(texto: str) -> str:
    """Versión corta y estable de un texto (para la clave de la caché)."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


# --- Caché --------------------------------------------------------------------

def _ruta_cache(directorio: str | Path, clave: str) -> Path:
    return Path(directorio) / f"{clave}.json"


def leer_cache(directorio: str | Path, clave: str, tipo: type[T]) -> T | None:
    """Lee y valida una respuesta cacheada; devuelve `None` si no existe o está rota."""
    camino = _ruta_cache(directorio, clave)
    if not camino.is_file():
        return None
    try:
        datos = json.loads(camino.read_text(encoding="utf-8"))
        return tipo.model_validate(datos["respuesta"])
    except (OSError, ValueError, KeyError, ValidationError):
        # Caché corrupta o de otro formato: se trata como si no existiera.
        return None


def escribir_cache(
    directorio: str | Path,
    clave: str,
    config: Configuracion,
    version: str,
    respuesta: BaseModel,
) -> None:
    """Guarda una respuesta del LLM con sus metadatos de trazabilidad."""
    camino = _ruta_cache(directorio, clave)
    camino.parent.mkdir(parents=True, exist_ok=True)
    contenido = {
        "clave": clave,
        "modelo": config.gemini_model,
        "version_prompt": version,
        "respuesta": respuesta.model_dump(mode="json"),
    }
    camino.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")


# --- Extracción y errores -----------------------------------------------------

def espera_sugerida(exc: Exception) -> float:
    """Espera ante un 429: usa el `retry_delay` sugerido, acotado a un tope."""
    coincidencia = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", str(exc))
    segundos = int(coincidencia.group(1)) if coincidencia else ESPERA_POR_DEFECTO_429_SEG
    return min(max(float(segundos), ESPERA_MINIMA_ENTRE_LLAMADAS_SEG), ESPERA_MAXIMA_REINTENTO_SEG)


def texto_salida(salida: Any) -> str:
    """Extrae el texto crudo de una salida estructurada, para el prompt de reparación."""
    if isinstance(salida, dict):
        contenido = getattr(salida.get("raw"), "content", None)
        if isinstance(contenido, str):
            return contenido
        if contenido:
            return json.dumps(contenido, ensure_ascii=False)
    return "(sin contenido utilizable)"


def extraer_parseado(salida: Any, tipo: type[T]) -> tuple[T | None, Exception | None]:
    """Convierte la salida del LLM en `tipo`; devuelve `(objeto, error)`."""
    if isinstance(salida, tipo):
        return salida, None
    if isinstance(salida, dict):
        parsed = salida.get("parsed")
        if isinstance(parsed, tipo):
            return parsed, None
        if parsed is not None:
            try:
                return tipo.model_validate(parsed), None
            except ValidationError as exc:
                return None, exc
        error = salida.get("parsing_error") or ValueError("el LLM no devolvió una respuesta válida")
        return None, error
    try:
        return tipo.model_validate(salida), None
    except ValidationError as exc:
        return None, exc


# --- Llamada al LLM con presupuesto -------------------------------------------

def obtener_respuesta_estructurada(
    llm: Any,
    mensajes: list[Any],
    *,
    tipo: type[T],
    validar: Callable[[T | None], Exception | None],
    reparar: Callable[[Exception, Any], list[Any]],
    error_cls: type[Exception],
    dormir: Dormir,
) -> T:
    """Llama al LLM respetando el tope de llamadas, los reintentos 429 y una reparación.

    - `validar(parsed)` devuelve un error (o `None` si es válido).
    - `reparar(error, salida)` construye los mensajes para el reintento de reparación.
    - Los errores de presupuesto, cuota agotada o validación se lanzan con `error_cls`.
    """
    llamadas = 0
    reintentos_429 = 0
    reparaciones = 0
    espera_pendiente = 0.0
    ultimo_error: Exception | None = None

    while True:
        if llamadas >= MAX_LLAMADAS_POR_LOTE:
            raise error_cls(
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
                raise error_cls(
                    "El LLM alcanzó el límite de solicitudes (429) y se agotaron los reintentos."
                ) from exc
            reintentos_429 += 1
            espera_pendiente = espera_sugerida(exc)
            continue
        except ChatGoogleGenerativeAIError as exc:
            raise error_cls(
                f"El LLM devolvió un error no recuperable ({type(exc).__name__})."
            ) from exc

        llamadas += 1
        parsed, error = extraer_parseado(salida, tipo)
        if error is None:
            error = validar(parsed)
        if error is None:
            return parsed  # type: ignore[return-value]

        ultimo_error = error
        if reparaciones >= REINTENTOS_VALIDACION:
            raise error_cls(
                "La salida del LLM siguió sin ser válida tras el reintento de reparación."
            ) from error
        reparaciones += 1
        mensajes = reparar(error, salida)
