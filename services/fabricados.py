"""Productos fabricados: lote con receta, costo por unidad y presentaciones.

Costo del lote = costo total de la receta (con los precios actuales).
Costo por unidad = costo del lote / cantidad fabricada.
Cada presentación (x6, x12, ...) cuesta "costo por unidad x cantidad".
Los precios de venta salen de los gastos fijos y los márgenes de ganancia.
"""

from decimal import Decimal

from services.margenes import calcular_precios_venta
from services.recetas import calcular_receta


class ErrorFabricado(ValueError):
    """Error de validación con mensaje en español para mostrar al usuario."""


def leer_fabricados(con):
    return [dict(fila) for fila in con.execute(
        "SELECT pf.*, r.nombre AS receta FROM productos_fabricados pf "
        "JOIN recetas r ON r.id = pf.receta_id ORDER BY pf.nombre")]


def presentaciones_de(con, fabricado_id):
    return [dict(fila) for fila in con.execute(
        "SELECT * FROM presentaciones WHERE producto_fabricado_id = ? ORDER BY id",
        (fabricado_id,))]


def calcular_fabricado(con, fabricado_id, gastos=None, margenes=None, redondeo="entero"):
    fila = con.execute(
        "SELECT pf.*, r.nombre AS receta FROM productos_fabricados pf "
        "JOIN recetas r ON r.id = pf.receta_id WHERE pf.id = ?", (fabricado_id,)).fetchone()
    if fila is None:
        raise ErrorFabricado("El producto fabricado no existe.")

    unidades = {u["id"]: u for u in con.execute("SELECT * FROM unidades")}
    receta = calcular_receta(con, fila["receta_id"], unidades=unidades)
    costo_lote = receta["total"]
    cantidad = Decimal(str(fila["cantidad_fabricada"] or 1))
    costo_unidad = costo_lote / cantidad if cantidad else Decimal("0")

    presentaciones = []
    for presentacion in presentaciones_de(con, fabricado_id):
        costo = costo_unidad * Decimal(str(presentacion["cantidad_unidades"] or 0))
        item = dict(presentacion)
        item["costo"] = costo
        if gastos is not None and margenes is not None:
            item["precio"] = calcular_precios_venta(costo, gastos, margenes, redondeo)
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
    if fabricado_id is None:
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
    con.commit()
    return fabricado_id


# FIN services/fabricados.py
