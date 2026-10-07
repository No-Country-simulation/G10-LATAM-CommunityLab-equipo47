"""Lectura de la configuración de CommunityLab desde variables de entorno.

Los valores vienen de `.env` (que no se versiona) y nunca se escriben fijos en el
código. La clave de Gemini queda fuera del `repr` para no imprimirla por accidente.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


class ErrorConfiguracion(Exception):
    """Falta un valor obligatorio de configuración."""


@dataclass(frozen=True)
class Configuracion:
    """Configuración de la aplicación, leída del entorno."""

    gemini_api_key: str = field(default="", repr=False)
    gemini_model: str = "gemini-2.5-flash"
    oci_config_file: str = "~/.oci/config"
    oci_config_profile: str = "DEFAULT"
    oci_region: str = "sa-santiago-1"
    oci_namespace: str = ""
    oci_bucket: str = "communitylab-activos-marketing"

    @property
    def ruta_config_oci(self) -> str:
        """Ruta real al archivo de configuración de OCI, con `~` expandido."""
        return str(Path(self.oci_config_file).expanduser())


def cargar_configuracion(ruta_env: str | None = None) -> Configuracion:
    """Carga `.env` y devuelve la configuración validada.

    `ruta_env` permite apuntar a un archivo concreto (útil en tests); si es `None`,
    se usa el `.env` habitual del proyecto.
    """
    load_dotenv(dotenv_path=ruta_env)

    config = Configuracion(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        oci_config_file=os.getenv("OCI_CONFIG_FILE", "~/.oci/config"),
        oci_config_profile=os.getenv("OCI_CONFIG_PROFILE", "DEFAULT"),
        oci_region=os.getenv("OCI_REGION", "sa-santiago-1"),
        oci_namespace=os.getenv("OCI_NAMESPACE", ""),
        oci_bucket=os.getenv("OCI_BUCKET", ""),
    )

    obligatorios = {
        "OCI_NAMESPACE": config.oci_namespace,
        "OCI_BUCKET": config.oci_bucket,
    }
    faltan = [nombre for nombre, valor in obligatorios.items() if not valor]
    if faltan:
        raise ErrorConfiguracion(
            "Faltan variables obligatorias en el entorno: " + ", ".join(faltan)
        )

    return config
