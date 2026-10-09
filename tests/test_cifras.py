"""Pruebas de la validación de cifras de los activos (sin LLM)."""

from communitylab.generadores.comun import extraer_cifras, validar_cifras

ORIGEN = "¿Cómo depuro una consulta que no devuelve resultados?"


def test_lista_numerada_no_dispara_el_error():
    activo = (
        "1. Revisa el filtro de la consulta.\n"
        "2. Quita las condiciones una por una.\n"
        "3. Comprueba la conexión."
    )

    assert validar_cifras(activo, ORIGEN) is None


def test_cifra_inventada_en_la_misma_linea_si_dispara():
    activo = "1. Revisa el filtro; repite esto un 40 por ciento de las veces."

    error = validar_cifras(activo, ORIGEN)

    assert error is not None
    assert "40" in str(error)


def test_cifra_presente_en_el_origen_pasa():
    origen = "El error aparece 3 veces al día."
    activo = "1. Revisa el filtro.\n2. Si aparece 3 veces, cambia de estrategia."

    assert validar_cifras(activo, origen) is None


def test_cifra_mid_linea_sin_marcador_sigue_exigiendo_presencia():
    assert validar_cifras("Sigue el paso 3 con calma.", ORIGEN) is not None


def test_cifra_no_pasa_por_estar_dentro_de_otra_cifra():
    origen = "Hay 13 recursos y el año 2026 fue clave."
    activo = "1. Revisa el paso 3 con calma."

    error = validar_cifras(activo, origen)

    assert error is not None
    assert "3" in str(error)


def test_extraer_cifras_ignora_solo_los_marcadores_de_lista():
    texto = "1. Revisa el paso 3.\n2) Repite 40 veces."

    assert extraer_cifras(texto) == {"3", "40"}
