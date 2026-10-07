"""Pruebas de productos fabricados y precios por producto (Fase 12 + mejora)."""

from decimal import Decimal

import pytest

from services.fabricados import (
    ErrorFabricado,
    calcular_fabricado,
    guardar_config_fabricado,
    guardar_fabricado,
    leer_plantilla,
)


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def crear_receta(con, nombre, precio):
    producto = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id, precio_actual)"
        " VALUES (?, ?, ?, ?)",
        (nombre, uid(con, "kg"), uid(con, "g"), precio)).lastrowid
    receta = con.execute(
        "INSERT INTO recetas (nombre, rendimiento_cantidad, rendimiento_unidad)"
        " VALUES (?, 1, 'lote')", (nombre,)).lastrowid
    con.execute(
        "INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad_id)"
        " VALUES (?, ?, 1000, ?)", (receta, producto, uid(con, "g")))
    con.commit()
    return receta


def crear_tequenos(con):
    receta = crear_receta(con, "Masa", 4860)
    return guardar_fabricado(con, None, {
        "nombre": "Tequeños", "receta_id": receta,
        "cantidad_fabricada": Decimal("20"), "notas": "",
    }, [{"nombre": "x6", "cantidad_unidades": Decimal("6")}])


def config(gastos=None, margen=30, delivery=None):
    return {
        "gastos": gastos if gastos is not None else [],
        "margenes": [
            {"numero": 1, "nombre": "M1", "porcentaje": margen, "elegido": 1},
            {"numero": 2, "nombre": "M2", "porcentaje": 50, "elegido": 0},
            {"numero": 3, "nombre": "M3", "porcentaje": 70, "elegido": 0},
        ],
        "delivery": delivery if delivery is not None else [],
    }


def test_costo_y_precios_por_defecto(con):
    fabricado_id = crear_tequenos(con)
    calculo = calcular_fabricado(con, fabricado_id)
    assert calculo["costo_lote"] == Decimal("4860")
    assert calculo["costo_unidad"] == Decimal("243")

    x6 = calculo["presentaciones"][0]
    assert x6["costo"] == Decimal("1458")
    # margen elegido 30 % -> 1458 / 0,70 = 2082,86 -> 2083
    assert x6["tienda"] == Decimal("2083")


def test_precios_con_gastos_y_delivery(con):
    fabricado_id = crear_tequenos(con)
    guardar_config_fabricado(con, fabricado_id,
                             gastos=[{"nombre": "Gas", "porcentaje": 10}],
                             margenes=config()["margenes"],
                             delivery=[{"nombre": "Comisión", "porcentaje": 5},
                                       {"nombre": "2,9%", "porcentaje": 2.9}])
    x6 = calcular_fabricado(con, fabricado_id)["presentaciones"][0]
    # 1458 * 1,10 = 1603,8 -> /0,70 = 2291,14 -> 2291
    assert x6["con_gastos"] == Decimal("1603.8")
    assert x6["tienda"] == Decimal("2291")
    # delivery = 2291 / (1 - 0,079) = 2291 / 0,921 = 2487,51 -> 2488
    assert x6["delivery"] == Decimal("2488")


def test_cambiar_un_producto_no_afecta_a_otro(con):
    uno = crear_tequenos(con)
    receta_dos = crear_receta(con, "Otra", 4860)
    dos = guardar_fabricado(con, None, {
        "nombre": "Otro", "receta_id": receta_dos,
        "cantidad_fabricada": Decimal("20"), "notas": ""},
        [{"nombre": "x6", "cantidad_unidades": Decimal("6")}])

    guardar_config_fabricado(con, uno, gastos=[{"nombre": "Gas", "porcentaje": 50}],
                             margenes=config()["margenes"], delivery=[])

    # El primero cambió; el segundo sigue con la plantilla (sin gastos).
    assert calcular_fabricado(con, uno)["presentaciones"][0]["con_gastos"] == Decimal("2187")
    assert calcular_fabricado(con, dos)["presentaciones"][0]["con_gastos"] == Decimal("1458")


def test_la_ultima_config_queda_como_plantilla(con):
    fabricado_id = crear_tequenos(con)
    guardar_config_fabricado(con, fabricado_id,
                             gastos=[{"nombre": "Luz", "porcentaje": 7}],
                             margenes=config(margen=40)["margenes"], delivery=[])
    plantilla = leer_plantilla(con)
    assert plantilla["gastos"] == [{"nombre": "Luz", "porcentaje": 7}]
    assert plantilla["margenes"][0]["porcentaje"] == 40

    # Un producto nuevo sin guardar usa esa plantilla.
    receta = crear_receta(con, "Nueva", 4860)
    nuevo = guardar_fabricado(con, None, {
        "nombre": "Nuevo", "receta_id": receta,
        "cantidad_fabricada": Decimal("20"), "notas": ""},
        [{"nombre": "x6", "cantidad_unidades": Decimal("6")}])
    x6 = calcular_fabricado(con, nuevo)["presentaciones"][0]
    # 1458 * 1,07 = 1560,06 -> / (1-0,40) = 2600,1 -> 2600
    assert x6["tienda"] == Decimal("2600")


def test_validaciones(con):
    receta = crear_receta(con, "Masa", 4860)
    with pytest.raises(ErrorFabricado):
        guardar_fabricado(con, None, {"nombre": "", "receta_id": receta,
                                      "cantidad_fabricada": Decimal("20"), "notas": ""}, [])
    with pytest.raises(ErrorFabricado):
        guardar_fabricado(con, None, {"nombre": "X", "receta_id": receta,
                                      "cantidad_fabricada": Decimal("0"), "notas": ""}, [])


# FIN tests/test_fabricados.py
