"""Selectores de la interacción por activo.

**TEMPORALES** hasta el router de la Fase 5. No hacen llamadas nuevas al LLM: reordenan
las sub-puntuaciones ya calculadas. Si ninguna interacción cumple el filtro, devuelven
`None` (y el generador informa de que ese lote no produce ese activo).
"""

from __future__ import annotations

from ..config import PESOS_SELECCION_FAQ, SENTIMIENTOS_LINKEDIN, TIPOS_FAQ, TIPOS_LINKEDIN
from ..modelos import InformeAnalisis, InteraccionAnalizada


def elegir_para_linkedin(informe: InformeAnalisis) -> InteraccionAnalizada | None:
    """Elige el mejor candidato para un post de LinkedIn: testimonio o muy positivo."""
    candidatas = [
        interaccion
        for interaccion in informe.interacciones
        if interaccion.tipo in TIPOS_LINKEDIN
        or interaccion.sentimiento.value in SENTIMIENTOS_LINKEDIN
    ]
    if not candidatas:
        return None
    return max(candidatas, key=lambda interaccion: interaccion.puntuacion.puntuacion_final)


def elegir_para_faq(informe: InformeAnalisis) -> InteraccionAnalizada | None:
    """Elige la mejor duda técnica, con pesos propios para no dejarla fuera por la rúbrica emocional."""
    candidatas = [
        interaccion for interaccion in informe.interacciones if interaccion.tipo in TIPOS_FAQ
    ]
    if not candidatas:
        return None
    return max(candidatas, key=_puntuacion_faq)


def _puntuacion_faq(interaccion: InteraccionAnalizada) -> float:
    subpuntuaciones = interaccion.puntuacion.subpuntuaciones
    return sum(
        subpuntuaciones.get(nombre, 0) * peso for nombre, peso in PESOS_SELECCION_FAQ.items()
    )
