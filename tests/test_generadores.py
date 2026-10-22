"""Pruebas de los generadores por canal con el LLM simulado (sin red)."""

from types import SimpleNamespace

import pytest
from langchain_google_genai.chat_models import GoogleRateLimitError

from communitylab.config import (
    Configuracion,
    PESOS_PUNTUACION,
    STATUS_FAQ,
)
from communitylab.generadores import (
    ErrorGeneracion,
    elegir_para_faq,
    elegir_para_linkedin,
    generar_faq,
    generar_post_linkedin,
)
from communitylab.modelos import (
    EstadoAprobacion,
    InformeAnalisis,
    InteraccionAnalizada,
    MetadatosInforme,
    PostLinkedIn,
    PostLinkedInLlm,
    PuntuacionRelevancia,
    Sentimiento,
    SugerenciaContenidoFaq,
    SugerenciaContenidoFaqLlm,
)

CONFIG = Configuracion(
    gemini_api_key="clave-falsa",
    oci_namespace="namespace-test",
    oci_bucket="bucket-test",
    gemini_model="gemini-3.5-flash-lite",
)

_NOP = lambda _segundos: None  # noqa: E731

_COPY_VALIDO = (
    "En nuestra comunidad celebramos cada avance y hoy queremos compartir una historia que nos motiva a seguir. "
    "Una persona construyó su proyecto con esfuerzo, aprendió a resolver problemas reales y lo presentó con confianza. "
    "Ese recorrido nos recuerda que el aprendizaje constante abre oportunidades y que nadie camina solo en este proceso. "
    "Gracias por inspirarnos y por demostrar de lo que somos capaces cuando trabajamos en equipo.\n\n"
    "#ComunidadTech #Aprendizaje #Logros"
)


def _subs(relevancia=90, impacto=85, claridad=80, novedad=70):
    return {
        "relevancia_comunidad": relevancia,
        "impacto_publicable": impacto,
        "claridad": claridad,
        "novedad": novedad,
    }


def _interaccion(
    *,
    autor="Paula Iriarte",
    canal="#historias",
    tipo="testimonio",
    sentimiento=Sentimiento.MUY_POSITIVO,
    texto="Presenté mi primer proyecto en una entrevista y me fue muy bien.",
    final=90,
    subs=None,
) -> InteraccionAnalizada:
    return InteraccionAnalizada(
        autor=autor,
        canal=canal,
        tipo=tipo,
        texto=texto,
        sentimiento=sentimiento,
        temas=["tema"],
        puntuacion=PuntuacionRelevancia(
            subpuntuaciones=subs or _subs(),
            pesos=PESOS_PUNTUACION,
            puntuacion_final=final,
        ),
        motivo_puntuacion="motivo",
    )


def _informe(interacciones) -> InformeAnalisis:
    return InformeAnalisis(
        origen_comunidad="Comunidad_Test",
        periodo_referencia="Semana_01",
        total_interacciones_procesadas=len(interacciones),
        sentimiento_predominante=Sentimiento.MUY_POSITIVO,
        temas_principales=["tema"],
        interacciones=interacciones,
        metadatos=MetadatosInforme(
            modelo="gemini-3.5-flash-lite", version_prompt="v", desde_cache=False
        ),
    )


def _raw(finish="STOP"):
    return SimpleNamespace(content="{}", response_metadata={"finish_reason": finish})


def _post_llm(copy=None, titulo="Un logro real") -> PostLinkedInLlm:
    return PostLinkedInLlm(
        titulo=titulo,
        copy=copy or _COPY_VALIDO,
        canal_recomendado="LinkedIn Oficial",
        potencial_engagement="Alto",
    )


def _ok(copy=None, finish="STOP"):
    return {"raw": _raw(finish), "parsed": _post_llm(copy), "parsing_error": None}


def _faq_llm(
    tema="Cómo depurar una consulta",
    pregunta="¿Qué reviso primero?",
    respuesta="Empieza por el filtro de la consulta y luego revisa la conexión.",
) -> SugerenciaContenidoFaqLlm:
    return SugerenciaContenidoFaqLlm(tema=tema, pregunta=pregunta, respuesta_sugerida=respuesta)


def _ok_faq(finish="STOP"):
    return {"raw": _raw(finish), "parsed": _faq_llm(), "parsing_error": None}


class FakeLlm:
    """LLM simulado: devuelve respuestas prefijadas y cuenta las llamadas."""

    def __init__(self, resultados):
        self._resultados = list(resultados)
        self.llamadas = 0

    def invoke(self, mensajes):  # noqa: ARG002
        self.llamadas += 1
        if not self._resultados:
            raise AssertionError("el LLM no debería haberse llamado")
        resultado = self._resultados.pop(0)
        if isinstance(resultado, Exception):
            raise resultado
        return resultado


# --- LinkedIn -----------------------------------------------------------------

def test_genera_post_linkedin_pendiente(tmp_path):
    interaccion = _interaccion()
    llm = FakeLlm([_ok()])

    post = generar_post_linkedin(
        interaccion, _informe([interaccion]), CONFIG, llm=llm, directorio_cache=tmp_path, dormir=_NOP
    )

    assert isinstance(post, PostLinkedIn)
    assert post.estado_aprobacion is EstadoAprobacion.PENDIENTE
    assert llm.llamadas == 1


def test_linkedin_usa_cache_sin_llamar(tmp_path):
    interaccion = _interaccion()
    informe = _informe([interaccion])

    generar_post_linkedin(
        interaccion, informe, CONFIG, llm=FakeLlm([_ok()]), directorio_cache=tmp_path, dormir=_NOP
    )
    llm_prohibido = FakeLlm([])
    post = generar_post_linkedin(
        interaccion, informe, CONFIG, llm=llm_prohibido, directorio_cache=tmp_path, dormir=_NOP
    )

    assert llm_prohibido.llamadas == 0
    assert isinstance(post, PostLinkedIn)


