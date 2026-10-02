"""Historial de precios: variaciones y detección de aumentos.

El historial NUNCA se borra (salvo al eliminar el producto). Cada fila guarda
el precio por unidad de la unidad de compra del producto en una fecha.
"""


def variacion(anterior, actual):
    """Devuelve (diferencia, porcentaje). El porcentaje es None si no hay base."""
    diferencia = actual - anterior
    porcentaje = None
    if anterior:
        porcentaje = diferencia / anterior * 100
    return diferencia, porcentaje


def resumen_par(anterior, actual):
    """Resumen entre dos precios."""
    diferencia, porcentaje = variacion(anterior, actual)
    return {
        "anterior": anterior,
        "actual": actual,
        "diferencia": diferencia,
        "porcentaje": porcentaje,
        "aumento": diferencia > 0,
    }


def historial_producto(con, producto_id):
    """Todos los precios de un producto, del más viejo al más nuevo."""
    return con.execute(
        "SELECT h.fecha, h.precio_unitario, u.abreviatura AS unidad "
        "FROM historial_precios h JOIN unidades u ON u.id = h.unidad_id "
        "WHERE h.producto_id = ? ORDER BY h.fecha ASC, h.id ASC",
        (producto_id,)).fetchall()


def resumen_ultimo(con, producto_id):
    """Compara los dos últimos precios del producto. None si hay menos de dos."""
    filas = historial_producto(con, producto_id)
    if len(filas) < 2:
        return None
    anterior = filas[-2]["precio_unitario"]
    actual = filas[-1]["precio_unitario"]
    resumen = resumen_par(anterior, actual)
    resumen["unidad"] = filas[-1]["unidad"]
    resumen["fecha_anterior"] = filas[-2]["fecha"]
    resumen["fecha_actual"] = filas[-1]["fecha"]
    return resumen


def listar_precios(con, categoria=None):
    """Un resumen por producto: último precio, precio anterior y variación."""
    sql = (
        "WITH ranked AS ("
        "  SELECT producto_id, fecha, precio_unitario, unidad_id,"
        "         ROW_NUMBER() OVER (PARTITION BY producto_id"
        "                            ORDER BY fecha DESC, id DESC) AS rn"
        "  FROM historial_precios"
        ")"
        " SELECT p.id AS producto_id, p.nombre AS nombre,"
        "        COALESCE(c.nombre, 'Sin categoría') AS categoria,"
        "        u.abreviatura AS unidad,"
        "        a.fecha AS fecha_actual, a.precio_unitario AS actual,"
        "        b.fecha AS fecha_anterior, b.precio_unitario AS anterior"
        " FROM ranked a"
        " JOIN productos p ON p.id = a.producto_id"
        " LEFT JOIN categorias c ON c.id = p.categoria_id"
        " LEFT JOIN ranked b ON b.producto_id = a.producto_id AND b.rn = 2"
        " LEFT JOIN unidades u ON u.id = a.unidad_id"
        " WHERE a.rn = 1"
    )
    params = []
    if categoria:
        sql += " AND COALESCE(c.nombre, 'Sin categoría') = ?"
        params.append(categoria)
    sql += " ORDER BY p.nombre"

    resultado = []
    for fila in con.execute(sql, params).fetchall():
        item = dict(fila)
        if fila["anterior"] is None:
            item.update({"diferencia": 0.0, "porcentaje": None, "aumento": False})
        else:
            item.update(resumen_par(fila["anterior"], fila["actual"]))
        resultado.append(item)
    return resultado


def productos_con_aumento(con, limite=None):
    """Productos cuyo último precio es mayor al anterior, de mayor a menor."""
    aumentos = [item for item in listar_precios(con) if item["aumento"]]
    aumentos.sort(key=lambda item: item["diferencia"], reverse=True)
    if limite:
        aumentos = aumentos[:limite]
    return aumentos


# FIN services/precios.py
