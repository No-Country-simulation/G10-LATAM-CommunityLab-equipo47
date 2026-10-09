"""Generador de la sugerencia de contenido para FAQ (duda técnica del MVP)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..config import PLANTILLA_ORIGEN_FAQ, RUTA_PROMPT_FAQ, STATUS_FAQ, Configuracion
from ..llm import Dormir, finish_reason
from ..modelos import (
    EstadoAprobacion,
    InformeAnalisis,
    InteraccionAnalizada,
    SugerenciaContenidoFaq,
    SugerenciaContenidoFaqLlm,
)
from .comun import ErrorGeneracion, generar_activo, validar_cifras


def generar_faq(
    interaccion: InteraccionAnalizada | None,
    informe: InformeAnalisis,
    config: Configuracion,
    *,
    llm: Any | None = None,
    directorio_cache: str | Path | None = None,
    dormir: Dormir | None = None,
) -> SugerenciaContenidoFaq:
    """Genera una FAQ a partir de la duda elegida."""
    if interaccion is None:
        raise ErrorGeneracion(
            "Este lote no produce una FAQ: ninguna interacción es una duda técnica."
        )

    return generar_activo(  # type: ignore[return-value]
        tipo_activo="sugerencia_contenido_faq",
        esquema_llm=SugerenciaContenidoFaqLlm,
        esquema_final=SugerenciaContenidoFaq,
        ruta_prompt=RUTA_PROMPT_FAQ,
        interaccion=interaccion,
        informe=informe,
        config=config,
        validar=lambda parsed, salida: _validar_faq(parsed, salida, interaccion),
        armar=lambda parsed: _armar_faq(parsed, interaccion),
        llm=llm,
        directorio_cache=directorio_cache,
        dormir=dormir,
    )


def _validar_faq(
    parsed: SugerenciaContenidoFaqLlm | None,
    salida: Any,
    interaccion: InteraccionAnalizada,
) -> Exception | None:
    if parsed is None:
        return ValueError("no hay FAQ que revisar")
    if finish_reason(salida) == "MAX_TOKENS":
        return ValueError("la respuesta del modelo se truncó (finish_reason=MAX_TOKENS)")
    if not parsed.pregunta.strip() or not parsed.respuesta_sugerida.strip():
        return ValueError("la FAQ debe traer pregunta y respuesta sugerida")

    return validar_cifras(
        f"{parsed.tema}\n{parsed.pregunta}\n{parsed.respuesta_sugerida}",
        interaccion.texto,
    )


def _armar_faq(parsed: SugerenciaContenidoFaqLlm, interaccion: InteraccionAnalizada) -> SugerenciaContenidoFaq:
    return SugerenciaContenidoFaq(
        tema=parsed.tema,
        origen=PLANTILLA_ORIGEN_FAQ.format(autor=interaccion.autor, canal=interaccion.canal),
        status=STATUS_FAQ,
        pregunta=parsed.pregunta,
        respuesta_sugerida=parsed.respuesta_sugerida,
        estado_aprobacion=EstadoAprobacion.PENDIENTE,
    )
