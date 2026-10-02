"""Recetas: ingredientes, rendimiento y costos.

El costo se calcula SIEMPRE en el momento, leyendo el precio actual del producto
(sección 6.3 del resumen). Por eso, al subir el precio de un producto, el costo
de las recetas que lo usan sube solo: no hay ningún costo guardado.
"""

from decimal import Decimal

from services.unidades import convertir


class ErrorReceta(ValueError):
    """Error de validación con mensaje en español para mostrar al usuario."""


def _unidades_por_id(con):
    return {fila["id"]: fila for fila in con.execute("SELECT * FROM unidades")}


def costo_linea(cantidad, unidad_ingrediente, unidad_compra, precio_actual):
    """Costo de un ingrediente: convierte la cantidad a la unidad de compra del
    producto y la multiplica por el precio actual (por esa unidad de compra)."""
    cantidad_en_compra = convertir(cantidad, unidad_ingrediente, unidad_compra)
    return cantidad_en_compra * Decimal(str(precio_actual or 0))


def validar_ingredientes(con, ingredientes, unidades=None):
    """Devuelve un mensaje de error o None si todo está bien."""
    if not ingredientes:
        return "Agregá al menos un ingrediente."
    if unidades is None:
        unidades = _unidades_por_id(con)
    for item in ingredientes:
        producto = con.execute(
            "SELECT * FROM productos WHERE id = ?", (item["producto_id"],)).fetchone()
        if producto is None:
            return "Uno de los productos elegidos no existe."
        u_ingrediente = unidades.get(item["unidad_id"])
        u_compra = unidades.get(producto["unidad_compra_id"])
        if u_ingrediente is None or u_compra is None:
            return "La unidad elegida no es válida."
        try:
            convertir(item["cantidad"], u_ingrediente, u_compra)
        except ValueError:
            return ("La unidad de un ingrediente no es compatible con la del "
                    "producto (por ejemplo, no podés usar litros para un "
                    "producto que se compra por kilogramo).")
    return None


def calcular_receta(con, receta_id, unidades=None):
    """Devuelve la receta, sus líneas con costo, el total y el costo por unidad."""
    receta = con.execute(
        "SELECT * FROM recetas WHERE id = ?", (receta_id,)).fetchone()
    if receta is None:
        raise ErrorReceta("La receta no existe.")
    if unidades is None:
        unidades = _unidades_por_id(con)

    filas = con.execute(
        "SELECT ri.id, ri.cantidad, ri.unidad_id, ri.producto_id,"
        "       p.nombre AS producto, p.precio_actual, p.unidad_compra_id,"
        "       u.abreviatura AS unidad "
        "FROM receta_ingredientes ri "
        "JOIN productos p ON p.id = ri.producto_id "
        "JOIN unidades u ON u.id = ri.unidad_id "
        "WHERE ri.receta_id = ? ORDER BY ri.id", (receta_id,)).fetchall()

    lineas = []
    total = Decimal("0")
    for fila in filas:
        item = dict(fila)
        u_ingrediente = unidades.get(fila["unidad_id"])
        u_compra = unidades.get(fila["unidad_compra_id"])
        try:
            item["costo"] = costo_linea(
                fila["cantidad"], u_ingrediente, u_compra, fila["precio_actual"])
            item["incompatible"] = False
            total += item["costo"]
        except ValueError:
            item["costo"] = Decimal("0")
            item["incompatible"] = True
        lineas.append(item)

    rendimiento = Decimal(str(receta["rendimiento_cantidad"] or 1))
    costo_unidad = total / rendimiento if rendimiento else Decimal("0")

    return {"receta": receta, "lineas": lineas, "total": total,
            "costo_unidad": costo_unidad,
            "rendimiento": rendimiento}


def costo_receta(con, receta_id, unidades=None):
    """Atajo: devuelve (total, costo_por_unidad) de una receta."""
    calculo = calcular_receta(con, receta_id, unidades=unidades)
    return calculo["total"], calculo["costo_unidad"]


# FIN services/recetas.py
