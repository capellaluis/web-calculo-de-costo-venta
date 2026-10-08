"""Pruebas de Ventas / pedidos."""

from decimal import Decimal

import app as appmod
from services.fabricados import guardar_fabricado
from services.ventas import (
    cambiar_estado,
    guardar_pedido,
    leer_pedido,
    resumen_periodo,
)


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def sembrar(con):
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
    fabricado = guardar_fabricado(con, None, {
        "nombre": "Tequeños", "receta_id": receta,
        "cantidad_fabricada": Decimal("20"), "notas": ""},
        [{"nombre": "x6", "cantidad_unidades": Decimal("6")}])
    presentacion = con.execute(
        "SELECT id FROM presentaciones WHERE producto_fabricado_id = ?",
        (fabricado,)).fetchone()["id"]
    return presentacion, fabricado


def _datos(canal="tienda"):
    return {"fecha": "2026-01-10", "canal": canal, "cliente_nombre": "Ana",
            "forma_pago": "Efectivo", "descuento": Decimal("0"), "estado": "nuevo",
            "notas": ""}


def test_pedido_total_y_ganancia(con):
    presentacion, fabricado = sembrar(con)
    pedido_id = guardar_pedido(con, None, _datos(), [{
        "presentacion_id": presentacion, "producto_fabricado_id": fabricado,
        "descripcion": "Tequeños x6", "cantidad": Decimal("2"),
        "precio_unitario": Decimal("2083")}])

    calculo = leer_pedido(con, pedido_id)
    assert calculo["total"] == 4166                       # 2083 x 2
    assert calculo["ganancia"] == Decimal("1250")          # (2083-1458) x 2


def test_resumen_ignora_cancelados(con):
    presentacion, fabricado = sembrar(con)
    pedido_id = guardar_pedido(con, None, _datos(), [{
        "presentacion_id": presentacion, "producto_fabricado_id": fabricado,
        "descripcion": "Tequeños x6", "cantidad": Decimal("1"),
        "precio_unitario": Decimal("2083")}])

    resumen = resumen_periodo(con, "2026-01-01", "2026-01-31")
    assert resumen["total"] == 2083
    assert resumen["cantidad"] == 1

    cambiar_estado(con, pedido_id, "cancelado")
    resumen = resumen_periodo(con, "2026-01-01", "2026-01-31")
    assert resumen["cantidad"] == 0


def test_rutas_ventas(db_temporal, con):
    presentacion, _ = sembrar(con)
    cliente = appmod.app.test_client()
    assert cliente.get("/ventas/").status_code == 200

    respuesta = cliente.post("/ventas/nuevo", data={
        "fecha": "2026-01-10", "canal": "tienda", "cliente_nombre": "Ana",
        "forma_pago": "Efectivo", "descuento": "", "estado": "nuevo", "notas": "",
        "presentacion_id": [str(presentacion)], "cantidad": ["2"],
        "precio_unitario": ["2083"]})
    assert respuesta.status_code == 302

    pedido_id = con.execute("SELECT id FROM pedidos").fetchone()[0]
    assert cliente.get("/ventas/%d" % pedido_id).status_code == 200


# FIN tests/test_ventas.py
