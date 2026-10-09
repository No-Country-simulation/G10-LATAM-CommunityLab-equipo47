"""Generador del post de LinkedIn (caso de éxito del MVP)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..config import (
    HASHTAGS_MAX_LINKEDIN,
    HASHTAGS_MIN_LINKEDIN,
    LONGITUD_MAX_COPY_LINKEDIN,
    LONGITUD_MIN_COPY_LINKEDIN,
    RUTA_PROMPT_LINKEDIN,
    Configuracion,
)
from ..llm import Dormir, finish_reason
from ..modelos import (
    EstadoAprobacion,
    InformeAnalisis,
    InteraccionAnalizada,
    PostLinkedIn,
    PostLinkedInLlm,
)
from .comun import ErrorGeneracion, generar_activo, validar_cifras


def generar_post_linkedin(
    interaccion: InteraccionAnalizada | None,
    informe: InformeAnalisis,
    config: Configuracion,
    *,
    llm: Any | None = None,
    directorio_cache: str | Path | None = None,
    dormir: Dormir | None = None,
) -> PostLinkedIn:
    """Genera un post de LinkedIn a partir de la interacción elegida."""
    if interaccion is None:
        raise ErrorGeneracion(
            "Este lote no produce un post de LinkedIn: ninguna interacción cumple el "
            "criterio (testimonio o sentimiento muy positivo)."
        )

    return generar_activo(  # type: ignore[return-value]
        tipo_activo="post_linkedin",
        esquema_llm=PostLinkedInLlm,
        esquema_final=PostLinkedIn,
        ruta_prompt=RUTA_PROMPT_LINKEDIN,
        interaccion=interaccion,
        informe=informe,
        config=config,
        validar=lambda parsed, salida: _validar_post(parsed, salida, interaccion),
        armar=_armar_post,
        llm=llm,
        directorio_cache=directorio_cache,
        dormir=dormir,
    )


def _validar_post(
    parsed: PostLinkedInLlm | None,
    salida: Any,
    interaccion: InteraccionAnalizada,
) -> Exception | None:
    if parsed is None:
        return ValueError("no hay post que revisar")
    if finish_reason(salida) == "MAX_TOKENS":
        return ValueError("la respuesta del modelo se truncó (finish_reason=MAX_TOKENS)")

    copy = parsed.copy
    if len(copy) < LONGITUD_MIN_COPY_LINKEDIN:
        return ValueError(
            f"el copy es demasiado corto ({len(copy)} caracteres; mínimo {LONGITUD_MIN_COPY_LINKEDIN})"
        )
    if len(copy) > LONGITUD_MAX_COPY_LINKEDIN:
        return ValueError(
            f"el copy es demasiado largo ({len(copy)} caracteres; máximo {LONGITUD_MAX_COPY_LINKEDIN})"
        )

    error = _validar_hashtags(copy)
    if error is not None:
        return error

    return validar_cifras(f"{parsed.titulo}\n{copy}", interaccion.texto)


def _validar_hashtags(copy: str) -> Exception | None:
    hashtags = re.findall(r"#[^\s#]+", copy)
    if len(hashtags) < HASHTAGS_MIN_LINKEDIN:
        return ValueError(
            f"faltan hashtags: hay {len(hashtags)} y el mínimo es {HASHTAGS_MIN_LINKEDIN}"
        )
    if len(hashtags) > HASHTAGS_MAX_LINKEDIN:
        return ValueError(
            f"hay demasiados hashtags: {len(hashtags)} y el máximo es {HASHTAGS_MAX_LINKEDIN}"
        )
    mal_formados = [hashtag for hashtag in hashtags if not re.fullmatch(r"#\w+", hashtag, re.UNICODE)]
    if mal_formados:
        return ValueError(f"hashtags mal formados: {mal_formados}")

    recortado = copy.rstrip()
    if recortado.endswith("#") or not re.search(r"#[^\s#]+$", recortado):
        return ValueError("los hashtags deben ir al final del copy y estar completos")
    return None


def _armar_post(parsed: PostLinkedInLlm) -> PostLinkedIn:
    return PostLinkedIn(**parsed.model_dump(), estado_aprobacion=EstadoAprobacion.PENDIENTE)
