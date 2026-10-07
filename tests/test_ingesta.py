"""Pruebas de lectura y validación de lotes de interacciones."""

import json
from pathlib import Path

import pytest

from communitylab.ingesta import ErrorIngesta, leer_lote_json, leer_lotes

RAIZ = Path(__file__).resolve().parents[1]
CARPETA_ENTRADA = RAIZ / "data" / "entrada"


def _lote_valido(**cambios) -> dict:
    datos = {
        "origen_comunidad": "Comunidad_Test",
        "periodo_referencia": "Semana_01_Sprints",
        "interacciones": [
            {
                "autor": "Persona Test",
                "canal": "#general",
                "tipo": "testimonio",
                "texto": "Un texto de prueba.",
            }
        ],
    }
    datos.update(cambios)
    return datos


def test_lee_los_tres_lotes_de_ejemplo():
    lotes = leer_lotes(CARPETA_ENTRADA)

    assert len(lotes) == 3
    assert all(len(lote.interacciones) == 3 for lote in lotes)
    assert all(lote.origen_comunidad for lote in lotes)
    assert all(lote.periodo_referencia for lote in lotes)


def test_primer_lote_conserva_origen_y_autores():
    lote = leer_lote_json(CARPETA_ENTRADA / "ejemplo_1_contratacion.json")

    assert lote.origen_comunidad == "Discord_ONE_LATAM"
    assert lote.periodo_referencia == "Semana_04_Sprints"
    assert lote.interacciones[0].autor == "Mariana Souza"
    assert lote.interacciones[0].pais == "Colombia"


def test_tipo_desconocido_no_rompe_la_ingesta(tmp_path):
    ruta = tmp_path / "lote.json"
    ruta.write_text(
        json.dumps(_lote_valido(interacciones=[{
            "autor": "Nueva",
            "canal": "#novedades",
            "tipo": "tipo_inventado",
            "texto": "Un tipo que no está en la lista conocida.",
        }])),
        encoding="utf-8",
    )

    lote = leer_lote_json(ruta)

    assert lote.interacciones[0].tipo == "tipo_inventado"


def test_archivo_inexistente_lanza_error_claro():
    with pytest.raises(ErrorIngesta):
        leer_lote_json(CARPETA_ENTRADA / "no_existe.json")


def test_json_invalido_lanza_error_claro(tmp_path):
    ruta = tmp_path / "roto.json"
    ruta.write_text("{ esto no es json", encoding="utf-8")

    with pytest.raises(ErrorIngesta):
        leer_lote_json(ruta)


def test_lote_sin_interacciones_lanza_error(tmp_path):
    ruta = tmp_path / "vacio.json"
    ruta.write_text(json.dumps(_lote_valido(interacciones=[])), encoding="utf-8")

    with pytest.raises(ErrorIngesta):
        leer_lote_json(ruta)


def test_directorio_inexistente_lanza_error(tmp_path):
    with pytest.raises(ErrorIngesta):
        leer_lotes(tmp_path / "no_existe")
