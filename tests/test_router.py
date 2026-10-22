"""Pruebas del router por tipo y sentimiento."""

from communitylab.config import PESOS_PUNTUACION, TIPOS_APOYO, TIPOS_FAQ, TIPOS_LINKEDIN
from communitylab.modelos import InteraccionAnalizada, PuntuacionRelevancia, Ruta, Sentimiento
from communitylab.router import asignar_ruta


def _interaccion(tipo, sentimiento, final=80):
    return InteraccionAnalizada(
        autor="Persona",
        canal="#general",
        tipo=tipo,
        texto="Texto",
        sentimiento=sentimiento,
        temas=["tema"],
        puntuacion=PuntuacionRelevancia(
            subpuntuaciones={
                "relevancia_comunidad": 80,
                "impacto_publicable": 70,
                "claridad": 60,
                "novedad": 50,
            },
            pesos=PESOS_PUNTUACION,
            puntuacion_final=final,
        ),
        motivo_puntuacion="motivo",
    )


def test_tipos_config_alineados_con_el_router():
    assert TIPOS_LINKEDIN == ("testimonio", "logro")
    assert TIPOS_FAQ == ("pregunta_tecnica", "duda")
    assert TIPOS_APOYO == ("alerta_apoyo", "dificultades")


def test_testimonio_positivo_va_a_linkedin():
    assert asignar_ruta(_interaccion("testimonio", Sentimiento.POSITIVO)) is Ruta.POST_LINKEDIN


def test_logro_muy_positivo_va_a_linkedin():
    assert asignar_ruta(_interaccion("logro", Sentimiento.MUY_POSITIVO)) is Ruta.POST_LINKEDIN


def test_testimonio_neutro_no_va_a_linkedin():
    assert asignar_ruta(_interaccion("testimonio", Sentimiento.NEUTRO)) is Ruta.SIN_ACTIVO


def test_logro_negativo_no_va_a_linkedin():
    assert asignar_ruta(_interaccion("logro", Sentimiento.NEGATIVO)) is Ruta.SIN_ACTIVO


def test_pregunta_tecnica_va_a_faq():
    assert asignar_ruta(_interaccion("pregunta_tecnica", Sentimiento.NEUTRO)) is Ruta.FAQ


def test_duda_va_a_faq():
    assert asignar_ruta(_interaccion("duda", Sentimiento.NEUTRO)) is Ruta.FAQ


def test_alerta_apoyo_tiene_prioridad_sobre_muy_positivo():
    assert asignar_ruta(_interaccion("alerta_apoyo", Sentimiento.MUY_POSITIVO)) is Ruta.APOYO


def test_dificultades_van_a_apoyo():
    assert asignar_ruta(_interaccion("dificultades", Sentimiento.NEGATIVO)) is Ruta.APOYO


def test_otro_tipo_positivo_va_a_linkedin():
    assert asignar_ruta(_interaccion("agradecimiento", Sentimiento.MUY_POSITIVO)) is Ruta.POST_LINKEDIN


def test_otro_tipo_positivo_va_a_sin_activo():
    assert asignar_ruta(_interaccion("agradecimiento", Sentimiento.POSITIVO)) is Ruta.SIN_ACTIVO


def test_otro_tipo_neutro_va_a_sin_activo():
    assert asignar_ruta(_interaccion("sugerencia", Sentimiento.NEUTRO)) is Ruta.SIN_ACTIVO
