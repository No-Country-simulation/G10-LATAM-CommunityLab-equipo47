"""Pruebas de la lectura de configuración desde variables de entorno."""

from pathlib import Path

import pytest

from communitylab.config import ErrorConfiguracion, cargar_configuracion


def _sin_env_oci(monkeypatch):
    for clave in ("OCI_NAMESPACE", "OCI_BUCKET", "OCI_CONFIG_FILE", "OCI_CONFIG_PROFILE", "OCI_REGION"):
        monkeypatch.delenv(clave, raising=False)


def test_carga_configuracion_desde_entorno(monkeypatch, tmp_path):
    _sin_env_oci(monkeypatch)
    monkeypatch.setenv("OCI_NAMESPACE", "namespace-test")
    monkeypatch.setenv("OCI_BUCKET", "bucket-test")
    monkeypatch.setenv("OCI_REGION", "sa-santiago-1")

    config = cargar_configuracion(ruta_env=str(tmp_path / "no_existe.env"))

    assert config.oci_namespace == "namespace-test"
    assert config.oci_bucket == "bucket-test"
    assert config.oci_region == "sa-santiago-1"


def test_expande_el_home_en_la_ruta_de_config(monkeypatch, tmp_path):
    _sin_env_oci(monkeypatch)
    monkeypatch.setenv("OCI_NAMESPACE", "n")
    monkeypatch.setenv("OCI_BUCKET", "b")
    monkeypatch.setenv("OCI_CONFIG_FILE", "~/.oci/config")

    config = cargar_configuracion(ruta_env=str(tmp_path / "no_existe.env"))

    assert config.ruta_config_oci == str(Path("~/.oci/config").expanduser())
    assert "~" not in config.ruta_config_oci


def test_falta_namespace_lanza_error(monkeypatch, tmp_path):
    _sin_env_oci(monkeypatch)
    monkeypatch.setenv("OCI_BUCKET", "b")

    with pytest.raises(ErrorConfiguracion):
        cargar_configuracion(ruta_env=str(tmp_path / "no_existe.env"))


def test_falta_bucket_lanza_error(monkeypatch, tmp_path):
    _sin_env_oci(monkeypatch)
    monkeypatch.setenv("OCI_NAMESPACE", "n")

    with pytest.raises(ErrorConfiguracion):
        cargar_configuracion(ruta_env=str(tmp_path / "no_existe.env"))


def test_la_clave_de_gemini_no_aparece_en_el_repr(monkeypatch, tmp_path):
    _sin_env_oci(monkeypatch)
    monkeypatch.setenv("OCI_NAMESPACE", "n")
    monkeypatch.setenv("OCI_BUCKET", "b")
    monkeypatch.setenv("GEMINI_API_KEY", "clave-secreta-123")

    config = cargar_configuracion(ruta_env=str(tmp_path / "no_existe.env"))

    assert "clave-secreta-123" not in repr(config)
