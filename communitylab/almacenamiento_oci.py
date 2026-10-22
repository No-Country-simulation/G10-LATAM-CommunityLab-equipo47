"""Subida y listado de objetos en OCI Object Storage con el SDK de Python.

La aplicación usa el perfil `DEFAULT` (clave de API). El namespace, el bucket y la
región vienen de `config.py`, nunca escritos fijos aquí.

Convención de objetos: `entradas/AAAA-semana-NN/`, `informes/AAAA-semana-NN/` y
`activos/AAAA-semana-NN/`. El nombre se construye con `construir_nombre_objeto()`.

Los mensajes de error nunca incluyen claves ni rutas de archivos `.pem`.
"""

from __future__ import annotations

import configparser
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import oci

from .config import Configuracion

CATEGORIAS_PERMITIDAS = ("entradas", "informes", "activos")

_PATRON_PERIODO = re.compile(r"semana[_\-\s]*(\d{1,2})", re.IGNORECASE)


class ErrorAlmacenamiento(Exception):
    """Error claro al operar con OCI Object Storage."""


class ObjetoYaExiste(ErrorAlmacenamiento):
    """El objeto ya existe en el bucket y no se pidió sobrescribir."""


def resolver_semana(periodo_referencia: str, fecha: date | None = None) -> tuple[int, int]:
    """Devuelve `(anio, semana)` para la ruta `AAAA-semana-NN`.

    El número de semana sale de `periodo_referencia` (p. ej. `Semana_04_Sprints`)
    usando el año actual. Si no trae número, se usa la semana ISO de `fecha` con su
    año ISO (`isocalendar()`), no el año del calendario.
    """
    referencia = fecha or datetime.now().date()

    coincidencia = _PATRON_PERIODO.search(periodo_referencia or "")
    if coincidencia:
        semana = int(coincidencia.group(1))
        if 1 <= semana <= 53:
            return referencia.year, semana

    anio_iso, semana_iso, _ = referencia.isocalendar()
    return anio_iso, semana_iso


def construir_nombre_objeto(categoria: str, anio: int, semana: int, nombre_archivo: str) -> str:
    """Construye la clave del objeto siguiendo la convención del proyecto."""
    if categoria not in CATEGORIAS_PERMITIDAS:
        raise ErrorAlmacenamiento(
            f"Categoría no permitida: {categoria!r}. Usa una de {CATEGORIAS_PERMITIDAS}."
        )

    semana = int(semana)
    if not 1 <= semana <= 53:
        raise ErrorAlmacenamiento(f"Semana fuera de rango (1-53): {semana}")

    archivo = Path(nombre_archivo).name
    if not archivo:
        raise ErrorAlmacenamiento("El nombre del archivo no puede estar vacío.")

    return f"{categoria}/{int(anio)}-semana-{semana:02d}/{archivo}"


def _validar_datos_oci(config: Configuracion) -> None:
    """Valida que estén región, namespace y bucket, sin exponer valores."""
    faltan = [
        nombre
        for nombre, valor in {
            "OCI_REGION": config.oci_region,
            "OCI_NAMESPACE": config.oci_namespace,
            "OCI_BUCKET": config.oci_bucket,
        }.items()
        if not valor
    ]
    if faltan:
        raise ErrorAlmacenamiento("Faltan datos de OCI: " + ", ".join(faltan) + ".")


def perfil_default_disponible(config: Configuracion) -> bool:
    """Comprueba si existe el perfil configurado, sin leer la clave."""
    camino = Path(config.ruta_config_oci)
    if not camino.is_file():
        return False

    parser = configparser.ConfigParser()
    try:
        parser.read(camino, encoding="utf-8")
    except (OSError, configparser.Error):
        return False

    # `[DEFAULT]` es una sección especial para configparser.
    if config.oci_config_profile.upper() == "DEFAULT":
        return bool(parser.defaults())
    return parser.has_section(config.oci_config_profile)


def crear_cliente(config: Configuracion) -> oci.object_storage.ObjectStorageClient:
    """Crea el cliente con credenciales explícitas o con el perfil configurado."""
    _validar_datos_oci(config)

    if config.credenciales_explicitas_completas:
        datos_config = {
            "user": config.oci_user,
            "fingerprint": config.oci_fingerprint,
            "tenancy": config.oci_tenancy,
            "region": config.oci_region,
        }
        if config.oci_key_content:
            datos_config["key_content"] = config.oci_key_content
        elif config.oci_key_file:
            datos_config["key_file"] = str(Path(config.oci_key_file).expanduser())

        try:
            oci.config.validate_config(datos_config)
        except Exception as exc:
            raise ErrorAlmacenamiento(
                "La configuración explícita de OCI no es válida."
            ) from exc
        return oci.object_storage.ObjectStorageClient(datos_config)

    try:
        datos_config = oci.config.from_file(
            file_location=config.ruta_config_oci,
            profile_name=config.oci_config_profile,
        )
    except oci.exceptions.ConfigFileNotFound as exc:
        raise ErrorAlmacenamiento(
            f"No se encontró el archivo de configuración de OCI (perfil {config.oci_config_profile})."
        ) from exc
    except oci.exceptions.ProfileNotFound as exc:
        raise ErrorAlmacenamiento(
            f"No existe el perfil {config.oci_config_profile} en la configuración de OCI."
        ) from exc

    datos_config["region"] = config.oci_region
    return oci.object_storage.ObjectStorageClient(datos_config)


