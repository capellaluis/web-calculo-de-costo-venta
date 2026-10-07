"""Productos fabricados: costo del lote y precios por producto.

Cada producto fabricado guarda SU configuración de precios:
  - gastos fijos (se SUMAN al costo),
  - 3 márgenes de ganancia (se DIVIDEN) y cuál se usa,
  - % de delivery (comisión, IVA, 2,9%...) que se DIVIDEN sobre el precio de tienda.

Un producto nuevo arranca con la ÚLTIMA configuración guardada (la "plantilla").
Precio de tienda = (costo + gastos) / (1 - margen %)
Precio delivery  = tienda / (1 - suma de % de delivery)
"""

import json
from decimal import Decimal

from services.margenes import ErrorMargen, leer_redondeo, redondear
from services.recetas import calcular_receta


class ErrorFabricado(ValueError):
    """Error de validación con mensaje en español para mostrar al usuario."""


PLANTILLA_DEFECTO = {
    "gastos": [
        {"nombre": "Gas", "porcentaje": 0},
        {"nombre": "Agua", "porcentaje": 0},
        {"nombre": "Luz", "porcentaje": 0},
    ],
    "margenes": [
        {"numero": 1, "nombre": "Margen 1", "porcentaje": 30, "elegido": 1},
        {"numero": 2, "nombre": "Margen 2", "porcentaje": 50, "elegido": 0},
        {"numero": 3, "nombre": "Margen 3", "porcentaje": 70, "elegido": 0},
    ],
    "delivery": [
        {"nombre": "Comisión", "porcentaje": 0},
        {"nombre": "IVA", "porcentaje": 0},
        {"nombre": "2,9%", "porcentaje": 2.9},
    ],
}


def _dec(valor):
    return Decimal(str(valor or 0))


def _leer_json(con, clave, defecto):
    fila = con.execute(
        "SELECT valor FROM configuracion WHERE clave = ?", (clave,)).fetchone()
    if fila is None:
        return defecto
    try:
        return json.loads(fila["valor"])
    except (ValueError, TypeError):
        return defecto


def _guardar_json(con, clave, valor):
    con.execute(
        "INSERT INTO configuracion (clave, valor) VALUES (?, ?)"
        " ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor",
        (clave, json.dumps(valor, ensure_ascii=False, default=float)))


def leer_plantilla(con):
    return {
        "gastos": _leer_json(con, "plantilla_gastos", PLANTILLA_DEFECTO["gastos"]),
        "margenes": _leer_json(con, "plantilla_margenes", PLANTILLA_DEFECTO["margenes"]),
        "delivery": _leer_json(con, "plantilla_delivery", PLANTILLA_DEFECTO["delivery"]),
    }


def guardar_plantilla(con, gastos, margenes, delivery):
    _guardar_json(con, "plantilla_gastos", gastos)
    _guardar_json(con, "plantilla_margenes", margenes)
    _guardar_json(con, "plantilla_delivery", delivery)
    con.commit()


def leer_fabricados(con):
    return [dict(fila) for fila in con.execute(
        "SELECT pf.*, r.nombre AS receta FROM productos_fabricados pf "
        "JOIN recetas r ON r.id = pf.receta_id ORDER BY pf.nombre")]


def presentaciones_de(con, fabricado_id):
    return [dict(fila) for fila in con.execute(
        "SELECT * FROM presentaciones WHERE producto_fabricado_id = ? ORDER BY id",
        (fabricado_id,))]


def leer_config_fabricado(con, fabricado_id):
    """Devuelve la config del producto; si no tiene, usa la última guardada."""
    gastos = [dict(f) for f in con.execute(
        "SELECT nombre, porcentaje FROM fabricado_gastos"
        " WHERE producto_fabricado_id = ? ORDER BY orden, id", (fabricado_id,))]
    margenes = [dict(f) for f in con.execute(
        "SELECT numero, nombre, porcentaje, elegido FROM fabricado_margenes"
        " WHERE producto_fabricado_id = ? ORDER BY numero", (fabricado_id,))]
    delivery = [dict(f) for f in con.execute(
        "SELECT nombre, porcentaje FROM fabricado_delivery"
        " WHERE producto_fabricado_id = ? ORDER BY orden, id", (fabricado_id,))]

    plantilla = leer_plantilla(con)
    if not gastos:
        gastos = plantilla["gastos"]
    if not margenes:
        margenes = plantilla["margenes"]
    if not delivery:
        delivery = plantilla["delivery"]
    return {"gastos": gastos, "margenes": margenes, "delivery": delivery}


