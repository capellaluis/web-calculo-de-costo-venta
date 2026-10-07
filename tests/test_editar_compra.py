"""Pruebas de edición de compras."""

from decimal import Decimal

import app as appmod
from services.compras import actualizar_compra, registrar_compra


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def crear_proveedor(con, nombre):
    proveedor = con.execute(
        "INSERT INTO proveedores (nombre) VALUES (?)", (nombre,)).lastrowid
    con.commit()
    return proveedor


def crear_producto(con, nombre):
    producto = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id)"
        " VALUES (?, ?, ?)", (nombre, uid(con, "kg"), uid(con, "g"))).lastrowid
    con.commit()
    return producto


def precio_actual(con, producto_id):
    return con.execute(
        "SELECT precio_actual FROM productos WHERE id = ?", (producto_id,)).fetchone()[0]


def test_editar_cambia_precio_proveedor_y_agrega_producto(con):
    sur = crear_proveedor(con, "Sur")
    norte = crear_proveedor(con, "Norte")
    azucar = crear_producto(con, "Azúcar")
    harina = crear_producto(con, "Harina")
    kg = uid(con, "kg")

    compra = registrar_compra(sur, "2026-01-10", "A-1", "", [
        {"producto_id": azucar, "cantidad": Decimal("25"),
         "unidad_id": kg, "precio_total": Decimal("30000")}])
    assert precio_actual(con, azucar) == 1200

    actualizar_compra(compra, norte, "2026-01-10", "A-1", "", [
        {"producto_id": azucar, "cantidad": Decimal("1"),
         "unidad_id": kg, "precio_total": Decimal("1350")},
        {"producto_id": harina, "cantidad": Decimal("1"),
         "unidad_id": kg, "precio_total": Decimal("500")},
    ])

    assert precio_actual(con, azucar) == 1350      # se recalculó al nuevo precio
    assert precio_actual(con, harina) == 500       # producto agregado

    cabecera = con.execute(
        "SELECT proveedor_id, total FROM compras WHERE id = ?", (compra,)).fetchone()
    assert cabecera["proveedor_id"] == norte       # cambió el proveedor
    assert cabecera["total"] == 1850

    filas_historial = con.execute(
        "SELECT COUNT(*) FROM historial_precios WHERE producto_id = ?",
        (azucar,)).fetchone()[0]
    assert filas_historial == 1                    # el registro viejo se reemplazó


def test_editar_cambia_la_unidad_de_medida(con):
    proveedor = crear_proveedor(con, "Sur")
    azucar = crear_producto(con, "Azúcar")  # se compra por kg
    g = uid(con, "g")

    compra = registrar_compra(proveedor, "2026-01-10", "", "", [
        {"producto_id": azucar, "cantidad": Decimal("25"),
         "unidad_id": uid(con, "kg"), "precio_total": Decimal("30000")}])

    # Ahora se cargan 500 g por $600 -> $1.200/kg
    actualizar_compra(compra, proveedor, "2026-01-10", "", "", [
        {"producto_id": azucar, "cantidad": Decimal("500"),
         "unidad_id": g, "precio_total": Decimal("600")}])

    assert precio_actual(con, azucar) == 1200
    detalle = con.execute(
        "SELECT unidad_id FROM detalle_compras WHERE compra_id = ?", (compra,)).fetchone()
    assert detalle["unidad_id"] == g


def test_ruta_editar_compra(db_temporal, con):
    proveedor = crear_proveedor(con, "Sur")
    azucar = crear_producto(con, "Azúcar")
    compra = registrar_compra(proveedor, "2026-01-10", "A-1", "", [
        {"producto_id": azucar, "cantidad": Decimal("1"),
         "unidad_id": uid(con, "kg"), "precio_total": Decimal("1000")}])

    cliente = appmod.app.test_client()
    # El formulario de edición se abre
    assert cliente.get("/compras/%d/editar" % compra).status_code == 200

    respuesta = cliente.post("/compras/%d/editar" % compra, data={
        "proveedor_id": str(proveedor),
        "fecha": "2026-01-10",
        "numero_documento": "A-1",
        "observaciones": "",
        "producto_id": [str(azucar)],
        "cantidad": ["2"],
        "unidad_id": [str(uid(con, "kg"))],
        "precio_total": ["2400"],
    })
    assert respuesta.status_code == 302
    assert precio_actual(con, azucar) == 1200


# FIN tests/test_editar_compra.py
