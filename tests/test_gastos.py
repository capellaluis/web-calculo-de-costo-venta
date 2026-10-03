"""Pruebas de gastos fijos."""

from decimal import Decimal

import pytest

from services.gastos import ErrorGasto, guardar_gastos, leer_gastos, monto


def test_gastos_iniciales(con):
    nombres = [g["nombre"] for g in leer_gastos(con)]
    assert nombres == ["Gas", "Agua", "Luz"]


def test_monto(con):
    assert monto(500, 5) == Decimal("25")
    assert monto(294, 10) == Decimal("29.4")


def test_guardar_gastos_reemplaza(con):
    guardar_gastos(con, [
        {"nombre": "Gas", "porcentaje": Decimal("5")},
        {"nombre": "Alquiler", "porcentaje": Decimal("10")},
    ])
    gastos = leer_gastos(con)
    assert [g["nombre"] for g in gastos] == ["Gas", "Alquiler"]
    assert gastos[1]["porcentaje"] == 10


def test_guardar_gasto_negativo(con):
    with pytest.raises(ErrorGasto):
        guardar_gastos(con, [{"nombre": "Gas", "porcentaje": Decimal("-1")}])


# FIN tests/test_gastos.py
