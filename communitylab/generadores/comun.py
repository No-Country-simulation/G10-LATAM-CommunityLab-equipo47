"""Piezas comunes de los generadores de activos por canal.

Aquí vive lo compartido por LinkedIn y FAQ: la validación de cifras, el armado de la
entrada y de la clave de caché, los mensajes (con el esquema inyectado) y la llamada al
LLM reutilizando `llm.py`. Cada generador concreto aporta su esquema y sus validaciones.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Callable

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from ..config import DIRECTORIO_CACHE_LLM, Configuracion
from ..llm import (
    Dormir,
    crear_llm_estructurado,
    escribir_cache,
    leer_cache,
    leer_prompt,
    obtener_respuesta_estructurada,
    texto_salida,
    version_prompt,
)
from ..modelos import InformeAnalisis, InteraccionAnalizada


class ErrorGeneracion(Exception):
    """Error claro al generar un activo por canal."""


# --- Cifras -------------------------------------------------------------------

# Números que no forman parte de un hashtag, mención ni palabra pegada.
_PATRON_CIFRA = re.compile(r"(?<![\w#@/])(\d+(?:[.,]\d+)?)")
# Marcador de lista al inicio de línea (p. ej. "1. " o "2) "): no es un dato.
_PATRON_MARCADOR_LISTA = re.compile(r"(?m)^\s*\d+[.)]\s")


def extraer_cifras(texto: str) -> set[str]:
    """Devuelve las cifras sueltas de un texto (sin contar los marcadores de lista).

    Solo se descartan los marcadores al inicio de línea; una cifra dentro de una frase
    (por ejemplo «un 40 %», «paso 3» o «3 días») sigue contando.
    """
    return set(_PATRON_CIFRA.findall(_PATRON_MARCADOR_LISTA.sub("", texto)))


def validar_cifras(texto_activo: str, texto_origen: str) -> Exception | None:
    """Comprueba que toda cifra del activo aparezca como cifra en el texto de origen.

    Se comparan conjuntos de cifras (no subcadenas), para que un «3» no pase por aparecer
    dentro de «2026» o «13».
    """
    cifras_origen = extraer_cifras(texto_origen)
    faltan = sorted(cifra for cifra in extraer_cifras(texto_activo) if cifra not in cifras_origen)
    if faltan:
        return ValueError(
            "el activo incluye cifras que no están en la interacción de origen: "
            + ", ".join(faltan)
        )
    return None


# --- Entrada, esquema y caché -------------------------------------------------

def inyectar_esquema(prompt: str, esquema: type[BaseModel]) -> str:
    """Sustituye `{{ESQUEMA}}` por el JSON Schema del modelo (fuente única: `modelos.py`)."""
    esquema_json = json.dumps(esquema.model_json_schema(), ensure_ascii=False, indent=2)
    if "{{ESQUEMA}}" in prompt:
        return prompt.replace("{{ESQUEMA}}", esquema_json)
    return prompt + "\n\n## Esquema de salida (JSON)\n\n" + esquema_json


def construir_entrada_generador(
    interaccion: InteraccionAnalizada,
    informe: InformeAnalisis,
) -> dict[str, Any]:
    """Arma lo único que entra al prompt (y sirve para la clave de caché)."""
    return {
        "interaccion": {
            "autor": interaccion.autor,
            "canal": interaccion.canal,
            "tipo": interaccion.tipo,
            "texto": interaccion.texto,
            "sentimiento": interaccion.sentimiento.value,
            "temas": interaccion.temas,
            "puntuacion_relevancia": interaccion.puntuacion.puntuacion_final,
            "motivo_puntuacion": interaccion.motivo_puntuacion,
        },
        "informe": {
            "origen_comunidad": informe.origen_comunidad,
            "periodo_referencia": informe.periodo_referencia,
            "sentimiento_predominante": informe.sentimiento_predominante.value,
            "temas_principales": informe.temas_principales,
        },
    }


def hash_esquema(esquema: type[BaseModel]) -> str:
    """Hash del esquema de salida (cambia si cambia `modelos.py` → invalida la caché)."""
    serializado = json.dumps(esquema.model_json_schema(), ensure_ascii=False, sort_keys=True)
    return version_prompt(serializado)


def clave_cache_activo(tipo_activo: str, version: str, hash_esquema_salida: str, entrada: dict) -> str:
    """Clave de caché: tipo de activo + versión del prompt + hash del esquema + hash de la entrada."""
    entrada_json = json.dumps(entrada, ensure_ascii=False, sort_keys=True)
    base = f"{tipo_activo}|{version}|{hash_esquema_salida}|{entrada_json}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


# --- Mensajes -----------------------------------------------------------------

def construir_mensajes(prompt: str, esquema: type[BaseModel], entrada: dict) -> list[Any]:
    sistema = inyectar_esquema(prompt, esquema)
    usuario = json.dumps(entrada, ensure_ascii=False, indent=2)
    return [SystemMessage(sistema), HumanMessage(usuario)]


def mensajes_reparacion(
    prompt: str,
    esquema: type[BaseModel],
    entrada: dict,
    error: Exception,
    salida: Any,
) -> list[Any]:
    sistema = inyectar_esquema(prompt, esquema)
    usuario = json.dumps(entrada, ensure_ascii=False, indent=2)
    return [
        SystemMessage(sistema),
        HumanMessage(usuario),
        AIMessage(texto_salida(salida)),
        HumanMessage(
            "Tu respuesta anterior no cumple el esquema o las restricciones: "
            f"{error}. Devuelve de nuevo SOLO el objeto JSON corregido, basándote "
            "únicamente en la interacción recibida."
        ),
    ]


# --- Orquestación -------------------------------------------------------------

def generar_activo(
    *,
    tipo_activo: str,
    esquema_llm: type[BaseModel],
    esquema_final: type[BaseModel],
    ruta_prompt: str,
    interaccion: InteraccionAnalizada,
    informe: InformeAnalisis,
    config: Configuracion,
    validar: Callable[[BaseModel | None, Any], Exception | None],
    armar: Callable[[BaseModel], BaseModel],
    error_cls: type[Exception] = ErrorGeneracion,
    llm: Any | None = None,
    directorio_cache: str | Path | None = None,
    dormir: Dormir | None = None,
) -> BaseModel:
    """Genera un activo: caché → llamada al LLM (con reintentos) → validación → armado final."""
    prompt = leer_prompt(ruta_prompt)
    version = version_prompt(prompt)
    entrada = construir_entrada_generador(interaccion, informe)
    clave = clave_cache_activo(tipo_activo, version, hash_esquema(esquema_final), entrada)
    directorio = Path(directorio_cache) if directorio_cache is not None else Path(DIRECTORIO_CACHE_LLM)

    respuesta = leer_cache(directorio, clave, esquema_llm)
    if respuesta is not None:
        return armar(respuesta)

    if llm is None:
        llm = crear_llm_estructurado(config, esquema_llm)

    respuesta = obtener_respuesta_estructurada(
        llm,
        construir_mensajes(prompt, esquema_llm, entrada),
        tipo=esquema_llm,
        validar=validar,
        reparar=lambda error, salida: mensajes_reparacion(prompt, esquema_llm, entrada, error, salida),
        error_cls=error_cls,
        dormir=dormir or time.sleep,
    )
    escribir_cache(directorio, clave, config, version, respuesta)
    return armar(respuesta)
