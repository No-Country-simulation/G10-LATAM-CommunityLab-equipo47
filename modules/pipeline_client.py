"""Configuración del pipeline para Streamlit (Gemini desde entorno o secretos)."""

from __future__ import annotations

from dataclasses import replace

import streamlit as st

from communitylab.config import Configuracion, cargar_configuracion


def _leer_secretos_gemini() -> dict | None:
    """Lee `st.secrets['gemini']`; `None` si no existe el archivo o la sección."""
    try:
        datos = st.secrets["gemini"]
        return dict(datos)
    except Exception:
        return None


def construir_configuracion() -> Configuracion:
    """Configuración desde entorno y, con prioridad, desde `st.secrets['gemini']`."""
    base = cargar_configuracion(validar_oci=False)
    datos = _leer_secretos_gemini()
    if not datos:
        return base

    return replace(
        base,
        gemini_api_key=str(datos.get("api_key") or base.gemini_api_key),
        gemini_model=str(datos.get("model") or base.gemini_model),
    )
