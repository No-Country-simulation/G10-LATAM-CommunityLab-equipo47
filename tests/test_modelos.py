"""Pruebas de los modelos de datos y del esquema del paquete de distribución."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from communitylab.modelos import EstadoAprobacion, PaqueteDistribucion

RAIZ = Path(__file__).resolve().parents[1]
EJEMPLO_PAQUETE = RAIZ / "docs" / "ejemplo-paquete-distribucion.json"


def _ejemplo() -> dict:
    return json.loads(EJEMPLO_PAQUETE.read_text(encoding="utf-8"))


def test_valida_el_ejemplo_del_paquete():
    paquete = PaqueteDistribucion.model_validate(_ejemplo())

    assert paquete.status == "exito"
    assert len(paquete.analisis_interacciones) == 3
    assert paquete.resumen_comunidad.total_interacciones_procesadas == 3
    assert paquete.almacenamiento_oci.ruta_objeto == "activos/2026-semana-04/paquete-distribucion.json"
    assert paquete.almacenamiento_oci.status == "guardado_con_exito"


def test_estado_aprobacion_por_defecto_es_pendiente():
    datos = _ejemplo()
    del datos["activos_distribucion_generados"]["post_linkedin"]["estado_aprobacion"]

    paquete = PaqueteDistribucion.model_validate(datos)

    assert paquete.activos_distribucion_generados.post_linkedin.estado_aprobacion is EstadoAprobacion.PENDIENTE


def test_puntuacion_fuera_de_rango_falla():
    datos = _ejemplo()
    datos["analisis_interacciones"][0]["puntuacion_relevancia"] = 150

    with pytest.raises(ValidationError):
        PaqueteDistribucion.model_validate(datos)


def test_sentimiento_invalido_falla():
    datos = _ejemplo()
    datos["analisis_interacciones"][0]["sentimiento"] = "rarisimo"

    with pytest.raises(ValidationError):
        PaqueteDistribucion.model_validate(datos)


def test_ruta_invalida_falla():
    datos = _ejemplo()
    datos["analisis_interacciones"][0]["ruta"] = "otra_ruta"

    with pytest.raises(ValidationError):
        PaqueteDistribucion.model_validate(datos)


def test_status_error_exige_mensaje():
    datos = _ejemplo()
    datos["status"] = "error"
    datos["mensaje_error"] = None

    with pytest.raises(ValidationError):
        PaqueteDistribucion.model_validate(datos)
