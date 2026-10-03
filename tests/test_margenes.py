"""Pruebas de márgenes, gastos y precios de venta."""

from decimal import Decimal

import pytest

from services.margenes import (
    ErrorMargen,
    calcular_precios_venta,
    guardar_margenes,
    leer_margenes,
    leer_redondeo,
    precio_margen_real,
    redondear,
)


def test_margen_real_dividiendo(con):
    # 500 / 0,70 = 714,29 ; 100 / 0,70 = 142,86
    assert precio_margen_real(500, 30).quantize(Decimal("0.01")) == Decimal("714.29")
    assert precio_margen_real(100, 30).quantize(Decimal("0.01")) == Decimal("142.86")


def test_margen_real_mayor_o_igual_a_100(con):
    with pytest.raises(ErrorMargen):
        precio_margen_real(500, 100)


def test_redondeo(con):
    assert redondear(Decimal("382.2"), "entero") == Decimal("382")
    assert redondear(Decimal("499.8"), "entero") == Decimal("500")
    assert redondear(Decimal("382.2"), "centavos") == Decimal("382.20")


def test_calcular_precios_venta_con_gastos(con):
    gastos = [{"nombre": "Gas", "porcentaje": 5},
              {"nombre": "Agua", "porcentaje": 3},
              {"nombre": "Luz", "porcentaje": 4}]
    margenes = leer_margenes(con)  # 30 / 50 / 70

    resultado = calcular_precios_venta(500, gastos, margenes, "entero")
    assert resultado["total_gastos"] == Decimal("60")
    assert resultado["costo_con_gastos"] == Decimal("560")
    # 560 / 0,70 = 800 ; 560 / 0,50 = 1120 ; 560 / 0,30 = 1866,67 -> 1867
    assert [p["precio"] for p in resultado["precios"]] == [
        Decimal("800"), Decimal("1120"), Decimal("1867")]
    assert resultado["precios"][0]["ganancia"] == Decimal("240")
    assert resultado["gastos"][0]["monto"] == Decimal("25")


def test_calcular_sin_gastos(con):
    margenes = leer_margenes(con)
    resultado = calcular_precios_venta(294, [], margenes, "entero")
    assert resultado["costo_con_gastos"] == Decimal("294")
    assert [p["precio"] for p in resultado["precios"]] == [
        Decimal("420"), Decimal("588"), Decimal("980")]


def test_guardar_y_leer_margenes(con):
    guardar_margenes(con, [
        {"numero": 1, "nombre": "Barato", "porcentaje": Decimal("35")},
        {"numero": 2, "nombre": "Medio", "porcentaje": Decimal("55")},
        {"numero": 3, "nombre": "Caro", "porcentaje": Decimal("80")},
    ], "centavos")
    margenes = leer_margenes(con)
    assert [m["nombre"] for m in margenes] == ["Barato", "Medio", "Caro"]
    assert [m["porcentaje"] for m in margenes] == [35, 55, 80]
    assert leer_redondeo(con) == "centavos"


def test_guardar_margen_invalido(con):
    with pytest.raises(ErrorMargen):
        guardar_margenes(con, [
            {"numero": 1, "nombre": "A", "porcentaje": Decimal("30")},
            {"numero": 2, "nombre": "B", "porcentaje": Decimal("50")},
            {"numero": 3, "nombre": "C", "porcentaje": Decimal("120")},
        ], "entero")


def test_guardar_negativo(con):
    with pytest.raises(ErrorMargen):
        guardar_margenes(con, [
            {"numero": 1, "nombre": "A", "porcentaje": Decimal("-1")},
            {"numero": 2, "nombre": "B", "porcentaje": Decimal("50")},
            {"numero": 3, "nombre": "C", "porcentaje": Decimal("70")},
        ], "entero")


# FIN tests/test_margenes.py
