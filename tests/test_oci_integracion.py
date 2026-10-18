"""Pruebas de integración OCI con mocks (sin red)."""

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import modules.oci_client as adaptador
from communitylab.almacenamiento_oci import (
    ErrorAlmacenamiento,
    ObjetoYaExiste,
    construir_nombre_objeto,
    crear_cliente,
    perfil_default_disponible,
    resolver_semana,
    subir_objeto,
)
from communitylab.config import Configuracion

FECHA = date(2026, 10, 18)  # semana ISO 42
RUTA = "activos/2026-semana-04/paquete-distribucion.json"


def _config(**cambios) -> Configuracion:
    base = {
        "oci_region": "region-test",
        "oci_namespace": "namespace-test",
        "oci_bucket": "bucket-test",
    }
    base.update(cambios)
    return Configuracion(**base)


def _paquete(periodo="Semestre_2026_1_Semana_04") -> dict:
    return {
        "resumen_comunidad": {"periodo_referencia": periodo},
        "activos_distribucion_generados": {},
        "almacenamiento_oci": {},
    }


# --- Ruta por semana ----------------------------------------------------------

@pytest.mark.parametrize(
    "periodo, semana",
    [
        ("Semestre_2026_1_Semana_04", 4),
        ("Semestre_2026_1_Semana_05", 5),
        ("Semestre_2026_1_Semana_06", 6),
        ("Semestre_2026_1_Feria_Proyectos", 42),
        ("Ciclo_2026_Sprint_Final", 42),
        ("Mes_Marzo_2026", 42),
        ("Ciclo_2026_Entregas_Finales", 42),
        ("Semana_04", 4),
    ],
)
def test_ruta_por_semana_con_los_ocho_periodos(periodo, semana):
    anio, obtenida = resolver_semana(periodo, FECHA)

    assert anio == 2026
    assert obtenida == semana
    assert construir_nombre_objeto(
        "activos", anio, obtenida, "paquete-distribucion.json"
    ) == f"activos/2026-semana-{semana:02d}/paquete-distribucion.json"


def test_ruta_sugerida_para_paquete():
    assert adaptador.ruta_sugerida_para_paquete(_paquete()) == RUTA


# --- Credenciales -------------------------------------------------------------

def test_credenciales_explicitas_completas():
    completa = _config(
        oci_user="u",
        oci_fingerprint="f",
        oci_tenancy="t",
        oci_key_content="k",
    )
    incompleta = _config(oci_user="u", oci_fingerprint="f")

    assert completa.credenciales_explicitas_completas is True
    assert incompleta.credenciales_explicitas_completas is False


def test_perfil_default_disponible_sin_archivo(tmp_path):
    assert perfil_default_disponible(_config(oci_config_file=str(tmp_path / "no_existe"))) is False


def test_perfil_default_disponible_con_seccion_default(tmp_path):
    ruta = tmp_path / "config"
    ruta.write_text(
        "[DEFAULT]\nuser = u\nfingerprint = f\ntenancy = t\nkey_file = clave.pem\n",
        encoding="utf-8",
    )

    assert perfil_default_disponible(_config(oci_config_file=str(ruta))) is True


def test_perfil_default_disponible_sin_el_perfil(tmp_path):
    ruta = tmp_path / "config"
    ruta.write_text("[otro]\nuser = u\n", encoding="utf-8")

    assert perfil_default_disponible(_config(oci_config_file=str(ruta))) is False


def test_crear_cliente_con_credenciales_explicitas():
    config = _config(
        oci_user="u",
        oci_fingerprint="f",
        oci_tenancy="t",
        oci_key_content="-----BEGIN PRIVATE KEY-----\nREEMPLAZAR\n-----END PRIVATE KEY-----",
    )

    with (
        patch("communitylab.almacenamiento_oci.oci.config.validate_config") as validar,
        patch("communitylab.almacenamiento_oci.oci.object_storage.ObjectStorageClient") as cliente,
    ):
        crear_cliente(config)

    validar.assert_called_once()
    datos = cliente.call_args.args[0]
    assert datos["user"] == "u"
    assert datos["key_content"] == config.oci_key_content
    assert "key_file" not in datos


def test_crear_cliente_con_perfil_default():
    config = _config(oci_config_file="C:/fake/config", oci_config_profile="DEFAULT")

    with (
        patch(
            "communitylab.almacenamiento_oci.oci.config.from_file",
            return_value={"user": "u"},
        ) as from_file,
        patch("communitylab.almacenamiento_oci.oci.object_storage.ObjectStorageClient") as cliente,
    ):
        crear_cliente(config)

    from_file.assert_called_once()
    datos = cliente.call_args.args[0]
    assert datos["region"] == "region-test"


# --- Subida -------------------------------------------------------------------

def test_subir_objeto_ya_existe_no_llama_put():
    cliente = MagicMock()
    cliente.head_object.return_value = MagicMock()

    with pytest.raises(ObjetoYaExiste):
        subir_objeto(cliente, _config(), RUTA, {"a": 1})

    cliente.put_object.assert_not_called()


def test_subir_objeto_sobrescribe_si_se_pide():
    cliente = MagicMock()
    cliente.head_object.return_value = MagicMock()

    subir_objeto(cliente, _config(), RUTA, {"a": 1}, sobrescribir=True)

    cliente.put_object.assert_called_once()