def test_linkedin_copy_largo_repara(tmp_path):
    interaccion = _interaccion()
    largo = "x" * 1400 + "\n\n#ComunidadTech #Aprendizaje #Logros"
    llm = FakeLlm([_ok(copy=largo), _ok()])

    generar_post_linkedin(
        interaccion, _informe([interaccion]), CONFIG, llm=llm, directorio_cache=tmp_path, dormir=_NOP
    )

    assert llm.llamadas == 2


def test_linkedin_hashtags_cortados_reparan(tmp_path):
    interaccion = _interaccion()
    cortado = _COPY_VALIDO.replace("#Logros", "#")
    llm = FakeLlm([_ok(copy=cortado), _ok()])

    generar_post_linkedin(
        interaccion, _informe([interaccion]), CONFIG, llm=llm, directorio_cache=tmp_path, dormir=_NOP
    )

    assert llm.llamadas == 2


def test_linkedin_cifra_inventada_repara(tmp_path):
    interaccion = _interaccion()  # su texto no contiene ninguna cifra
    con_cifra = _COPY_VALIDO.replace("Gracias por", "Un 40 por ciento más de avance. Gracias por")
    llm = FakeLlm([_ok(copy=con_cifra), _ok()])

    generar_post_linkedin(
        interaccion, _informe([interaccion]), CONFIG, llm=llm, directorio_cache=tmp_path, dormir=_NOP
    )

    assert llm.llamadas == 2


def test_linkedin_truncado_repara(tmp_path):
    interaccion = _interaccion()
    llm = FakeLlm([_ok(finish="MAX_TOKENS"), _ok()])

    generar_post_linkedin(
        interaccion, _informe([interaccion]), CONFIG, llm=llm, directorio_cache=tmp_path, dormir=_NOP
    )

    assert llm.llamadas == 2


def test_linkedin_reparacion_agotada(tmp_path):
    interaccion = _interaccion()
    llm = FakeLlm([_ok(finish="MAX_TOKENS"), _ok(finish="MAX_TOKENS")])

    with pytest.raises(ErrorGeneracion):
        generar_post_linkedin(
            interaccion, _informe([interaccion]), CONFIG, llm=llm, directorio_cache=tmp_path, dormir=_NOP
        )

    assert llm.llamadas == 2


def test_linkedin_sin_interaccion_avisa():
    with pytest.raises(ErrorGeneracion):
        generar_post_linkedin(None, _informe([]), CONFIG)


# --- FAQ ----------------------------------------------------------------------

def test_genera_faq_con_campos_de_codigo(tmp_path):
    interaccion = _interaccion(
        tipo="pregunta_tecnica",
        sentimiento=Sentimiento.NEUTRO,
        texto="¿Cómo depuro una consulta que no devuelve resultados?",
    )
    llm = FakeLlm([_ok_faq()])

    faq = generar_faq(
        interaccion, _informe([interaccion]), CONFIG, llm=llm, directorio_cache=tmp_path, dormir=_NOP
    )

    assert isinstance(faq, SugerenciaContenidoFaq)
    assert faq.estado_aprobacion is EstadoAprobacion.PENDIENTE
    assert faq.status == STATUS_FAQ
    assert faq.origen == "Duda planteada por Paula Iriarte en #historias"
    assert llm.llamadas == 1


def test_faq_repara_por_cifra(tmp_path):
    interaccion = _interaccion(
        tipo="pregunta_tecnica",
        sentimiento=Sentimiento.NEUTRO,
        texto="¿Cómo depuro una consulta que no devuelve resultados?",
    )
    con_cifra = _faq_llm(respuesta="Revisa los 3 pasos de depuración.")
    llm = FakeLlm([{"raw": _raw(), "parsed": con_cifra, "parsing_error": None}, _ok_faq()])

    generar_faq(
        interaccion, _informe([interaccion]), CONFIG, llm=llm, directorio_cache=tmp_path, dormir=_NOP
    )

    assert llm.llamadas == 2


def test_faq_sin_interaccion_avisa():
    with pytest.raises(ErrorGeneracion):
        generar_faq(None, _informe([]), CONFIG)


# --- Selección ----------------------------------------------------------------

def test_seleccion_faq_prefiere_la_duda():
    testimonio = _interaccion(final=95)
    duda = _interaccion(tipo="pregunta_tecnica", sentimiento=Sentimiento.NEUTRO, final=78)
    informe = _informe([testimonio, duda])

    assert elegir_para_linkedin(informe) is testimonio
    assert elegir_para_faq(informe) is duda


def test_seleccion_devuelve_none_sin_candidatas():
    solo_duda = _informe([_interaccion(tipo="pregunta_tecnica", sentimiento=Sentimiento.NEUTRO)])
    solo_testimonio = _informe([_interaccion()])

    assert elegir_para_linkedin(solo_duda) is None
    assert elegir_para_faq(solo_testimonio) is None


# --- 429 ----------------------------------------------------------------------

def test_429_con_espera_larga_falla_de_inmediato(tmp_path):
    interaccion = _interaccion()
    llm = FakeLlm([
        GoogleRateLimitError(
            "429 RESOURCE_EXHAUSTED. {'error': {'details': "
            "[{'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '120s'}]}}"
        ),
        _ok(),
    ])

    with pytest.raises(ErrorGeneracion) as info:
        generar_post_linkedin(
            interaccion, _informe([interaccion]), CONFIG, llm=llm, directorio_cache=tmp_path, dormir=_NOP
        )

    assert llm.llamadas == 1  # no gasta reintentos
    assert "Cuota" in str(info.value)
