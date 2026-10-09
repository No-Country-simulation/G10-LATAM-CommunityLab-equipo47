"""Generadores de activos por canal (Fase 4)."""

from .comun import ErrorGeneracion
from .faq import generar_faq
from .linkedin import generar_post_linkedin
from .seleccion import elegir_para_faq, elegir_para_linkedin

__all__ = [
    "ErrorGeneracion",
    "elegir_para_faq",
    "elegir_para_linkedin",
    "generar_faq",
    "generar_post_linkedin",
]