def _insertar_config(con, fabricado_id, gastos, margenes, delivery):
    con.execute("DELETE FROM fabricado_gastos WHERE producto_fabricado_id = ?",
                (fabricado_id,))
    con.execute("DELETE FROM fabricado_margenes WHERE producto_fabricado_id = ?",
                (fabricado_id,))
    con.execute("DELETE FROM fabricado_delivery WHERE producto_fabricado_id = ?",
                (fabricado_id,))

    for orden, gasto in enumerate(gastos):
        con.execute(
            "INSERT INTO fabricado_gastos"
            " (producto_fabricado_id, nombre, porcentaje, orden) VALUES (?, ?, ?, ?)",
            (fabricado_id, gasto["nombre"] or "Gasto",
             float(gasto["porcentaje"]), orden))
    for margen in margenes:
        con.execute(
            "INSERT INTO fabricado_margenes"
            " (producto_fabricado_id, numero, nombre, porcentaje, elegido)"
            " VALUES (?, ?, ?, ?, ?)",
            (fabricado_id, margen["numero"], margen["nombre"] or "Margen",
             float(margen["porcentaje"]), 1 if margen.get("elegido") else 0))
    for orden, item in enumerate(delivery):
        con.execute(
            "INSERT INTO fabricado_delivery"
            " (producto_fabricado_id, nombre, porcentaje, orden) VALUES (?, ?, ?, ?)",
            (fabricado_id, item["nombre"] or "Delivery",
             float(item["porcentaje"]), orden))


def tiene_config(con, fabricado_id):
    for tabla in ("fabricado_gastos", "fabricado_margenes", "fabricado_delivery"):
        fila = con.execute(
            "SELECT 1 FROM %s WHERE producto_fabricado_id = ? LIMIT 1" % tabla,
            (fabricado_id,)).fetchone()
        if fila:
            return True
    return False


def sembrar_config_fabricado(con, fabricado_id):
    """Copia la última plantilla como config propia del producto nuevo."""
    plantilla = leer_plantilla(con)
    _insertar_config(con, fabricado_id, plantilla["gastos"], plantilla["margenes"],
                     plantilla["delivery"])
    con.commit()


def guardar_config_fabricado(con, fabricado_id, gastos, margenes, delivery):
    """Reemplaza la config del producto y la guarda como última plantilla."""
    _insertar_config(con, fabricado_id, gastos, margenes, delivery)
    con.commit()
    guardar_plantilla(con, gastos, margenes, delivery)


def _margen_elegido(margenes):
    for margen in margenes:
        if margen.get("elegido"):
            return margen
    return margenes[0] if margenes else None


