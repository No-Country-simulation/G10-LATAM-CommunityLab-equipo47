"""Pruebas de utilidades de `llm.py`: parseo de `retry_delay` y `finish_reason`."""

from types import SimpleNamespace

import pytest
from google.genai.errors import ClientError
from langchain_google_genai.chat_models import GoogleRateLimitError, _handle_client_error

from communitylab.config import ESPERA_POR_DEFECTO_429_SEG
from communitylab.llm import finish_reason, retry_delay_segundos


def _exc(texto: str) -> GoogleRateLimitError:
    return GoogleRateLimitError(texto)


def test_retry_delay_formato_real_del_sdk():
    exc = _exc(
        "429 RESOURCE_EXHAUSTED. {'error': {'details': "
        "[{'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '120s'}]}}"
    )

    assert retry_delay_segundos(exc) == 120.0


def test_retry_delay_formato_json_con_comillas_dobles():
    assert retry_delay_segundos(_exc('{"retryDelay": "7.5s"}')) == 7.5


def test_retry_delay_formato_proto_de_texto():
    assert retry_delay_segundos(_exc("429 RESOURCE_EXHAUSTED retry_delay { seconds: 9 }")) == 9.0


def test_retry_delay_sin_dato_usa_el_valor_por_defecto():
    assert retry_delay_segundos(_exc("429 RESOURCE_EXHAUSTED")) == ESPERA_POR_DEFECTO_429_SEG


def test_finish_reason_desde_la_salida_cruda():
    salida = {"raw": SimpleNamespace(response_metadata={"finish_reason": "MAX_TOKENS"})}

    assert finish_reason(salida) == "MAX_TOKENS"


def test_finish_reason_ausente_devuelve_none():
    assert finish_reason({"raw": SimpleNamespace(response_metadata={})}) is None
    assert finish_reason("texto plano") is None


def test_429_real_se_convierte_y_conserva_el_retry_delay():
    client_error = ClientError(
        429,
        {
            "error": {
                "code": 429,
                "status": "RESOURCE_EXHAUSTED",
                "message": "Quota exceeded for model",
                "details": [
                    {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "120s"}
                ],
            }
        },
    )

    with pytest.raises(GoogleRateLimitError) as info:
        _handle_client_error(client_error, {"model": "gemini-3.5-flash-lite"})

    assert retry_delay_segundos(info.value) == 120.0
