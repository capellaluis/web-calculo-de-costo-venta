"""Pruebas de productos fabricados (Fase 12)."""

from decimal import Decimal

import pytest

from services.fabricados import (
    ErrorFabricado,
    calcular_fabricado,
    guardar_fabricado,
)
from services.gastos import leer_gastos
from services.margenes import leer_margenes


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def crear_receta_costo_4860(con):
    producto = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id, precio_actual)"
        " VALUES ('Masa', ?, ?, 4860)", (uid(con, "kg"), uid(con, "g"))).lastrowid
    receta = con.execute(
        "INSERT INTO recetas (nombre, rendimiento_cantidad, rendimiento_unidad)"
        " VALUES ('Tequeños', 1, 'lote')").lastrowid
    con.execute(
        "INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad_id)"
        " VALUES (?, ?, 1000, ?)", (receta, producto, uid(con, "g")))
    con.commit()
    return receta


def test_guardar_y_calcular_tequenos(con):
    receta = crear_receta_costo_4860(con)
    fabricado_id = guardar_fabricado(con, None, {
        "nombre": "Tequeños", "receta_id": receta,
        "cantidad_fabricada": Decimal("20"), "notas": "",
    }, [
        {"nombre": "x6", "cantidad_unidades": Decimal("6")},
        {"nombre": "x12", "cantidad_unidades": Decimal("12")},
    ])

    calculo = calcular_fabricado(con, fabricado_id, leer_gastos(con), leer_margenes(con))
    assert calculo["costo_lote"] == Decimal("4860")
    assert calculo["costo_unidad"] == Decimal("243")

    x6 = calculo["presentaciones"][0]
    assert x6["costo"] == Decimal("1458")
    # 1458 / 0,70 = 2082,86 -> 2083 ; /0,50 = 2916 ; /0,30 = 4860
    assert [p["precio"] for p in x6["precio"]["precios"]] == [
        Decimal("2083"), Decimal("2916"), Decimal("4860")]


def test_validaciones(con):
    receta = crear_receta_costo_4860(con)
    with pytest.raises(ErrorFabricado):
        guardar_fabricado(con, None, {
            "nombre": "", "receta_id": receta,
            "cantidad_fabricada": Decimal("20"), "notas": ""}, [])
    with pytest.raises(ErrorFabricado):
        guardar_fabricado(con, None, {
            "nombre": "X", "receta_id": receta,
            "cantidad_fabricada": Decimal("0"), "notas": ""}, [])
    with pytest.raises(ErrorFabricado):
        guardar_fabricado(con, None, {
            "nombre": "X", "receta_id": receta,
            "cantidad_fabricada": Decimal("20"), "notas": ""},
            [{"nombre": "x0", "cantidad_unidades": Decimal("0")}])


def test_editar_reemplaza_presentaciones(con):
    receta = crear_receta_costo_4860(con)
    fabricado_id = guardar_fabricado(con, None, {
        "nombre": "Tequeños", "receta_id": receta,
        "cantidad_fabricada": Decimal("20"), "notas": ""},
        [{"nombre": "x6", "cantidad_unidades": Decimal("6")}])

    guardar_fabricado(con, fabricado_id, {
        "nombre": "Tequeños", "receta_id": receta,
        "cantidad_fabricada": Decimal("20"), "notas": ""},
        [{"nombre": "x12", "cantidad_unidades": Decimal("12")},
         {"nombre": "x20", "cantidad_unidades": Decimal("20")}])

    calculo = calcular_fabricado(con, fabricado_id)
    assert [p["nombre"] for p in calculo["presentaciones"]] == ["x12", "x20"]


# FIN tests/test_fabricados.py