def calcular_fabricado(con, fabricado_id, redondeo=None):
    fila = con.execute(
        "SELECT pf.*, r.nombre AS receta FROM productos_fabricados pf "
        "JOIN recetas r ON r.id = pf.receta_id WHERE pf.id = ?", (fabricado_id,)).fetchone()
    if fila is None:
        raise ErrorFabricado("El producto fabricado no existe.")
    if redondeo is None:
        redondeo = leer_redondeo(con)

    unidades = {u["id"]: u for u in con.execute("SELECT * FROM unidades")}
    receta = calcular_receta(con, fila["receta_id"], unidades=unidades)
    costo_lote = receta["total"]
    cantidad = _dec(fila["cantidad_fabricada"] or 1)
    costo_unidad = costo_lote / cantidad if cantidad else Decimal("0")

    config = leer_config_fabricado(con, fabricado_id)
    total_gastos = sum((_dec(g["porcentaje"]) for g in config["gastos"]), Decimal("0"))
    total_delivery = sum((_dec(d["porcentaje"]) for d in config["delivery"]), Decimal("0"))
    margen = _margen_elegido(config["margenes"])
    margen_pct = _dec(margen["porcentaje"]) if margen else Decimal("0")

    presentaciones = []
    for presentacion in presentaciones_de(con, fabricado_id):
        costo = costo_unidad * _dec(presentacion["cantidad_unidades"])
        con_gastos = costo * (1 + total_gastos / 100)
        tienda = None
        delivery = None
        ganancia = None
        if margen_pct < 100:
            tienda = redondear(con_gastos / (1 - margen_pct / 100), redondeo)
            ganancia = tienda - con_gastos
            if total_delivery < 100:
                delivery = redondear(tienda / (1 - total_delivery / 100), redondeo)
        item = dict(presentacion)
        item.update({"costo": costo, "con_gastos": con_gastos,
                     "tienda": tienda, "delivery": delivery, "ganancia": ganancia,
                     "margen_pct": margen_pct})
        presentaciones.append(item)

    return {
        "id": fila["id"],
        "nombre": fila["nombre"],
        "receta": fila["receta"],
        "receta_id": fila["receta_id"],
        "cantidad_fabricada": fila["cantidad_fabricada"],
        "notas": fila["notas"],
        "costo_lote": costo_lote,
        "costo_unidad": costo_unidad,
        "config": config,
        "margen_elegido": margen,
        "total_gastos": total_gastos,
        "total_delivery": total_delivery,
        "presentaciones": presentaciones,
        "hay_incompatible": any(l["incompatible"] for l in receta["lineas"]),
    }


def guardar_fabricado(con, fabricado_id, datos, presentaciones):
    if not datos["nombre"]:
        raise ErrorFabricado("El nombre es obligatorio.")
    if not datos["receta_id"]:
        raise ErrorFabricado("Elegí la receta del producto.")
    if datos["cantidad_fabricada"] <= 0:
        raise ErrorFabricado("La cantidad fabricada debe ser mayor a cero.")
    for presentacion in presentaciones:
        if presentacion["cantidad_unidades"] <= 0:
            raise ErrorFabricado(
                "La cantidad de cada presentación debe ser mayor a cero.")

    valores = (datos["nombre"], int(datos["receta_id"]),
               float(datos["cantidad_fabricada"]), datos["notas"])
    nuevo = fabricado_id is None
    if nuevo:
        fabricado_id = con.execute(
            "INSERT INTO productos_fabricados"
            " (nombre, receta_id, cantidad_fabricada, notas) VALUES (?, ?, ?, ?)",
            valores).lastrowid
    else:
        con.execute(
            "UPDATE productos_fabricados SET nombre = ?, receta_id = ?,"
            " cantidad_fabricada = ?, notas = ? WHERE id = ?", valores + (fabricado_id,))
        con.execute(
            "DELETE FROM presentaciones WHERE producto_fabricado_id = ?", (fabricado_id,))

    for presentacion in presentaciones:
        nombre = (presentacion.get("nombre") or "").strip() or (
            "x%g" % presentacion["cantidad_unidades"])
        con.execute(
            "INSERT INTO presentaciones"
            " (producto_fabricado_id, nombre, cantidad_unidades) VALUES (?, ?, ?)",
            (fabricado_id, nombre, float(presentacion["cantidad_unidades"])))
    if nuevo:
        sembrar_config_fabricado(con, fabricado_id)
    con.commit()
    return fabricado_id


def fabricados_que_usan_producto(con, producto_id):
    """Nombres de productos fabricados cuya receta usa este insumo."""
    filas = con.execute(
        "SELECT DISTINCT pf.nombre AS nombre FROM productos_fabricados pf "
        "JOIN receta_ingredientes ri ON ri.receta_id = pf.receta_id "
        "WHERE ri.producto_id = ? ORDER BY pf.nombre", (producto_id,))
    return [f["nombre"] for f in filas]


# FIN services/fabricados.py
