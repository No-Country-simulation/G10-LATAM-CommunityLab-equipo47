"""Pruebas del módulo de OCI Object Storage (sin tocar la red)."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import oci
import pytest

from communitylab.almacenamiento_oci import (
    ErrorAlmacenamiento,
    construir_nombre_objeto,
    listar_objetos,
    resolver_semana,
    subir_objeto,
)
from communitylab.config import Configuracion

CONFIG = Configuracion(oci_namespace="namespace-test", oci_bucket="bucket-test")


def _cliente_con_objeto(existe: bool) -> MagicMock:
    cliente = MagicMock()
    if existe:
        cliente.head_object.return_value = MagicMock()
    else:
        cliente.head_object.side_effect = oci.exceptions.ServiceError(
            status=404, code="NotFound", headers={}, message="No encontrado"
        )
    return cliente


def test_construye_nombre_de_objeto():
    nombre = construir_nombre_objeto("entradas", 2026, 4, "ejemplo_1_contratacion.json")

    assert nombre == "entradas/2026-semana-04/ejemplo_1_contratacion.json"


def test_nombre_usa_solo_el_archivo_sin_rutas():
    nombre = construir_nombre_objeto("activos", 2026, 4, "data/salida/paquete.json")

    assert nombre == "activos/2026-semana-04/paquete.json"


def test_categoria_no_permitida_falla():
    with pytest.raises(ErrorAlmacenamiento):
        construir_nombre_objeto("otros", 2026, 4, "x.json")


@pytest.mark.parametrize("semana", [0, 54])
def test_semana_fuera_de_rango_falla(semana):
    with pytest.raises(ErrorAlmacenamiento):
        construir_nombre_objeto("entradas", 2026, semana, "x.json")


def test_resolver_semana_toma_el_numero_de_periodo_referencia():
    assert resolver_semana("Semana_04_Sprints", date(2026, 1, 1)) == (2026, 4)


def test_resolver_semana_sin_numero_usa_semana_iso():
    fecha = date(2026, 1, 5)

    assert resolver_semana("Sin numero de semana", fecha) == fecha.isocalendar()[:2]


def test_subir_objeto_llama_put_object():
    cliente = _cliente_con_objeto(existe=False)
    nombre = "entradas/2026-semana-04/lote.json"

    resultado = subir_objeto(cliente, CONFIG, nombre, {"clave": "valor"})

    assert resultado == nombre
    a_args = cliente.put_object.call_args.args
    assert a_args[0] == "namespace-test"
    assert a_args[1] == "bucket-test"
    assert a_args[2] == nombre


def test_subir_objeto_no_sobrescribe_por_defecto():
    cliente = _cliente_con_objeto(existe=True)

    with pytest.raises(ErrorAlmacenamiento):
        subir_objeto(cliente, CONFIG, "entradas/2026-semana-04/lote.json", {"clave": "valor"})

    cliente.put_object.assert_not_called()


def test_subir_objeto_sobrescribe_si_se_pide():
    cliente = _cliente_con_objeto(existe=True)

    subir_objeto(cliente, CONFIG, "entradas/2026-semana-04/lote.json", {"clave": "valor"}, sobrescribir=True)

    cliente.put_object.assert_called_once()


def test_listar_objetos_recorre_las_paginas():
    pagina_1 = MagicMock()
    pagina_1.data.objects = [SimpleNamespace(name="a.json")]
    pagina_1.data.next_start_with = "b.json"
    pagina_2 = MagicMock()
    pagina_2.data.objects = [SimpleNamespace(name="b.json")]
    pagina_2.data.next_start_with = None
    cliente = MagicMock()
    cliente.list_objects.side_effect = [pagina_1, pagina_2]

    resultado = listar_objetos(cliente, CONFIG, prefijo="entradas/")

    assert resultado == ["a.json", "b.json"]
    assert cliente.list_objects.call_count == 2


def test_listar_objetos_propaga_error_de_servicio():
    cliente = MagicMock()
    cliente.list_objects.side_effect = oci.exceptions.ServiceError(
        status=404, code="BucketNotFound", headers={}, message="Sin bucket"
    )

    with pytest.raises(ErrorAlmacenamiento):
        listar_objetos(cliente, CONFIG)
