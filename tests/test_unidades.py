"""Pruebas de conversión de unidades (sección 6.1 del resumen)."""

from decimal import Decimal

import pytest

from services.unidades import ErrorUnidad, convertir


def unidad(con, abreviatura):
    return con.execute(
        "SELECT * FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()


def test_kg_a_g(con):
    assert convertir(1, unidad(con, "kg"), unidad(con, "g")) == Decimal("1000")


def test_g_a_kg(con):
    assert convertir(300, unidad(con, "g"), unidad(con, "kg")) == Decimal("0.3")


def test_docena_a_unidad(con):
    assert convertir(1, unidad(con, "doc"), unidad(con, "un")) == Decimal("12")


def test_litro_a_ml(con):
    assert convertir(1, unidad(con, "l"), unidad(con, "ml")) == Decimal("1000")


def test_tipos_distintos_falla(con):
    with pytest.raises(ErrorUnidad):
        convertir(1, unidad(con, "kg"), unidad(con, "ml"))


def test_paquete_a_caja_falla(con):
    with pytest.raises(ErrorUnidad):
        convertir(1, unidad(con, "paq"), unidad(con, "caja"))


def test_paquete_a_paquete_ok(con):
    assert convertir(3, unidad(con, "paq"), unidad(con, "paq")) == Decimal("3")


# FIN tests/test_unidades.py