def existe_objeto(
    cliente: oci.object_storage.ObjectStorageClient,
    config: Configuracion,
    nombre_objeto: str,
) -> bool:
    """Indica si el objeto ya existe en el bucket."""
    try:
        cliente.head_object(config.oci_namespace, config.oci_bucket, nombre_objeto)
        return True
    except oci.exceptions.ServiceError as exc:
        if exc.status == 404:
            return False
        raise ErrorAlmacenamiento(_mensaje_servicio("consultar", nombre_objeto, exc)) from exc


def subir_objeto(
    cliente: oci.object_storage.ObjectStorageClient,
    config: Configuracion,
    nombre_objeto: str,
    contenido: Any,
    content_type: str = "application/json",
    sobrescribir: bool = False,
) -> str:
    """Sube contenido a un objeto del bucket y devuelve su nombre.

    `contenido` puede ser un `dict`/`list` (se serializa a JSON UTF-8), un `str` o
    `bytes`. Por defecto **no sobrescribe**: si el objeto existe, lanza
    `ErrorAlmacenamiento` salvo que se pase `sobrescribir=True`.
    """
    if isinstance(contenido, (dict, list)):
        cuerpo = json.dumps(contenido, ensure_ascii=False, indent=2).encode("utf-8")
    elif isinstance(contenido, str):
        cuerpo = contenido.encode("utf-8")
    else:
        cuerpo = bytes(contenido)

    if not sobrescribir and existe_objeto(cliente, config, nombre_objeto):
        raise ObjetoYaExiste(
            f"El objeto {nombre_objeto} ya existe; usa sobrescribir=True para reemplazarlo."
        )

    try:
        cliente.put_object(
            config.oci_namespace,
            config.oci_bucket,
            nombre_objeto,
            cuerpo,
            content_type=content_type,
        )
    except oci.exceptions.ServiceError as exc:
        raise ErrorAlmacenamiento(_mensaje_servicio("subir", nombre_objeto, exc)) from exc

    return nombre_objeto


def subir_archivo(
    cliente: oci.object_storage.ObjectStorageClient,
    config: Configuracion,
    nombre_objeto: str,
    ruta_archivo: str | Path,
    content_type: str = "application/json",
    sobrescribir: bool = False,
) -> str:
    """Sube el contenido de un archivo local a un objeto del bucket."""
    camino = Path(ruta_archivo)
    try:
        cuerpo = camino.read_bytes()
    except OSError as exc:
        raise ErrorAlmacenamiento(f"No se pudo leer el archivo local {camino.name}.") from exc

    return subir_objeto(
        cliente,
        config,
        nombre_objeto,
        cuerpo,
        content_type=content_type,
        sobrescribir=sobrescribir,
    )


def listar_objetos_detalle(
    cliente: oci.object_storage.ObjectStorageClient,
    config: Configuracion,
    prefijo: str = "",
) -> list[dict[str, Any]]:
    """Lista los objetos del bucket con nombre, tamaño y fecha, paginando hasta el final."""
    resultados: list[dict[str, Any]] = []
    inicio: str | None = None

    while True:
        try:
            respuesta = cliente.list_objects(
                config.oci_namespace,
                config.oci_bucket,
                prefix=prefijo,
                start=inicio,
            )
        except oci.exceptions.ServiceError as exc:
            raise ErrorAlmacenamiento(_mensaje_servicio("listar", prefijo or "todos", exc)) from exc

        for objeto in respuesta.data.objects:
            resultados.append(
                {
                    "name": objeto.name,
                    "size": getattr(objeto, "size", None) or 0,
                    "time_modified": getattr(objeto, "time_modified", None),
                }
            )

        inicio = respuesta.data.next_start_with
        if not inicio:
            break

    return resultados


def listar_objetos(
    cliente: oci.object_storage.ObjectStorageClient,
    config: Configuracion,
    prefijo: str = "",
) -> list[str]:
    """Lista los nombres de objeto del bucket, paginando hasta el final."""
    return [item["name"] for item in listar_objetos_detalle(cliente, config, prefijo)]


def _mensaje_servicio(accion: str, referencia: str, exc: oci.exceptions.ServiceError) -> str:
    """Mensaje de error de OCI sin claves ni rutas de credenciales."""
    detalle = exc.message or "sin detalle"
    return f"Error al {accion} '{referencia}' en OCI (HTTP {exc.status}): {detalle}"
