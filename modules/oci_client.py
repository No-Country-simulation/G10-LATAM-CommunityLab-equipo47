"""Adaptador de OCI Object Storage para las vistas del prototipo.

La lógica real vive en `communitylab/almacenamiento_oci.py`. Este módulo conserva
`guardar_en_oci` y `listar_activos_oci` (mismas claves de retorno que usan las vistas)
y añade el estado y el modo necesarios para no reportar éxito falso.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import streamlit as st

from communitylab.almacenamiento_oci import (
    ErrorAlmacenamiento,
    ObjetoYaExiste,
    construir_nombre_objeto,
    crear_cliente,
    listar_objetos_detalle,
    perfil_default_disponible,
    resolver_semana,
    subir_objeto,
)
from communitylab.config import Configuracion, cargar_configuracion

DIRECTORIO_OFFLINE = Path(__file__).resolve().parent.parent / "data" / "salida" / "oci_offline"


def _leer_secretos_oci() -> dict | None:
    """Lee `st.secrets['oci']`; devuelve `None` si no existe el archivo o la sección."""
    try:
        datos = st.secrets["oci"]
        return dict(datos)
    except Exception:
        return None


def _configuracion_oci() -> Configuracion:
    """Configuración con secretos (prioridad) y entorno/`DEFAULT` como respaldo."""
    base = cargar_configuracion(validar_oci=False)
    datos = _leer_secretos_oci()
    if not datos:
        return base

    return Configuracion(
        gemini_api_key=base.gemini_api_key,
        gemini_model=base.gemini_model,
        oci_config_file=base.oci_config_file,
        oci_config_profile=base.oci_config_profile,
        oci_region=str(datos.get("region") or base.oci_region),
        oci_namespace=str(datos.get("namespace") or base.oci_namespace),
        oci_bucket=str(datos.get("bucket") or base.oci_bucket),
        oci_user=str(datos.get("user") or base.oci_user),
        oci_fingerprint=str(datos.get("fingerprint") or base.oci_fingerprint),
        oci_tenancy=str(datos.get("tenancy") or base.oci_tenancy),
        oci_key_content=str(datos.get("key_content") or base.oci_key_content),
        oci_key_file=str(datos.get("key_file") or base.oci_key_file),
    )


def hay_credenciales(config: Configuracion) -> bool:
    """Credenciales explícitas completas o perfil DEFAULT existente."""
    return config.credenciales_explicitas_completas or perfil_default_disponible(config)


def configuracion_oci_publica() -> dict:
    """Datos no sensibles para mostrar en la vista (región, bucket y si hay credenciales)."""
    config = _configuracion_oci()
    return {
        "region": config.oci_region,
        "bucket": config.oci_bucket,
        "namespace": config.oci_namespace,
        "hay_credenciales": hay_credenciales(config),
    }


def ruta_sugerida_para_paquete(paquete: dict) -> str:
    """Ruta `activos/AAAA-semana-NN/paquete-distribucion.json` según el periodo."""
    periodo = (
        paquete.get("resumen_comunidad", {}).get("periodo_referencia")
        or paquete.get("periodo_referencia", "")
    )
    anio, semana = resolver_semana(periodo)
    return construir_nombre_objeto("activos", anio, semana, "paquete-distribucion.json")


def _mensaje_error(exc: Exception) -> str:
    """Mensaje de error sin configuración, claves ni rutas de `.pem`."""
    if isinstance(exc, ErrorAlmacenamiento):
        return str(exc)
    return f"Error al operar con OCI ({type(exc).__name__})."


def _guardar_offline(paquete: dict, bucket: str, ruta: str) -> dict:
    destino = DIRECTORIO_OFFLINE / bucket / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(paquete, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "bucket": bucket,
        "ruta_objeto": ruta,
        "status": "guardado_local",
        "modo": "offline",
        "nube_real": False,
        "ruta_local_espejo": str(destino),
        "error_nube": None,
        "aviso": "Sin credenciales OCI: el paquete se guardó solo en local (no en el bucket).",
    }


def guardar_en_oci(
    paquete: dict,
    bucket_name: str | None = None,
    ruta_objeto: str | None = None,
    sobrescribir: bool = False,
) -> dict:
    """Persiste el paquete en OCI o en el espejo offline, sin reportar éxito falso."""
    config = _configuracion_oci()
    if bucket_name:
        config = replace(config, oci_bucket=bucket_name)

    ruta = ruta_objeto or ruta_sugerida_para_paquete(paquete)
    bucket = config.oci_bucket or bucket_name or "sin-bucket"

    if not hay_credenciales(config):
        return _guardar_offline(paquete, bucket, ruta)

    try:
        cliente = crear_cliente(config)
        subir_objeto(cliente, config, ruta, paquete, sobrescribir=sobrescribir)
    except ObjetoYaExiste as exc:
        return {
            "bucket": bucket,
            "ruta_objeto": ruta,
            "status": "ya_existe",
            "modo": "OCI_Cloud_SDK",
            "nube_real": False,
            "ruta_local_espejo": "",
            "error_nube": str(exc),
            "aviso": "El objeto ya existe. Confirma la sobrescritura para reemplazarlo.",
        }
    except Exception as exc:
        return {
            "bucket": bucket,
            "ruta_objeto": ruta,
            "status": "error_al_guardar",
            "modo": "OCI_Cloud_SDK",
            "nube_real": False,
            "ruta_local_espejo": "",
            "error_nube": _mensaje_error(exc),
            "aviso": None,
        }

    return {
        "bucket": bucket,
        "ruta_objeto": ruta,
        "status": "guardado_con_exito",
        "modo": "OCI_Cloud_SDK",
        "nube_real": True,
        "ruta_local_espejo": "",
        "error_nube": None,
        "aviso": None,
    }


def _listar_offline(bucket: str) -> list[dict]:
    base = DIRECTORIO_OFFLINE / bucket
    if not base.is_dir():
        return []

    archivos = []
    for camino in sorted(base.rglob("*.json")):
        archivos.append(
            {
                "nombre": camino.name,
                "ruta_objeto": str(camino.relative_to(base)).replace("\\", "/"),
                "tamano_bytes": camino.stat().st_size,
                "fecha_modificacion": camino.stat().st_mtime,
                "origen": "local",
                "ruta_local": str(camino),
            }
        )
    return archivos


def listar_activos_oci(bucket_name: str | None = None) -> list[dict]:
    """Lista en la nube (paginado) o en el espejo local, indicando el origen."""
    config = _configuracion_oci()
    if bucket_name:
        config = replace(config, oci_bucket=bucket_name)
    bucket = config.oci_bucket or bucket_name or "sin-bucket"

    if not hay_credenciales(config):
        st.warning("Modo offline: mostrando los objetos del espejo local (no del bucket OCI).")
        return _listar_offline(bucket)

    try:
        cliente = crear_cliente(config)
        objetos = listar_objetos_detalle(cliente, config)
    except Exception as exc:
        st.error(_mensaje_error(exc))
        return []

    return [
        {
            "nombre": obj["name"].split("/")[-1],
            "ruta_objeto": obj["name"],
            "tamano_bytes": obj["size"],
            "fecha_modificacion": str(obj["time_modified"] or "OCI"),
            "origen": "nube",
            "ruta_local": "",
        }
        for obj in objetos
    ]
