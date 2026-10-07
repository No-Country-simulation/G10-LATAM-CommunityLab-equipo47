"""Modelos de datos de CommunityLab.

- Modelos de **entrada**: describen un lote de interacciones de la comunidad.
- Modelos de **salida**: representan el `paquete-distribucion.json` descrito en
  `docs/esquema-paquete-distribucion.md`.

Se validan con Pydantic. Los campos que produce nuestro código o el LLM van como
enums estrictos (`sentimiento`, `ruta`, `estado_aprobacion`). El campo `tipo` llega
desde los datos de la comunidad, así que se deja como texto libre para no romper la
ingesta ante un tipo desconocido.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


# --- Enums de campos cerrados -------------------------------------------------

class Sentimiento(str, Enum):
    """Sentimiento detectado en una interacción."""

    MUY_POSITIVO = "muy_positivo"
    POSITIVO = "positivo"
    NEUTRO = "neutro"
    NEGATIVO = "negativo"


class Ruta(str, Enum):
    """Decisión del router para una interacción."""

    POST_LINKEDIN = "post_linkedin"
    FAQ = "faq"
    APOYO = "apoyo"
    SIN_ACTIVO = "sin_activo"


class EstadoAprobacion(str, Enum):
    """Estado de revisión de un activo (lo cambia la interfaz Streamlit)."""

    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


# --- Modelos de entrada -------------------------------------------------------

class Interaccion(BaseModel):
    """Una interacción de la comunidad."""

    autor: str = Field(min_length=1)
    canal: str = Field(min_length=1)
    tipo: str = Field(min_length=1)
    texto: str = Field(min_length=1)
    pais: str | None = None


class LoteEntrada(BaseModel):
    """Lote de interacciones de una comunidad y periodo."""

    origen_comunidad: str = Field(min_length=1)
    periodo_referencia: str = Field(min_length=1)
    interacciones: list[Interaccion] = Field(min_length=1)


# --- Modelos de salida (paquete-distribucion.json) ----------------------------

class ResumenComunidad(BaseModel):
    """Resumen consolidado de la comunidad."""

    origen_comunidad: str
    periodo_referencia: str
    total_interacciones_procesadas: int = Field(ge=0)
    sentimiento_predominante: str
    temas_principales: list[str]


class AnalisisInteraccion(BaseModel):
    """Análisis de una interacción: sentimiento, temas, relevancia y ruta."""

    autor: str
    canal: str
    tipo: str
    sentimiento: Sentimiento
    temas: list[str]
    puntuacion_relevancia: int = Field(ge=0, le=100)
    motivo_puntuacion: str
    ruta: Ruta


class PostLinkedIn(BaseModel):
    """Activo de LinkedIn (caso de éxito del MVP)."""

    titulo: str
    # `copy` es el nombre exacto del esquema; Pydantic avisa porque tapa un método
    # obsoleto de BaseModel. Se mantiene para que el paquete se serialice igual.
    copy: str
    canal_recomendado: str
    potencial_engagement: str
    estado_aprobacion: EstadoAprobacion = EstadoAprobacion.PENDIENTE


class SugerenciaContenidoFaq(BaseModel):
    """Activo de FAQ (duda técnica)."""

    tema: str
    origen: str
    status: str
    pregunta: str
    respuesta_sugerida: str
    estado_aprobacion: EstadoAprobacion = EstadoAprobacion.PENDIENTE


class DestaqueNewsletter(BaseModel):
    """Formato extra opcional: destaque de newsletter semanal."""

    seccion: str
    titular: str
    resumen: str
    estado_aprobacion: EstadoAprobacion = EstadoAprobacion.PENDIENTE


class ActivosDistribucion(BaseModel):
    """Activos de marketing generados a partir del análisis."""

    post_linkedin: PostLinkedIn
    sugerencia_contenido_faq: SugerenciaContenidoFaq
    destaque_newsletter_semanal: DestaqueNewsletter | None = None


class AlmacenamientoOCI(BaseModel):
    """Ubicación del paquete en OCI Object Storage.

    El paquete guardado lleva `bucket` y `ruta_objeto`. El `status` de la subida
    solo se conoce después, así que es opcional en el archivo y lo completa la
    respuesta de la subida.
    """

    bucket: str
    ruta_objeto: str
    status: str | None = None


class PaqueteDistribucion(BaseModel):
    """Paquete de distribución: resumen, análisis, activos y ubicación en OCI."""

    status: str
    mensaje_error: str | None = None
    resumen_comunidad: ResumenComunidad
    analisis_interacciones: list[AnalisisInteraccion]
    activos_distribucion_generados: ActivosDistribucion
    almacenamiento_oci: AlmacenamientoOCI

    @model_validator(mode="after")
    def _exigir_mensaje_cuando_falla(self) -> "PaqueteDistribucion":
        if self.status == "error" and not self.mensaje_error:
            raise ValueError("si 'status' es 'error', 'mensaje_error' es obligatorio")
        return self
