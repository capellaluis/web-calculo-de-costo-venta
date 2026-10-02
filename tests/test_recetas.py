"""Pruebas de costos de recetas (sección 6.3 del resumen)."""

from decimal import Decimal

import pytest

from services.recetas import (
    ErrorReceta,
    calcular_receta,
    costo_linea,
    costo_receta,
    validar_ingredientes,
)


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def crear_producto(con, nombre, compra, uso, precio):
    return con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id, precio_actual)"
        " VALUES (?, ?, ?, ?)",
        (nombre, uid(con, compra), uid(con, uso), precio)).lastrowid


def crear_receta(con, nombre, rendimiento_cantidad, rendimiento_unidad="vasos"):
    return con.execute(
        "INSERT INTO recetas (nombre, rendimiento_cantidad, rendimiento_unidad)"
        " VALUES (?, ?, ?)",
        (nombre, rendimiento_cantidad, rendimiento_unidad)).lastrowid


def agregar_ingrediente(con, receta_id, producto_id, cantidad, unidad):
    con.execute(
        "INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad_id)"
        " VALUES (?, ?, ?, ?)",
        (receta_id, producto_id, cantidad, uid(con, unidad)))


def test_costo_linea_convierte_gramos_a_kilogramo(con):
    kg = con.execute("SELECT * FROM unidades WHERE abreviatura = 'kg'").fetchone()
    g = con.execute("SELECT * FROM unidades WHERE abreviatura = 'g'").fetchone()
    assert costo_linea(300, g, kg, 1350) == Decimal("405")


def test_receta_chicha_y_recalculo_al_cambiar_el_precio(con):
    maiz = crear_producto(con, "Maíz", "kg", "g", 200)
    azucar = crear_producto(con, "Azúcar", "kg", "g", 1200)
    leche = crear_producto(con, "Leche", "l", "ml", 1000)
    canela = crear_producto(con, "Canela", "kg", "g", 8000)

    receta_id = crear_receta(con, "Chicha", 10)
    agregar_ingrediente(con, receta_id, maiz, 500, "g")
    agregar_ingrediente(con, receta_id, azucar, 300, "g")
    agregar_ingrediente(con, receta_id, leche, 1, "l")
    agregar_ingrediente(con, receta_id, canela, 10, "g")
    con.commit()

    calculo = calcular_receta(con, receta_id)
    assert calculo["total"] == Decimal("1540")
    assert calculo["costo_unidad"] == Decimal("154")

    # Sube el azúcar: el costo se recalcula solo (no hay costo guardado).
    con.execute("UPDATE productos SET precio_actual = 1500 WHERE id = ?", (azucar,))
    con.commit()

    total, por_unidad = costo_receta(con, receta_id)
    assert total == Decimal("1630")
    assert por_unidad == Decimal("163")


def test_receta_inexistente(con):
    with pytest.raises(ErrorReceta):
        calcular_receta(con, 999)


def test_validar_ingredientes_unidad_incompatible(con):
    producto = crear_producto(con, "Azúcar", "kg", "g", 1200)
    error = validar_ingredientes(con, [
        {"producto_id": producto, "cantidad": Decimal("1"), "unidad_id": uid(con, "ml")},
    ])
    assert error is not None
    assert "no es compatible" in error


def test_validar_ingredientes_ok(con):
    producto = crear_producto(con, "Azúcar", "kg", "g", 1200)
    error = validar_ingredientes(con, [
        {"producto_id": producto, "cantidad": Decimal("300"), "unidad_id": uid(con, "g")},
    ])
    assert error is None


# FIN tests/test_recetas.py
