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
    gemini_model: str = "gemini-3.5-flash-lite"
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
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
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


# --- Análisis con el LLM (Fase 3) ---------------------------------------------

# Pesos de la puntuación de relevancia. Deben sumar 1.0. El LLM devuelve
# sub-puntuaciones (0-100) y el código calcula la puntuación final con estos pesos.
PESOS_PUNTUACION: dict[str, float] = {
    "relevancia_comunidad": 0.4,
    "impacto_publicable": 0.3,
    "claridad": 0.2,
    "novedad": 0.1,
}

# Modelos de Gemini que usan muestreo fijo: Google ignora (y LangChain descarta) los
# parámetros de muestreo como `temperature`. Para ellos no se fija `temperature`; la
# reproducibilidad la da la caché, no la temperatura.
MODELOS_MUESTREO_FIJO: tuple[str, ...] = ("gemini-3.5-flash-lite", "gemini-3.6-flash")

# Presupuesto y ritmo de llamadas, para respetar la cuota gratuita de Gemini
# (15 solicitudes/min, 250K tokens/min, 500/día). La clave es compartida por el equipo,
# así que la espera es por proceso (no coordinación entre personas).
LLAMADAS_NOMINALES_POR_LOTE = 3  # 1 análisis + 1 LinkedIn + 1 FAQ
MAX_LLAMADAS_POR_OPERACION = 4  # por operación: 1 + 2×429 + 1 reparación
MAX_LLAMADAS_POR_LOTE = 12  # techo absoluto del lote: 3 operaciones × 4
MAX_REINTENTOS_429 = 2  # reintentos propios ante un error 429
REINTENTOS_VALIDACION = 1  # una reparación si la salida no valida con Pydantic
MAX_REINTENTOS_CLIENTE = 1  # `max_retries` del cliente: sin reintentos ocultos
# Si un 429 pide esperar más que esto, se falla de inmediato (cuota agotada) sin reintentar.
MAX_ESPERA_ACEPTABLE_SEG = 60

# Esperas (segundos).
ESPERA_MINIMA_ENTRE_LLAMADAS_SEG = 4.0  # 15 RPM -> 60/15 = 4 s entre llamadas
ESPERA_POR_DEFECTO_429_SEG = 20.0  # si el error 429 no trae `retry_delay`
ESPERA_MAXIMA_REINTENTO_SEG = 60.0  # tope de espera ante un 429
TIMEOUT_LLM_SEG = 60

# Rutas de trabajo (relativas a la raíz del proyecto).
RUTA_PROMPT_ANALISIS = "prompts/analisis.md"
DIRECTORIO_CACHE_LLM = "data/salida/cache"

# --- Generadores por canal (Fase 4) -------------------------------------------
RUTA_PROMPT_LINKEDIN = "prompts/linkedin.md"
RUTA_PROMPT_FAQ = "prompts/faq.md"

# LinkedIn: topes editoriales (no el límite de la plataforma), contados sobre el copy.
LONGITUD_MIN_COPY_LINKEDIN = 300
LONGITUD_MAX_COPY_LINKEDIN = 1300
# Hashtags al final del copy: completos y entre un mínimo y un máximo.
HASHTAGS_MIN_LINKEDIN = 3
HASHTAGS_MAX_LINKEDIN = 5

# Selección temporal de la interacción hasta el router (Fase 5). No hay llamadas nuevas
# al LLM: se reordenan las sub-puntuaciones ya calculadas.
TIPOS_LINKEDIN: tuple[str, ...] = ("testimonio",)
SENTIMIENTOS_LINKEDIN: tuple[str, ...] = ("muy_positivo",)
TIPOS_FAQ: tuple[str, ...] = ("pregunta_tecnica",)
PESOS_SELECCION_FAQ: dict[str, float] = {
    "claridad": 0.5,
    "relevancia_comunidad": 0.35,
    "novedad": 0.1,
    "impacto_publicable": 0.05,
}

# Campos de la FAQ que arma el código (no se le piden al LLM).
PLANTILLA_ORIGEN_FAQ = "Duda planteada por {autor} en {canal}"
STATUS_FAQ = "derivado_a_mentoria"  # valor de la consigna (a revisar el 9-oct)
