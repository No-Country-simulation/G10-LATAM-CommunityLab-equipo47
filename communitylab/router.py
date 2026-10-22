"""Router de interacciones a rutas de activos (reglas simples y explicables)."""

from __future__ import annotations

from .config import (
    SENTIMIENTOS_LINKEDIN_OTROS,
    SENTIMIENTOS_LINKEDIN_TESTIMONIO,
    TIPOS_APOYO,
    TIPOS_FAQ,
    TIPOS_LINKEDIN,
)
from .modelos import InteraccionAnalizada, Ruta


def asignar_ruta(interaccion: InteraccionAnalizada) -> Ruta:
    """Asigna una ruta a la interacción.

    Orden de prioridad:
    1. `apoyo` (alerta_apoyo/dificultades) siempre gana.
    2. `testimonio`/`logro` van a LinkedIn con sentimiento positivo o muy positivo.
    3. `pregunta_tecnica`/`duda` van a FAQ.
    4. El resto solo va a LinkedIn con sentimiento muy positivo; si no, `sin_activo`.
    """
    tipo = interaccion.tipo
    sentimiento = interaccion.sentimiento.value

    if tipo in TIPOS_APOYO:
        return Ruta.APOYO

    if tipo in TIPOS_LINKEDIN:
        if sentimiento in SENTIMIENTOS_LINKEDIN_TESTIMONIO:
            return Ruta.POST_LINKEDIN
        return Ruta.SIN_ACTIVO

    if tipo in TIPOS_FAQ:
        return Ruta.FAQ

    if sentimiento in SENTIMIENTOS_LINKEDIN_OTROS:
        return Ruta.POST_LINKEDIN

    return Ruta.SIN_ACTIVO
