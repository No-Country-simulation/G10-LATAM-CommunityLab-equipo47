"""Pruebas del cálculo de la puntuación de relevancia (puro, sin LLM)."""

import pytest

from communitylab.analisis import ErrorAnalisis, calcular_puntuacion
from communitylab.config import PESOS_PUNTUACION


def _subs(relevancia, impacto, claridad, novedad):
    return {
        "relevancia_comunidad": relevancia,
        "impacto_publicable": impacto,
        "claridad": claridad,
        "novedad": novedad,
    }


def test_los_pesos_suman_uno():
    assert sum(PESOS_PUNTUACION.values()) == pytest.approx(1.0)


def test_puntuacion_maxima():
    resultado = calcular_puntuacion(_subs(100, 100, 100, 100))

    assert resultado.puntuacion_final == 100
    assert resultado.pesos == PESOS_PUNTUACION


def test_puntuacion_minima():
    assert calcular_puntuacion(_subs(0, 0, 0, 0)).puntuacion_final == 0


def test_puntuacion_ponderada():
    # 90*0.4 + 80*0.3 + 70*0.2 + 60*0.1 = 80
    assert calcular_puntuacion(_subs(90, 80, 70, 60)).puntuacion_final == 80


def test_conserva_las_subpuntuaciones():
    resultado = calcular_puntuacion(_subs(90, 80, 70, 60))

    assert resultado.subpuntuaciones["relevancia_comunidad"] == 90
    assert resultado.subpuntuaciones["novedad"] == 60


def test_falta_una_subpuntuacion_lanza_error():
    incompleto = {"relevancia_comunidad": 90, "impacto_publicable": 80, "claridad": 70}

    with pytest.raises(ErrorAnalisis):
        calcular_puntuacion(incompleto)
