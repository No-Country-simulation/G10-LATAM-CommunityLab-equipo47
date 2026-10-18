"""Pruebas del pipeline real con LLM y generadores simulados (sin red)."""

from datetime import datetime

import pytest

import communitylab.pipeline as pipeline
from communitylab.analisis import ErrorAnalisis
from communitylab.config import PESOS_PUNTUACION, Configuracion
from communitylab.modelos import (
    EstadoAprobacion,
    InformeAnalisis,
    InteraccionAnalizada,
    MetadatosInforme,
    PostLinkedIn,
    PuntuacionRelevancia,
    Sentimiento,
    SugerenciaContenidoFaq,
)

CONFIG = Configuracion(
    gemini_api_key="clave-falsa",
    gemini_model="gemini-3.5-flash-lite",
    oci_region="region-test",
    oci_namespace="namespace-test",
    oci_bucket="bucket-test",
)


def _interaccion(autor, tipo, sentimiento, final=80, subs=None):
    return InteraccionAnalizada(
        autor=autor,
        canal="#general",
        tipo=tipo,
        texto="Texto",
        sentimiento=sentimiento,
        temas=["tema"],
        puntuacion=PuntuacionRelevancia(
            subpuntuaciones=subs
            or {
                "relevancia_comunidad": 80,
                "impacto_publicable": 70,
                "claridad": 60,
                "novedad": 50,
            },
            pesos=PESOS_PUNTUACION,
            puntuacion_final=final,
        ),
        motivo_puntuacion="motivo",
    )


def _informe(interacciones):
    return InformeAnalisis(
        origen_comunidad="Comunidad_Test",
        periodo_referencia="Semestre_2026_1_Semana_04",
        total_interacciones_procesadas=len(interacciones),
        sentimiento_predominante=Sentimiento.POSITIVO,
        temas_principales=["tema"],
        interacciones=interacciones,
        metadatos=MetadatosInforme(
            modelo="gemini-3.5-flash-lite", version_prompt="v", desde_cache=False
        ),
    )


def _datos():
    return {
        "origen_comunidad": "Comunidad_Test",
        "periodo_referencia": "Semestre_2026_1_Semana_04",
        "interacciones": [
            {"autor": "A", "canal": "#general", "tipo": "testimonio", "texto": "Texto A"},
            {"autor": "B", "canal": "#general", "tipo": "pregunta_tecnica", "texto": "Texto B"},
            {"autor": "C", "canal": "#general", "tipo": "alerta_apoyo", "texto": "Texto C"},
        ],
    }


def _post():
    return PostLinkedIn(
        titulo="Titulo",
        copy="Copy",
        canal_recomendado="LinkedIn",
        potencial_engagement="Alto",
    )


def _faq():
    return SugerenciaContenidoFaq(
        tema="Tema",
        origen="Origen",
        status="derivado_a_mentoria",
        pregunta="Pregunta",
        respuesta_sugerida="Respuesta",
    )


def test_pipeline_arma_paquete_completo(monkeypatch):
    interacciones = [
        _interaccion("A", "testimonio", Sentimiento.MUY_POSITIVO, 95),
        _interaccion("B", "pregunta_tecnica", Sentimiento.NEUTRO, 70),
        _interaccion("C", "alerta_apoyo", Sentimiento.NEGATIVO, 50),
    ]
    monkeypatch.setattr(pipeline, "analizar_lote", lambda *a, **k: _informe(interacciones))
    monkeypatch.setattr(pipeline, "generar_post_linkedin", lambda *a, **k: _post())
    monkeypatch.setattr(pipeline, "generar_faq", lambda *a, **k: _faq())

    paquete = pipeline.procesar_lote(_datos(), CONFIG)

    assert paquete["resumen_comunidad"]["origen_comunidad"] == "Comunidad_Test"
    assert paquete["resumen_comunidad"]["periodo_referencia"] == "Semestre_2026_1_Semana_04"
    assert paquete["resumen_comunidad"]["sentimiento_predominante"] == "Positivo"
    assert [i["ruta"] for i in paquete["analisis_interacciones"]] == [
        "post_linkedin",
        "faq",
        "apoyo",
    ]

    activos = paquete["activos_distribucion_generados"]
    assert "post_linkedin" in activos
    assert "sugerencia_contenido_faq" in activos
    assert "destaque_newsletter_semanal" not in activos
    assert activos["post_linkedin"]["estado_aprobacion"] == "pendiente"
    assert paquete["almacenamiento_oci"]["ruta_objeto"] == (
        f"activos/{datetime.now().year}-semana-04/paquete-distribucion.json"
    )


def test_pipeline_sin_candidato_faq(monkeypatch):
    interacciones = [_interaccion("A", "testimonio", Sentimiento.POSITIVO)]
    monkeypatch.setattr(pipeline, "analizar_lote", lambda *a, **k: _informe(interacciones))
    monkeypatch.setattr(pipeline, "generar_post_linkedin", lambda *a, **k: _post())

    def _no_faq(*args, **kwargs):
        raise AssertionError("no debe generarse FAQ sin candidato")

    monkeypatch.setattr(pipeline, "generar_faq", _no_faq)

    paquete = pipeline.procesar_lote(_datos(), CONFIG)

    assert "post_linkedin" in paquete["activos_distribucion_generados"]
    assert "sugerencia_contenido_faq" not in paquete["activos_distribucion_generados"]


def test_pipeline_sin_candidatos(monkeypatch):
    interacciones = [_interaccion("C", "alerta_apoyo", Sentimiento.NEGATIVO)]
    monkeypatch.setattr(pipeline, "analizar_lote", lambda *a, **k: _informe(interacciones))

    def _no_generar(*args, **kwargs):
        raise AssertionError("no debe generarse ningún activo")

    monkeypatch.setattr(pipeline, "generar_post_linkedin", _no_generar)
    monkeypatch.setattr(pipeline, "generar_faq", _no_generar)

    paquete = pipeline.procesar_lote(_datos(), CONFIG)

    assert paquete["activos_distribucion_generados"] == {}
    assert paquete["analisis_interacciones"][0]["ruta"] == "apoyo"


def test_pipeline_propaga_error_de_llm(monkeypatch):
    def _falla(*args, **kwargs):
        raise ErrorAnalisis("fallo de cuota")

    monkeypatch.setattr(pipeline, "analizar_lote", _falla)

    with pytest.raises(ErrorAnalisis, match="fallo de cuota"):
        pipeline.procesar_lote(_datos(), CONFIG)


def test_faq_final_acepta_pregunta_y_respuesta_ausentes():
    faq = SugerenciaContenidoFaq(
        tema="Tema",
        origen="Origen",
        status="derivado_a_mentoria",
    )

    assert faq.pregunta is None
    assert faq.respuesta_sugerida is None
    assert faq.estado_aprobacion is EstadoAprobacion.PENDIENTE
