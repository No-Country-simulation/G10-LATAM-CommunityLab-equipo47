"""Lectura y validación de lotes de interacciones de la comunidad."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .modelos import LoteEntrada


class ErrorIngesta(Exception):
    """Error claro al leer o validar un lote de interacciones."""


def leer_lote_json(ruta: str | Path) -> LoteEntrada:
    """Lee un lote JSON y lo valida contra el modelo `LoteEntrada`.

    Lanza `ErrorIngesta` con un mensaje claro si el archivo no existe, no es JSON
    válido o no cumple el esquema.
    """
    camino = Path(ruta)

    try:
        contenido = camino.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ErrorIngesta(f"No se encontró el lote: {camino.name}") from exc
    except OSError as exc:
        raise ErrorIngesta(f"No se pudo leer el lote {camino.name}.") from exc

    try:
        datos = json.loads(contenido)
    except json.JSONDecodeError as exc:
        raise ErrorIngesta(
            f"El lote {camino.name} no es JSON válido (línea {exc.lineno})."
        ) from exc

    try:
        return LoteEntrada.model_validate(datos)
    except ValidationError as exc:
        raise ErrorIngesta(
            f"El lote {camino.name} no cumple el esquema: {exc.error_count()} error(es)."
        ) from exc


def leer_lotes(directorio: str | Path) -> list[LoteEntrada]:
    """Lee y valida todos los lotes `.json` de un directorio, en orden."""
    carpeta = Path(directorio)
    if not carpeta.is_dir():
        raise ErrorIngesta(f"No existe el directorio de lotes: {carpeta.name}")

    return [leer_lote_json(archivo) for archivo in sorted(carpeta.glob("*.json"))]