# --- Adaptador ----------------------------------------------------------------

def test_guardar_en_oci_error_de_nube_no_cae_a_local(tmp_path):
    config = _config(
        oci_user="u",
        oci_fingerprint="f",
        oci_tenancy="t",
        oci_key_content="k",
    )

    with (
        patch.object(adaptador, "_configuracion_oci", return_value=config),
        patch.object(adaptador, "hay_credenciales", return_value=True),
        patch.object(adaptador, "crear_cliente", return_value=MagicMock()),
        patch.object(
            adaptador,
            "subir_objeto",
            side_effect=ErrorAlmacenamiento("fallo de red"),
        ),
        patch.object(adaptador, "DIRECTORIO_OFFLINE", tmp_path),
    ):
        resultado = adaptador.guardar_en_oci(_paquete(), ruta_objeto=RUTA)

    assert resultado["status"] == "error_al_guardar"
    assert resultado["nube_real"] is False
    assert "fallo de red" in resultado["error_nube"]
    assert list(tmp_path.rglob("*.json")) == []


def test_guardar_en_oci_offline(tmp_path):
    with (
        patch.object(adaptador, "_configuracion_oci", return_value=_config()),
        patch.object(adaptador, "hay_credenciales", return_value=False),
        patch.object(adaptador, "DIRECTORIO_OFFLINE", tmp_path),
    ):
        resultado = adaptador.guardar_en_oci(_paquete(), ruta_objeto=RUTA)

    assert resultado["status"] == "guardado_local"
    assert resultado["nube_real"] is False
    assert resultado["aviso"]
    assert (tmp_path / "bucket-test" / RUTA).is_file()


def test_guardar_en_oci_ya_existe():
    config = _config(
        oci_user="u",
        oci_fingerprint="f",
        oci_tenancy="t",
        oci_key_content="k",
    )

    with (
        patch.object(adaptador, "_configuracion_oci", return_value=config),
        patch.object(adaptador, "hay_credenciales", return_value=True),
        patch.object(adaptador, "crear_cliente", return_value=MagicMock()),
        patch.object(adaptador, "subir_objeto", side_effect=ObjetoYaExiste("ya existe")),
    ):
        resultado = adaptador.guardar_en_oci(_paquete(), ruta_objeto=RUTA)

    assert resultado["status"] == "ya_existe"
    assert resultado["nube_real"] is False


def test_guardar_en_oci_exito():
    config = _config(
        oci_user="u",
        oci_fingerprint="f",
        oci_tenancy="t",
        oci_key_content="k",
    )

    with (
        patch.object(adaptador, "_configuracion_oci", return_value=config),
        patch.object(adaptador, "hay_credenciales", return_value=True),
        patch.object(adaptador, "crear_cliente", return_value=MagicMock()),
        patch.object(adaptador, "subir_objeto", return_value=RUTA),
    ):
        resultado = adaptador.guardar_en_oci(_paquete(), ruta_objeto=RUTA)

    assert resultado["status"] == "guardado_con_exito"
    assert resultado["nube_real"] is True
    assert resultado["error_nube"] is None


def test_listar_activos_oci_offline(tmp_path):
    ruta = tmp_path / "bucket-test" / RUTA
    ruta.parent.mkdir(parents=True)
    ruta.write_text("{}", encoding="utf-8")

    with (
        patch.object(adaptador, "_configuracion_oci", return_value=_config()),
        patch.object(adaptador, "hay_credenciales", return_value=False),
        patch.object(adaptador, "DIRECTORIO_OFFLINE", tmp_path),
        patch.object(adaptador.st, "warning") as warning,
    ):
        objetos = adaptador.listar_activos_oci()

    assert len(objetos) == 1
    assert objetos[0]["origen"] == "local"
    assert objetos[0]["ruta_local"] == str(ruta)
    warning.assert_called_once()


def test_listar_activos_oci_nube():
    config = _config(
        oci_user="u",
        oci_fingerprint="f",
        oci_tenancy="t",
        oci_key_content="k",
    )

    with (
        patch.object(adaptador, "_configuracion_oci", return_value=config),
        patch.object(adaptador, "hay_credenciales", return_value=True),
        patch.object(adaptador, "crear_cliente", return_value=MagicMock()),
        patch.object(
            adaptador,
            "listar_objetos_detalle",
            return_value=[
                {"name": RUTA, "size": 10, "time_modified": None},
            ],
        ),
    ):
        objetos = adaptador.listar_activos_oci()

    assert len(objetos) == 1
    assert objetos[0]["origen"] == "nube"
    assert objetos[0]["tamano_bytes"] == 10


def test_configuracion_publica_no_expone_secretos():
    config = _config(
        oci_user="u",
        oci_fingerprint="f",
        oci_tenancy="t",
        oci_key_content="SECRETO-QUE-NO-DEBE-SALIR",
    )

    with (
        patch.object(adaptador, "_configuracion_oci", return_value=config),
        patch.object(adaptador, "hay_credenciales", return_value=True),
    ):
        publica = adaptador.configuracion_oci_publica()

    assert set(publica) == {"region", "bucket", "namespace", "hay_credenciales"}
    assert "SECRETO-QUE-NO-DEBE-SALIR" not in str(publica)
