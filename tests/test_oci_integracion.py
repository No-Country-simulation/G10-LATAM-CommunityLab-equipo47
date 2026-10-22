"""Pruebas de integración OCI con mocks (sin red)."""

from datetime import date
import json
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
from communitylab.modelos import EstadoAprobacion, PaqueteDistribucion

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


def _paquete_con_activos(activos: dict, periodo="Semestre_2026_1_Semana_04") -> dict:
    paquete = _paquete(periodo)
    paquete["activos_distribucion_generados"] = activos
    return paquete


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


def test_limpiar_paquete_quita_activos_vacios_sin_mutar_original():
    paquete = {
        "activos_distribucion_generados": {
            "post_linkedin": {"titulo": "", "copy": "copy"},
            "destaque_newsletter_semanal": {"titular": "t", "resumen": "   "},
            "sugerencia_contenido_faq": {"tema": "  "},
        }
    }

    limpio = adaptador.limpiar_paquete_para_guardar(paquete)

    assert limpio["activos_distribucion_generados"] == {}
    assert paquete["activos_distribucion_generados"]["post_linkedin"]["titulo"] == ""


def test_limpiar_paquete_conserva_activos_completos():
    activos = {
        "post_linkedin": {"titulo": "Titulo", "copy": "Copy"},
        "destaque_newsletter_semanal": {"titular": "Titular", "resumen": "Resumen"},
        "sugerencia_contenido_faq": {"tema": "Tema"},
    }
    paquete = {"activos_distribucion_generados": activos}

    limpio = adaptador.limpiar_paquete_para_guardar(paquete)

    assert limpio["activos_distribucion_generados"] == activos
    assert limpio is not paquete


def test_guardar_en_oci_limpia_antes_de_subir():
    config = _config(
        oci_user="u",
        oci_fingerprint="f",
        oci_tenancy="t",
        oci_key_content="k",
    )
    paquete = {
        "activos_distribucion_generados": {
            "post_linkedin": {"titulo": "", "copy": "Copy"},
            "sugerencia_contenido_faq": {"tema": "Tema"},
        }
    }

    with (
        patch.object(adaptador, "_configuracion_oci", return_value=config),
        patch.object(adaptador, "hay_credenciales", return_value=True),
        patch.object(adaptador, "crear_cliente", return_value=MagicMock()),
        patch.object(adaptador, "subir_objeto", return_value=RUTA) as subir,
    ):
        adaptador.guardar_en_oci(paquete, ruta_objeto=RUTA)

    contenido = subir.call_args.args[3]
    assert "post_linkedin" not in contenido["activos_distribucion_generados"]
    assert "sugerencia_contenido_faq" in contenido["activos_distribucion_generados"]
    assert "post_linkedin" in paquete["activos_distribucion_generados"]


def test_guardar_en_oci_offline_limpia(tmp_path):
    paquete = {
        "activos_distribucion_generados": {
            "post_linkedin": {"titulo": "", "copy": "Copy"},
        }
    }

    with (
        patch.object(adaptador, "_configuracion_oci", return_value=_config()),
        patch.object(adaptador, "hay_credenciales", return_value=False),
        patch.object(adaptador, "DIRECTORIO_OFFLINE", tmp_path),
    ):
        adaptador.guardar_en_oci(paquete, ruta_objeto=RUTA)

    destino = tmp_path / "bucket-test" / RUTA
    contenido = json.loads(destino.read_text(encoding="utf-8"))
    assert "post_linkedin" not in contenido["activos_distribucion_generados"]


# --- Preparación del paquete para guardar ------------------------------------

def test_preparar_paquete_actualiza_metadatos_y_no_muta_original():
    paquete = _paquete_con_activos(
        {
            "post_linkedin": {
                "titulo": "Titulo",
                "copy": "Copy",
                "canal_recomendado": "LinkedIn",
                "potencial_engagement": "Alto",
                "estado_aprobacion": "pendiente",
                "estado_curaduria": "Aprobado para Publicar",
            }
        }
    )
    paquete["almacenamiento_oci"] = {
        "bucket": "bucket-viejo",
        "ruta_objeto": RUTA,
        "status": "guardado_con_exito",
    }

    preparado = adaptador.preparar_paquete_para_guardar(
        paquete,
        bucket="bucket-real",
        ruta="pruebas/roberto/prueba-ui.json",
    )

    assert preparado["almacenamiento_oci"] == {
        "bucket": "bucket-real",
        "ruta_objeto": "pruebas/roberto/prueba-ui.json",
    }
    assert preparado is not paquete
    assert (
        preparado["activos_distribucion_generados"]
        is not paquete["activos_distribucion_generados"]
    )
    assert paquete["almacenamiento_oci"]["bucket"] == "bucket-viejo"
    assert paquete["almacenamiento_oci"]["status"] == "guardado_con_exito"


