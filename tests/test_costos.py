"""Pruebas de la pantalla de Costos (Fase 10)."""

from decimal import Decimal

from services.costos import (
    costo_total_recetas,
    ranking_ingredientes,
    resumen_recetas,
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


def ingrediente(con, receta_id, producto_id, cantidad, unidad):
    con.execute(
        "INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad_id)"
        " VALUES (?, ?, ?, ?)", (receta_id, producto_id, cantidad, uid(con, unidad)))


def sembrar(con):
    maiz = crear_producto(con, "Maíz", "kg", "g", 200)
    azucar = crear_producto(con, "Azúcar", "kg", "g", 1200)
    leche = crear_producto(con, "Leche", "l", "ml", 1000)
    canela = crear_producto(con, "Canela", "kg", "g", 8000)

    chicha = crear_receta(con, "Chicha", 10)
    ingrediente(con, chicha, maiz, 500, "g")
    ingrediente(con, chicha, azucar, 300, "g")
    ingrediente(con, chicha, leche, 1, "l")
    ingrediente(con, chicha, canela, 10, "g")

    postre = crear_receta(con, "Postre", 4, "porciones")
    ingrediente(con, postre, leche, 1, "l")
    ingrediente(con, postre, azucar, 200, "g")
    con.commit()
    return {"chicha": chicha, "postre": postre}


def test_resumen_recetas(con):
    ids = sembrar(con)
    resumen = resumen_recetas(con)
    por_nombre = {r["nombre"]: r for r in resumen}
    assert por_nombre["Chicha"]["total"] == Decimal("1540")
    assert por_nombre["Chicha"]["costo_unidad"] == Decimal("154")
    assert por_nombre["Postre"]["total"] == Decimal("1240")
    assert por_nombre["Postre"]["costo_unidad"] == Decimal("310")


def test_ranking_ingredientes(con):
    sembrar(con)
    lista, total = ranking_ingredientes(con)
    # Leche: 1000 + 1000 = 2000; Azúcar: 360 + 240 = 600; Maíz 100; Canela 80.
    assert total == Decimal("2780")
    assert [i["nombre"] for i in lista] == ["Leche", "Azúcar", "Maíz", "Canela"]
    leche = lista[0]
    assert leche["costo"] == Decimal("2000")
    assert leche["n_recetas"] == 2
    assert round(float(leche["porcentaje"]), 2) == round(2000 / 2780 * 100, 2)


def test_costo_total_recetas_coincide_con_la_suma(con):
    sembrar(con)
    resumen = resumen_recetas(con)
    assert costo_total_recetas(con) == sum(r["total"] for r in resumen)


def test_sin_recetas(con):
    assert resumen_recetas(con) == []
    lista, total = ranking_ingredientes(con)
    assert lista == []
    assert total == 0


# FIN tests/test_costos.py
