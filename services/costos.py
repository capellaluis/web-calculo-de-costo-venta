"""Pantalla de Costos: costos por receta y peso de cada ingrediente.

Todo se calcula con los precios actuales (secciones 6.2 y 6.3 del resumen).
"""

from decimal import Decimal

from services.recetas import calcular_receta, costo_linea


def _unidades_por_id(con):
    return {fila["id"]: fila for fila in con.execute("SELECT * FROM unidades")}


def resumen_recetas(con, unidades=None):
    """Lista con el costo total y por unidad de cada receta."""
    if unidades is None:
        unidades = _unidades_por_id(con)
    resultado = []
    for receta in con.execute("SELECT * FROM recetas ORDER BY nombre"):
        calculo = calcular_receta(con, receta["id"], unidades=unidades)
        resultado.append({
            "id": receta["id"],
            "nombre": receta["nombre"],
            "rendimiento_cantidad": receta["rendimiento_cantidad"],
            "rendimiento_unidad": receta["rendimiento_unidad"],
            "n_ingredientes": len(calculo["lineas"]),
            "total": calculo["total"],
            "costo_unidad": calculo["costo_unidad"],
            "hay_incompatible": any(l["incompatible"] for l in calculo["lineas"]),
        })
    return resultado


def ranking_ingredientes(con, unidades=None):
    """Ingredientes que más pesan en el costo, sumando todas las recetas.

    Devuelve (lista, total). Cada ítem trae el costo acumulado, en cuántas
    recetas se usa y el porcentaje sobre el costo total de todas las recetas.
    """
    if unidades is None:
        unidades = _unidades_por_id(con)
    filas = con.execute(
        "SELECT ri.producto_id, ri.cantidad, ri.unidad_id, ri.receta_id,"
        "       p.nombre AS producto, p.precio_actual, p.unidad_compra_id,"
        "       u.abreviatura AS unidad "
        "FROM receta_ingredientes ri "
        "JOIN productos p ON p.id = ri.producto_id "
        "JOIN unidades u ON u.id = ri.unidad_id").fetchall()

    acumulado = {}
    total = Decimal("0")
    for fila in filas:
        try:
            costo = costo_linea(fila["cantidad"], unidades[fila["unidad_id"]],
                                unidades[fila["unidad_compra_id"]], fila["precio_actual"])
        except (ValueError, KeyError):
            costo = Decimal("0")
        item = acumulado.setdefault(fila["producto_id"], {
            "producto_id": fila["producto_id"],
            "nombre": fila["producto"],
            "precio_actual": fila["precio_actual"],
            "unidad": fila["unidad"],
            "costo": Decimal("0"),
            "recetas": set(),
        })
        item["costo"] += costo
        item["recetas"].add(fila["receta_id"])
        total += costo

    lista = []
    for item in acumulado.values():
        item["n_recetas"] = len(item.pop("recetas"))
        item["porcentaje"] = (item["costo"] / total * 100) if total else None
        lista.append(item)
    lista.sort(key=lambda x: x["costo"], reverse=True)
    return lista, total


def costo_total_recetas(con):
    """Suma del costo de todas las recetas (para el Panel principal)."""
    return ranking_ingredientes(con)[1]


# FIN services/costos.py