def test_guardar_en_oci_sube_copia_con_ruta_real_sin_mutar_original():
    config = _config(
        oci_user="u",
        oci_fingerprint="f",
        oci_tenancy="t",
        oci_key_content="k",
    )
    paquete = _paquete_con_activos(
        {
            "post_linkedin": {
                "titulo": "Titulo",
                "copy": "Copy",
                "canal_recomendado": "LinkedIn",
                "potencial_engagement": "Alto",
                "estado_aprobacion": "pendiente",
                "estado_curaduria": "Aprobado para Publicar",
            }
        }
    )
    paquete["almacenamiento_oci"] = {
        "bucket": "bucket-test",
        "ruta_objeto": RUTA,
    }

    with (
        patch.object(adaptador, "_configuracion_oci", return_value=config),
        patch.object(adaptador, "hay_credenciales", return_value=True),
        patch.object(adaptador, "crear_cliente", return_value=MagicMock()),
        patch.object(adaptador, "subir_objeto", return_value="ok") as subir,
    ):
        resultado = adaptador.guardar_en_oci(
            paquete,
            ruta_objeto="pruebas/roberto/prueba-ui.json",
        )

    contenido = subir.call_args.args[3]
    assert contenido["almacenamiento_oci"] == {
        "bucket": "bucket-test",
        "ruta_objeto": "pruebas/roberto/prueba-ui.json",
    }
    assert (
        contenido["activos_distribucion_generados"]["post_linkedin"][
            "estado_aprobacion"
        ]
        == "aprobado"
    )
    assert paquete["almacenamiento_oci"]["ruta_objeto"] == RUTA
    assert resultado["ruta_objeto"] == "pruebas/roberto/prueba-ui.json"


@pytest.mark.parametrize(
    "decision, estado_inicial, esperado",
    [
        ("Aprobado para Publicar", "pendiente", "aprobado"),
        ("Pendiente de Modificaciones", "aprobado", "pendiente"),
        ("Rechazado", "aprobado", "rechazado"),
    ],
)
def test_preparar_paquete_mapea_aprobacion_linkedin(
    decision, estado_inicial, esperado
):
    paquete = _paquete_con_activos(
        {
            "post_linkedin": {
                "titulo": "Titulo",
                "copy": "Copy",
                "canal_recomendado": "LinkedIn",
                "potencial_engagement": "Alto",
                "estado_aprobacion": estado_inicial,
                "estado_curaduria": decision,
            }
        }
    )

    preparado = adaptador.preparar_paquete_para_guardar(paquete, "bucket", RUTA)

    assert (
        preparado["activos_distribucion_generados"]["post_linkedin"][
            "estado_aprobacion"
        ]
        == esperado
    )


@pytest.mark.parametrize(
    "decision, esperado",
    [
        ("Incluir en la Edición Semanal", "aprobado"),
        ("Omitir en este envío", "rechazado"),
    ],
)
def test_preparar_paquete_mapea_aprobacion_newsletter(decision, esperado):
    paquete = _paquete_con_activos(
        {
            "destaque_newsletter_semanal": {
                "seccion": "Seccion",
                "titular": "Titular",
                "resumen": "Resumen",
                "estado_aprobacion": "pendiente",
                "estado_curaduria": decision,
            }
        }
    )

    preparado = adaptador.preparar_paquete_para_guardar(paquete, "bucket", RUTA)

    assert (
        preparado["activos_distribucion_generados"][
            "destaque_newsletter_semanal"
        ]["estado_aprobacion"]
        == esperado
    )


def test_preparar_paquete_sin_estado_curaduria_no_cambia_aprobacion():
    paquete = _paquete_con_activos(
        {
            "post_linkedin": {
                "titulo": "Titulo",
                "copy": "Copy",
                "canal_recomendado": "LinkedIn",
                "potencial_engagement": "Alto",
                "estado_aprobacion": "rechazado",
            },
            "destaque_newsletter_semanal": {
                "seccion": "Seccion",
                "titular": "Titular",
                "resumen": "Resumen",
            },
        }
    )

    preparado = adaptador.preparar_paquete_para_guardar(paquete, "bucket", RUTA)

    post = preparado["activos_distribucion_generados"]["post_linkedin"]
    newsletter = preparado["activos_distribucion_generados"][
        "destaque_newsletter_semanal"
    ]
    assert post["estado_aprobacion"] == "rechazado"
    assert "estado_aprobacion" not in newsletter


