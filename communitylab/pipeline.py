"""Pipeline de funciones simples: ingesta → análisis → router → generación → paquete.

No usa LangGraph. Reutiliza `analisis.py`, la puntuación y los generadores tal como están.
"""

from __future__ import annotations

from pathlib import Path

from .almacenamiento_oci import construir_nombre_objeto, resolver_semana
from .analisis import analizar_lote
from .config import PESOS_SELECCION_FAQ, SENTIMIENTO_ETIQUETAS, Configuracion
from .generadores import generar_faq, generar_post_linkedin
from .modelos import (
    InteraccionAnalizada,
    LoteEntrada,
    PaqueteDistribucion,
    Ruta,
)
from .router import asignar_ruta


def _mejor_por_ruta(
    informe,
    rutas: list[Ruta],
    ruta: Ruta,
    clave,
) -> InteraccionAnalizada | None:
    candidatos = [
        interaccion
        for interaccion, ruta_asignada in zip(informe.interacciones, rutas)
        if ruta_asignada == ruta
    ]
    if not candidatos:
        return None
    return max(candidatos, key=clave)


def _puntuacion_faq(interaccion: InteraccionAnalizada) -> float:
    subpuntuaciones = interaccion.puntuacion.subpuntuaciones
    return sum(
        subpuntuaciones.get(nombre, 0) * peso for nombre, peso in PESOS_SELECCION_FAQ.items()
    )


def procesar_lote(
    datos: dict,
    config: Configuracion,
    *,
    directorio_cache: str | Path | None = None,
) -> dict:
    """Valida el lote, analiza, enruta, genera los activos disponibles y arma el paquete."""
    lote = LoteEntrada.model_validate(datos)
    informe = analizar_lote(lote, config, directorio_cache=directorio_cache)

    rutas: list[Ruta] = []
    analisis: list[dict] = []
    for interaccion in informe.interacciones:
        ruta = asignar_ruta(interaccion)
        rutas.append(ruta)
        analisis.append(
            {
                "autor": interaccion.autor,
                "canal": interaccion.canal,
                "tipo": interaccion.tipo,
                "sentimiento": interaccion.sentimiento.value,
                "temas": interaccion.temas,
                "puntuacion_relevancia": interaccion.puntuacion.puntuacion_final,
                "motivo_puntuacion": interaccion.motivo_puntuacion,
                "ruta": ruta.value,
            }
        )

    candidato_linkedin = _mejor_por_ruta(
        informe,
        rutas,
        Ruta.POST_LINKEDIN,
        lambda interaccion: interaccion.puntuacion.puntuacion_final,
    )
    candidato_faq = _mejor_por_ruta(informe, rutas, Ruta.FAQ, _puntuacion_faq)

    activos: dict = {}
    if candidato_linkedin is not None:
        post = generar_post_linkedin(
            candidato_linkedin,
            informe,
            config,
            directorio_cache=directorio_cache,
        )
        activos["post_linkedin"] = post.model_dump(mode="json")

    if candidato_faq is not None:
        faq = generar_faq(
            candidato_faq,
            informe,
            config,
            directorio_cache=directorio_cache,
        )
        activos["sugerencia_contenido_faq"] = faq.model_dump(mode="json", exclude_none=True)

    anio, semana = resolver_semana(lote.periodo_referencia)
    ruta_objeto = construir_nombre_objeto(
        "activos", anio, semana, "paquete-distribucion.json"
    )

    paquete = {
        "status": "exito",
        "resumen_comunidad": {
            "origen_comunidad": lote.origen_comunidad,
            "periodo_referencia": lote.periodo_referencia,
            "total_interacciones_procesadas": informe.total_interacciones_procesadas,
            "sentimiento_predominante": SENTIMIENTO_ETIQUETAS[
                informe.sentimiento_predominante.value
            ],
            "temas_principales": informe.temas_principales,
        },
        "analisis_interacciones": analisis,
        "activos_distribucion_generados": activos,
        "almacenamiento_oci": {
            "bucket": config.oci_bucket,
            "ruta_objeto": ruta_objeto,
        },
    }

    return PaqueteDistribucion.model_validate(paquete).model_dump(
        mode="json", exclude_none=True
    )
