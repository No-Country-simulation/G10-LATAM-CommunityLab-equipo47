"""Análisis de sentimiento y temas de un lote con Gemini (vía LangChain).

Una sola llamada por lote (con todas las interacciones), salida estructurada validada
con Pydantic, puntuación de relevancia explicable (sub-puntuaciones del LLM + pesos del
código) y caché local de cada respuesta.

El cliente, la caché, los reintentos y el tope viven en `llm.py`; aquí queda lo propio
del análisis (mensajes, cobertura y armado del informe). El cliente del LLM se recibe
como parámetro para poder simularlo en los tests.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .config import DIRECTORIO_CACHE_LLM, PESOS_PUNTUACION, RUTA_PROMPT_ANALISIS, Configuracion
from .llm import (
    Dormir,
    ErrorLlm,
    crear_llm as _crear_llm,
    crear_llm_estructurado as _crear_llm_estructurado,
    escribir_cache,
    leer_cache,
    leer_prompt,
    obtener_respuesta_estructurada,
    texto_salida,
    usa_muestreo_fijo,  # noqa: F401  (se reexporta para uso y tests)
    version_prompt,  # noqa: F401  (se reexporta para uso y tests)
)
from .modelos import (
    InformeAnalisis,
    InteraccionAnalizada,
    LoteEntrada,
    MetadatosInforme,
    PuntuacionRelevancia,
    RespuestaLlmAnalisis,
)


class ErrorAnalisis(Exception):
    """Error claro al analizar un lote con el LLM."""


# --- Cliente del LLM ----------------------------------------------------------
# La API pública del análisis conserva `ErrorAnalisis`: los envoltorios convierten
# `ErrorLlm` (que usa `llm.py`) para no cambiar el tipo de error que ya existía.

def crear_llm(config: Configuracion) -> ChatGoogleGenerativeAI:
    """Crea el modelo de chat de Gemini según la configuración."""
    try:
        return _crear_llm(config)
    except ErrorLlm as exc:
        raise ErrorAnalisis(str(exc)) from exc


def crear_llm_estructurado(config: Configuracion):
    """Devuelve el LLM listo para devolver `RespuestaLlmAnalisis` (con la salida cruda)."""
    try:
        return _crear_llm_estructurado(config, RespuestaLlmAnalisis)
    except ErrorLlm as exc:
        raise ErrorAnalisis(str(exc)) from exc


# --- Prompt y caché -----------------------------------------------------------

def cargar_prompt(ruta: str | Path = RUTA_PROMPT_ANALISIS) -> str:
    """Lee el prompt de análisis desde `prompts/analisis.md`."""
    try:
        return leer_prompt(ruta)
    except ErrorLlm as exc:
        raise ErrorAnalisis(
            f"No se pudo leer el prompt de análisis: {Path(ruta).name}"
        ) from exc


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
        AIMessage(texto_salida(salida)),
        HumanMessage(
            "Tu respuesta anterior no cumple el esquema solicitado: "
            f"{error}. Devuelve de nuevo SOLO el objeto JSON corregido, con un índice "
            "por cada interacción del lote, sin repetir ni omitir ninguno."
        ),
    ]


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


# --- Orquestación -------------------------------------------------------------

def _obtener_respuesta(
    llm: Any,
    prompt: str,
    lote: LoteEntrada,
    dormir: Dormir,
) -> RespuestaLlmAnalisis:
    """Llama al LLM respetando el tope de llamadas, los reintentos 429 y una reparación."""
    return obtener_respuesta_estructurada(
        llm,
        _construir_mensajes(prompt, lote),
        tipo=RespuestaLlmAnalisis,
        validar=lambda parsed: _validar_cobertura(parsed, lote),
        reparar=lambda error, salida: _mensajes_reparacion(prompt, lote, error, salida),
        error_cls=ErrorAnalisis,
        dormir=dormir,
    )


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

    respuesta = leer_cache(directorio, clave, RespuestaLlmAnalisis)
    if respuesta is not None:
        return _construir_informe(lote, config, respuesta, version, desde_cache=True)

    if llm is None:
        llm = crear_llm_estructurado(config)

    respuesta = _obtener_respuesta(llm, prompt, lote, dormir or time.sleep)
    escribir_cache(directorio, clave, config, version, respuesta)

    return _construir_informe(lote, config, respuesta, version, desde_cache=False)
