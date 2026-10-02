"""Pruebas del historial de precios (sección 6.2 y Fase 8 del resumen)."""

import pytest

from services.precios import (
    listar_precios,
    productos_con_aumento,
    resumen_ultimo,
    variacion,
)


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def crear_producto(con, nombre, categoria=None):
    categoria_id = None
    if categoria:
        categoria_id = con.execute(
            "INSERT INTO categorias (nombre) VALUES (?)", (categoria,)).lastrowid
    producto_id = con.execute(
        "INSERT INTO productos (nombre, categoria_id, unidad_compra_id, unidad_uso_id)"
        " VALUES (?, ?, ?, ?)",
        (nombre, categoria_id, uid(con, "kg"), uid(con, "g"))).lastrowid
    con.commit()
    return producto_id


def agregar_precio(con, producto_id, fecha, precio):
    con.execute(
        "INSERT INTO historial_precios (producto_id, fecha, precio_unitario, unidad_id)"
        " VALUES (?, ?, ?, ?)", (producto_id, fecha, precio, uid(con, "kg")))
    con.commit()


def buscar(lista, nombre):
    return next(item for item in lista if item["nombre"] == nombre)


def test_variacion(con):
    diferencia, porcentaje = variacion(1350, 1500)
    assert diferencia == 150
    assert round(porcentaje, 2) == 11.11


def test_variacion_sin_base(con):
    diferencia, porcentaje = variacion(0, 100)
    assert diferencia == 100
    assert porcentaje is None


def test_variacion_baja(con):
    diferencia, porcentaje = variacion(1500, 1200)
    assert diferencia == -300
    assert porcentaje < 0


def test_listar_precios_detecta_aumento(con):
    producto_id = crear_producto(con, "Azúcar", "Insumos")
    for fecha, precio in [("2026-01-01", 1200), ("2026-02-01", 1350), ("2026-03-01", 1500)]:
        agregar_precio(con, producto_id, fecha, precio)

    item = buscar(listar_precios(con), "Azúcar")
    assert item["anterior"] == 1350
    assert item["actual"] == 1500
    assert item["diferencia"] == 150
    assert item["aumento"] is True
    assert item["categoria"] == "Insumos"


def test_producto_con_un_solo_precio_no_tiene_variacion(con):
    producto_id = crear_producto(con, "Harina")
    agregar_precio(con, producto_id, "2026-01-01", 900)

    item = buscar(listar_precios(con), "Harina")
    assert item["anterior"] is None
    assert item["aumento"] is False
    assert item["porcentaje"] is None


def test_producto_que_baja_no_cuenta_como_aumento(con):
    producto_id = crear_producto(con, "Leche")
    agregar_precio(con, producto_id, "2026-01-01", 1500)
    agregar_precio(con, producto_id, "2026-02-01", 1200)

    item = buscar(listar_precios(con), "Leche")
    assert item["aumento"] is False


def test_productos_con_aumento_ordenados(con):
    azucar = crear_producto(con, "Azúcar")
    agregar_precio(con, azucar, "2026-01-01", 1200)
    agregar_precio(con, azucar, "2026-02-01", 1350)
    agregar_precio(con, azucar, "2026-03-01", 1500)

    harina = crear_producto(con, "Harina")
    agregar_precio(con, harina, "2026-01-01", 500)
    agregar_precio(con, harina, "2026-02-01", 900)

    subieron = productos_con_aumento(con)
    assert [item["nombre"] for item in subieron] == ["Harina", "Azúcar"]
    assert subieron[0]["diferencia"] == 400
    assert subieron[1]["diferencia"] == 150


def test_filtro_por_categoria(con):
    azucar = crear_producto(con, "Azúcar", "Insumos")
    agregar_precio(con, azucar, "2026-01-01", 1000)
    agregar_precio(con, azucar, "2026-02-01", 1200)

    limpieza = crear_producto(con, "Jabón", "Limpieza")
    agregar_precio(con, limpieza, "2026-01-01", 300)

    resultado = listar_precios(con, categoria="Insumos")
    assert [item["nombre"] for item in resultado] == ["Azúcar"]


def test_resumen_ultimo(con):
    producto_id = crear_producto(con, "Azúcar")
    agregar_precio(con, producto_id, "2026-01-01", 1200)
    agregar_precio(con, producto_id, "2026-02-01", 1350)
    agregar_precio(con, producto_id, "2026-03-01", 1500)

    resumen = resumen_ultimo(con, producto_id)
    assert resumen["anterior"] == 1350
    assert resumen["actual"] == 1500
    assert resumen["diferencia"] == 150
    assert resumen["aumento"] is True


def test_resumen_ultimo_con_pocos_precios(con):
    producto_id = crear_producto(con, "Harina")
    agregar_precio(con, producto_id, "2026-01-01", 900)
    assert resumen_ultimo(con, producto_id) is None


# FIN tests/test_precios.py
