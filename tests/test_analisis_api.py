"""Fija que la API pública de `analisis.py` conserve el tipo `ErrorAnalisis`.

Tras extraer la lógica común a `llm.py`, los envoltorios deben seguir lanzando
`ErrorAnalisis` (y no `ErrorLlm`) para no cambiar el comportamiento previo.
"""

from pathlib import Path

import pytest

from communitylab.analisis import (
    ErrorAnalisis,
    cargar_prompt,
    crear_llm,
    crear_llm_estructurado,
)
from communitylab.config import Configuracion
from communitylab.llm import ErrorLlm


def _config_sin_clave() -> Configuracion:
    return Configuracion(gemini_api_key="", oci_namespace="n", oci_bucket="b")


def test_error_analisis_y_error_llm_son_distintos():
    assert not issubclass(ErrorAnalisis, ErrorLlm)
    assert not issubclass(ErrorLlm, ErrorAnalisis)


def test_crear_llm_sin_clave_lanza_error_analisis():
    with pytest.raises(ErrorAnalisis):
        crear_llm(_config_sin_clave())


def test_crear_llm_estructurado_sin_clave_lanza_error_analisis():
    with pytest.raises(ErrorAnalisis):
        crear_llm_estructurado(_config_sin_clave())


def test_cargar_prompt_inexistente_lanza_error_analisis(tmp_path: Path):
    with pytest.raises(ErrorAnalisis):
        cargar_prompt(tmp_path / "no_existe.md")
