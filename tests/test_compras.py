"""Pruebas del registro y la eliminación de compras (sección 6.2 del resumen)."""

from decimal import Decimal

import pytest

from services.compras import ErrorCompra, eliminar_compra, registrar_compra


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def crear_proveedor(con, nombre="Distribuidora Sur"):
    cursor = con.execute("INSERT INTO proveedores (nombre) VALUES (?)", (nombre,))
    con.commit()
    return cursor.lastrowid


def crear_producto(con, nombre="Azúcar", compra="kg", uso="g", precio=0):
    uc = uid(con, compra)
    uu = uid(con, uso)
    cursor = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id, precio_actual)"
        " VALUES (?, ?, ?, ?)", (nombre, uc, uu, precio))
    con.commit()
    return cursor.lastrowid, uc, uu


def precio_actual(con, producto_id):
    return con.execute(
        "SELECT precio_actual FROM productos WHERE id = ?", (producto_id,)).fetchone()[0]


def contar(con, tabla):
    return con.execute("SELECT COUNT(*) FROM %s" % tabla).fetchone()[0]


def test_25_kg_por_30000(con):
    proveedor = crear_proveedor(con)
    producto_id, uc, _ = crear_producto(con)
    kg = uid(con, "kg")

    compra_id = registrar_compra(proveedor, "2026-01-10", "A-0001", "", [
        {"producto_id": producto_id, "cantidad": Decimal("25"),
         "unidad_id": kg, "precio_total": Decimal("30000")},
    ])

    assert precio_actual(con, producto_id) == 1200
    filas = con.execute(
        "SELECT * FROM historial_precios WHERE producto_id = ?", (producto_id,)).fetchall()
    assert len(filas) == 1
    assert filas[0]["precio_unitario"] == 1200
    assert filas[0]["unidad_id"] == uc
    assert filas[0]["detalle_compra_id"] is not None

    detalle = con.execute(
        "SELECT * FROM detalle_compras WHERE compra_id = ?", (compra_id,)).fetchone()
    assert detalle["cantidad"] == 25
    assert detalle["unidad_id"] == kg
    assert detalle["precio_unitario"] == 1200
    assert con.execute(
        "SELECT total FROM compras WHERE id = ?", (compra_id,)).fetchone()[0] == 30000


def test_500_g_por_600_en_producto_comprado_en_kg(con):
    proveedor = crear_proveedor(con)
    producto_id, _, _ = crear_producto(con)
    g = uid(con, "g")

    registrar_compra(proveedor, "2026-01-10", "", "", [
        {"producto_id": producto_id, "cantidad": Decimal("500"),
         "unidad_id": g, "precio_total": Decimal("600")},
    ])

    assert precio_actual(con, producto_id) == 1200


def test_tres_compras_dejan_tres_precios(con):
    proveedor = crear_proveedor(con)
    producto_id, _, _ = crear_producto(con)
    kg = uid(con, "kg")

    for fecha, precio in [("2026-01-01", 1200), ("2026-02-01", 1350), ("2026-03-01", 1500)]:
        registrar_compra(proveedor, fecha, "", "", [
            {"producto_id": producto_id, "cantidad": Decimal("1"),
             "unidad_id": kg, "precio_total": Decimal(str(precio))},
        ])

    assert contar(con, "historial_precios") == 3
    assert precio_actual(con, producto_id) == 1500


def test_compra_con_fecha_anterior_no_cambia_el_precio(con):
    proveedor = crear_proveedor(con)
    producto_id, _, _ = crear_producto(con)
    kg = uid(con, "kg")

    registrar_compra(proveedor, "2026-03-01", "", "", [
        {"producto_id": producto_id, "cantidad": Decimal("1"),
         "unidad_id": kg, "precio_total": Decimal("1500")},
    ])
    registrar_compra(proveedor, "2026-01-15", "", "", [
        {"producto_id": producto_id, "cantidad": Decimal("1"),
         "unidad_id": kg, "precio_total": Decimal("1000")},
    ])

    assert precio_actual(con, producto_id) == 1500
    assert contar(con, "historial_precios") == 2


def test_unidad_incompatible_hace_rollback_completo(con):
    proveedor = crear_proveedor(con)
    producto_id, _, _ = crear_producto(con)
    kg = uid(con, "kg")
    ml = uid(con, "ml")

    with pytest.raises(ErrorCompra):
        registrar_compra(proveedor, "2026-01-10", "", "", [
            {"producto_id": producto_id, "cantidad": Decimal("1"),
             "unidad_id": kg, "precio_total": Decimal("1200")},
            {"producto_id": producto_id, "cantidad": Decimal("1"),
             "unidad_id": ml, "precio_total": Decimal("100")},
        ])

    assert contar(con, "compras") == 0
    assert contar(con, "detalle_compras") == 0
    assert contar(con, "historial_precios") == 0
    assert precio_actual(con, producto_id) == 0


def test_eliminar_la_ultima_compra_restaura_el_precio_anterior(con):
    proveedor = crear_proveedor(con)
    producto_id, _, _ = crear_producto(con)
    kg = uid(con, "kg")

    ids = []
    for fecha, precio in [("2026-01-01", 1200), ("2026-02-01", 1350), ("2026-03-01", 1500)]:
        ids.append(registrar_compra(proveedor, fecha, "", "", [
            {"producto_id": producto_id, "cantidad": Decimal("1"),
             "unidad_id": kg, "precio_total": Decimal(str(precio))},
        ]))
    assert precio_actual(con, producto_id) == 1500

    sin_historial = eliminar_compra(ids[-1])

    assert sin_historial == []
    assert precio_actual(con, producto_id) == 1350
    assert contar(con, "historial_precios") == 2


def test_eliminar_la_unica_compra_conserva_el_precio_y_avisa(con):
    proveedor = crear_proveedor(con)
    producto_id, _, _ = crear_producto(con)
    kg = uid(con, "kg")

    compra_id = registrar_compra(proveedor, "2026-01-01", "", "", [
        {"producto_id": producto_id, "cantidad": Decimal("1"),
         "unidad_id": kg, "precio_total": Decimal("1200")},
    ])

    sin_historial = eliminar_compra(compra_id)

    assert sin_historial == ["Azúcar"]
    assert precio_actual(con, producto_id) == 1200
    assert contar(con, "historial_precios") == 0


# FIN tests/test_compras.py