def test_preparar_paquete_no_toca_faq():
    paquete = _paquete_con_activos(
        {
            "sugerencia_contenido_faq": {
                "tema": "Tema",
                "origen": "Comunidad",
                "status": "descartado",
                "pregunta": "Pregunta",
                "respuesta_sugerida": "Respuesta",
                "estado_aprobacion": "aprobado",
            }
        }
    )

    preparado = adaptador.preparar_paquete_para_guardar(paquete, "bucket", RUTA)

    faq = preparado["activos_distribucion_generados"]["sugerencia_contenido_faq"]
    assert faq["status"] == "descartado"
    assert faq["estado_aprobacion"] == "aprobado"


def test_guardar_en_oci_offline_escribe_metadatos_y_aprobacion(tmp_path):
    paquete = _paquete_con_activos(
        {
            "post_linkedin": {
                "titulo": "Titulo",
                "copy": "Copy",
                "canal_recomendado": "LinkedIn",
                "potencial_engagement": "Alto",
                "estado_aprobacion": "pendiente",
                "estado_curaduria": "Aprobado para Publicar",
            }
        }
    )
    paquete["almacenamiento_oci"] = {
        "bucket": "bucket-viejo",
        "ruta_objeto": RUTA,
    }

    with (
        patch.object(adaptador, "_configuracion_oci", return_value=_config()),
        patch.object(adaptador, "hay_credenciales", return_value=False),
        patch.object(adaptador, "DIRECTORIO_OFFLINE", tmp_path),
    ):
        resultado = adaptador.guardar_en_oci(
            paquete,
            ruta_objeto="pruebas/roberto/prueba-ui-offline.json",
        )

    assert resultado["status"] == "guardado_local"
    destino = tmp_path / "bucket-test" / "pruebas/roberto/prueba-ui-offline.json"
    contenido = json.loads(destino.read_text(encoding="utf-8"))
    assert contenido["almacenamiento_oci"] == {
        "bucket": "bucket-test",
        "ruta_objeto": "pruebas/roberto/prueba-ui-offline.json",
    }
    assert (
        contenido["activos_distribucion_generados"]["post_linkedin"][
            "estado_aprobacion"
        ]
        == "aprobado"
    )
    assert paquete["almacenamiento_oci"]["bucket"] == "bucket-viejo"


def test_paquete_preparado_valida_con_el_modelo():
    ruta_ejemplo = (
        Path(__file__).resolve().parent.parent
        / "docs"
        / "ejemplo-paquete-distribucion.json"
    )
    paquete = json.loads(ruta_ejemplo.read_text(encoding="utf-8"))
    paquete["activos_distribucion_generados"]["post_linkedin"][
        "estado_curaduria"
    ] = "Aprobado para Publicar"

    preparado = adaptador.preparar_paquete_para_guardar(
        paquete,
        bucket="bucket-real",
        ruta="pruebas/roberto/prueba-ui.json",
    )
    validado = PaqueteDistribucion.model_validate(preparado)

    assert validado.almacenamiento_oci.bucket == "bucket-real"
    assert validado.almacenamiento_oci.ruta_objeto == "pruebas/roberto/prueba-ui.json"
    assert validado.almacenamiento_oci.status is None
    assert (
        validado.activos_distribucion_generados.post_linkedin.estado_aprobacion
        == EstadoAprobacion.APROBADO
    )


def test_preparar_paquete_combina_limpieza_y_metadatos():
    paquete = _paquete_con_activos(
        {
            "post_linkedin": {"titulo": "", "copy": "Copy"},
            "sugerencia_contenido_faq": {
                "tema": "Tema",
                "origen": "Comunidad",
                "status": "derivado_a_mentoria",
            },
        }
    )
    paquete["almacenamiento_oci"] = {
        "bucket": "bucket-viejo",
        "ruta_objeto": RUTA,
    }

    preparado = adaptador.preparar_paquete_para_guardar(
        paquete,
        bucket="bucket-test",
        ruta="activos/2026-semana-05/paquete-distribucion.json",
    )

    activos = preparado["activos_distribucion_generados"]
    assert "post_linkedin" not in activos
    assert "sugerencia_contenido_faq" in activos
    assert preparado["almacenamiento_oci"] == {
        "bucket": "bucket-test",
        "ruta_objeto": "activos/2026-semana-05/paquete-distribucion.json",
    }
    assert "post_linkedin" in paquete["activos_distribucion_generados"]
