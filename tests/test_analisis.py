"""Pruebas del módulo de análisis con el LLM simulado (sin red)."""

import pytest
from langchain_google_genai.chat_models import GoogleRateLimitError

from communitylab.analisis import (
    ErrorAnalisis,
    analizar_lote,
    clave_cache,
    crear_llm,
    usa_muestreo_fijo,
    version_prompt,
)
from communitylab.config import Configuracion, MAX_LLAMADAS_POR_OPERACION
from communitylab.modelos import LoteEntrada, RespuestaLlmAnalisis


def _config(modelo="gemini-3.5-flash-lite") -> Configuracion:
    return Configuracion(
        gemini_api_key="clave-falsa",
        oci_namespace="namespace-test",
        oci_bucket="bucket-test",
        gemini_model=modelo,
    )


def _lote(n=3) -> LoteEntrada:
    return LoteEntrada.model_validate({
        "origen_comunidad": "Comunidad_Test",
        "periodo_referencia": "Semana_04_Sprints",
        "interacciones": [
            {
                "autor": f"Persona {i}",
                "canal": "#general",
                "tipo": "testimonio",
                "texto": f"Texto {i}",
            }
            for i in range(n)
        ],
    })


def _subpuntuaciones():
    return {
        "relevancia_comunidad": 80,
        "impacto_publicable": 70,
        "claridad": 60,
        "novedad": 50,
    }


def _respuesta(n, valida=True):
    if valida:
        interacciones = [
            {
                "indice": i,
                "sentimiento": "positivo",
                "temas": [f"tema {i}"],
                "subpuntuaciones": _subpuntuaciones(),
                "motivo": f"motivo {i}",
            }
            for i in range(n)
        ]
    else:
        # Solo cubre el índice 0: la cobertura queda incompleta.
        interacciones = [{
            "indice": 0,
            "sentimiento": "positivo",
            "temas": ["tema"],
            "subpuntuaciones": _subpuntuaciones(),
            "motivo": "motivo",
        }]
    return {
        "resumen": {"sentimiento_predominante": "positivo", "temas_principales": ["tema"]},
        "interacciones": interacciones,
    }


def _ok(n):
    return {
        "raw": None,
        "parsed": RespuestaLlmAnalisis.model_validate(_respuesta(n)),
        "parsing_error": None,
    }


def _parsing_error(n):
    return {"raw": None, "parsed": None, "parsing_error": ValueError("falta el campo resumen")}


class FakeLlm:
    """LLM simulado: devuelve respuestas prefijadas y cuenta las llamadas."""

    def __init__(self, resultados):
        self._resultados = list(resultados)
        self.llamadas = 0

    def invoke(self, mensajes):  # noqa: ARG002
        self.llamadas += 1
        if not self._resultados:
            raise AssertionError("el LLM no debería haberse llamado")
        resultado = self._resultados.pop(0)
        if isinstance(resultado, Exception):
            raise resultado
        return resultado


def test_analiza_y_usa_cache_en_la_segunda_ejecucion(tmp_path):
    n = 3
    llm = FakeLlm([_ok(n)])

    informe = analizar_lote(_lote(n), _config(), llm=llm, directorio_cache=tmp_path, dormir=lambda s: None)

    assert llm.llamadas == 1
    assert informe.metadatos.desde_cache is False
    assert informe.total_interacciones_procesadas == n
    assert informe.interacciones[0].puntuacion.puntuacion_final == 70  # 80*.4+70*.3+60*.2+50*.1
    assert informe.metadatos.modelo == "gemini-3.5-flash-lite"

    llm_prohibido = FakeLlm([])
    informe_cache = analizar_lote(
        _lote(n), _config(), llm=llm_prohibido, directorio_cache=tmp_path, dormir=lambda s: None
    )

    assert llm_prohibido.llamadas == 0
    assert informe_cache.metadatos.desde_cache is True
    assert informe_cache.interacciones[0].motivo_puntuacion == "motivo 0"


def test_clave_cache_cambia_con_modelo_prompt_y_entrada():
    lote = _lote(2)

    base = clave_cache("gemini-3.5-flash-lite", "v1", lote)

    assert base == clave_cache("gemini-3.5-flash-lite", "v1", lote)
    assert base != clave_cache("gemini-2.5-flash", "v1", lote)
    assert base != clave_cache("gemini-3.5-flash-lite", "v2", lote)
    assert base != clave_cache("gemini-3.5-flash-lite", "v1", _lote(3))


def test_reparacion_valida_con_un_reintento(tmp_path):
    llm = FakeLlm([_parsing_error(2), _ok(2)])

    informe = analizar_lote(_lote(2), _config(), llm=llm, directorio_cache=tmp_path, dormir=lambda s: None)

    assert llm.llamadas == 2
    assert len(informe.interacciones) == 2


def test_cobertura_incompleta_agota_reparacion(tmp_path):
    # Respuestas válidas en formato pero que solo cubren el índice 0 de un lote de 2.
    solo_indice_cero = RespuestaLlmAnalisis.model_validate(_respuesta(1))
    llm = FakeLlm([
        {"raw": None, "parsed": solo_indice_cero, "parsing_error": None},
        {"raw": None, "parsed": solo_indice_cero, "parsing_error": None},
    ])

    with pytest.raises(ErrorAnalisis):
        analizar_lote(_lote(2), _config(), llm=llm, directorio_cache=tmp_path, dormir=lambda s: None)

    assert llm.llamadas == 2


def test_429_reintenta_y_luego_exito(tmp_path):
    esperas = []
    llm = FakeLlm([
        GoogleRateLimitError(
            "429 RESOURCE_EXHAUSTED. {'error': {'details': "
            "[{'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '3s'}]}}"
        ),
        _ok(2),
    ])

    informe = analizar_lote(_lote(2), _config(), llm=llm, directorio_cache=tmp_path, dormir=esperas.append)

    assert llm.llamadas == 2
    assert esperas  # hubo espera antes de reintentar
    assert len(informe.interacciones) == 2


def test_429_agotado_respeta_el_tope(tmp_path):
    llm = FakeLlm([GoogleRateLimitError("429") for _ in range(6)])

    with pytest.raises(ErrorAnalisis):
        analizar_lote(_lote(2), _config(), llm=llm, directorio_cache=tmp_path, dormir=lambda s: None)

    assert llm.llamadas <= MAX_LLAMADAS_POR_OPERACION


def test_no_pasa_temperature_a_los_modelos_de_muestreo_fijo():
    assert usa_muestreo_fijo("gemini-3.5-flash-lite") is True
    assert usa_muestreo_fijo("gemini-3.6-flash") is True
    assert usa_muestreo_fijo("gemini-2.5-flash") is False

    assert crear_llm(_config("gemini-3.5-flash-lite")).temperature is None
    assert crear_llm(_config("gemini-2.5-flash")).temperature == 0


def test_version_prompt_es_estable_y_sensible():
    assert version_prompt("hola") == version_prompt("hola")
    assert version_prompt("hola") != version_prompt("hola!")
