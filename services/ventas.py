"""Ventas / pedidos.

Un pedido tiene canal (tienda/delivery) y estado (nuevo/entregado/cancelado).
Los ítems referencian un producto fabricado + presentación; el precio sale del
canal (tienda o delivery) y se puede editar. La ganancia se calcula con el COSTO
ACTUAL del producto fabricado.
"""

from decimal import Decimal, ROUND_HALF_UP

from services.fabricados import calcular_fabricado

CANALES = {"tienda": "Tienda", "delivery": "Delivery"}
ESTADOS = {"nuevo": "Nuevo", "entregado": "Entregado", "cancelado": "Cancelado"}
FORMAS_PAGO = ["Efectivo", "Transferencia", "Tarjeta", "Otro"]


class ErrorVenta(ValueError):
    """Error de validación con mensaje en español para mostrar al usuario."""


def _q(valor):
    return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def datos_presentacion(con, presentacion_id):
    fila = con.execute(
        "SELECT p.nombre AS presentacion, pf.id AS fabricado_id, pf.nombre AS fabricado"
        " FROM presentaciones p"
        " JOIN productos_fabricados pf ON pf.id = p.producto_fabricado_id"
        " WHERE p.id = ?", (presentacion_id,)).fetchone()
    if fila is None:
        return None
    return {"producto_fabricado_id": fila["fabricado_id"],
            "descripcion": "%s %s" % (fila["fabricado"], fila["presentacion"])}


def datos_para_form(con):
    """Productos fabricados con sus presentaciones y precios (para el formulario)."""
    fabricados = []
    for fila in con.execute("SELECT id, nombre FROM productos_fabricados ORDER BY nombre"):
        calculo = calcular_fabricado(con, fila["id"])
        presentaciones = [{
            "id": p["id"], "nombre": p["nombre"], "cantidad_unidades": p["cantidad_unidades"],
            "tienda": float(p["tienda"]) if p["tienda"] is not None else None,
            "delivery": float(p["delivery"]) if p["delivery"] is not None else None,
        } for p in calculo["presentaciones"]]
        fabricados.append({"id": fila["id"], "nombre": fila["nombre"],
                           "presentaciones": presentaciones})
    return fabricados


def _ganancia_pedido(con, pedido):
    """Ganancia (precio - costo actual) de un pedido, menos el descuento."""
    caché = {}
    ganancia = Decimal("0")
    for item in con.execute(
            "SELECT * FROM pedido_items WHERE pedido_id = ?", (pedido["id"],)):
        costo = Decimal("0")
        if item["producto_fabricado_id"] and item["presentacion_id"]:
            calculo = caché.get(item["producto_fabricado_id"])
            if calculo is None:
                calculo = calcular_fabricado(con, item["producto_fabricado_id"])
                caché[item["producto_fabricado_id"]] = calculo
            for presentacion in calculo["presentaciones"]:
                if presentacion["id"] == item["presentacion_id"]:
                    costo = Decimal(str(presentacion["costo"] or 0))
                    break
        ganancia += (Decimal(str(item["precio_unitario"])) - costo) * Decimal(str(item["cantidad"]))
    return ganancia - Decimal(str(pedido["descuento"] or 0))


def leer_pedido(con, pedido_id):
    pedido = con.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
    if pedido is None:
        return None
    caché = {}
    items = []
    ganancia = Decimal("0")
    for item in con.execute(
            "SELECT * FROM pedido_items WHERE pedido_id = ? ORDER BY id", (pedido_id,)):
        fila = dict(item)
        costo = Decimal("0")
        if fila["producto_fabricado_id"] and fila["presentacion_id"]:
            calculo = caché.get(fila["producto_fabricado_id"])
            if calculo is None:
                calculo = calcular_fabricado(con, fila["producto_fabricado_id"])
                caché[fila["producto_fabricado_id"]] = calculo
            for presentacion in calculo["presentaciones"]:
                if presentacion["id"] == fila["presentacion_id"]:
                    costo = Decimal(str(presentacion["costo"] or 0))
                    break
        fila["costo_unitario"] = costo
        fila["subtotal"] = fila["precio_unitario"] * fila["cantidad"]
        fila["ganancia"] = (Decimal(str(fila["precio_unitario"])) - costo) * Decimal(str(fila["cantidad"]))
        ganancia += fila["ganancia"]
        items.append(fila)
    return {"pedido": dict(pedido), "items": items, "total": pedido["total"],
            "ganancia": ganancia - Decimal(str(pedido["descuento"] or 0))}


def listar_pedidos(con, filtros=None):
    filtros = filtros or {}
    sql = "SELECT * FROM pedidos WHERE 1 = 1"
    params = []
    if filtros.get("desde"):
        sql += " AND fecha >= ?"
        params.append(filtros["desde"])
    if filtros.get("hasta"):
        sql += " AND fecha <= ?"
        params.append(filtros["hasta"])
    if filtros.get("canal"):
        sql += " AND canal = ?"
        params.append(filtros["canal"])
    if filtros.get("estado"):
        sql += " AND estado = ?"
        params.append(filtros["estado"])
    if filtros.get("cliente"):
        sql += " AND COALESCE(cliente_nombre, '') LIKE ?"
        params.append("%" + filtros["cliente"] + "%")
    sql += " ORDER BY fecha DESC, id DESC"

    filas = []
    for pedido in con.execute(sql, params):
        filas.append({**dict(pedido), "ganancia": _ganancia_pedido(con, pedido)})
    return filas


def resumen_periodo(con, desde=None, hasta=None):
    sql = "SELECT * FROM pedidos WHERE estado != 'cancelado'"
    params = []
    if desde:
        sql += " AND fecha >= ?"
        params.append(desde)
    if hasta:
        sql += " AND fecha <= ?"
        params.append(hasta)
    total = 0.0
    ganancia = Decimal("0")
    cantidad = 0
    for pedido in con.execute(sql, params):
        total += pedido["total"] or 0
        ganancia += _ganancia_pedido(con, pedido)
        cantidad += 1
    return {"total": total, "ganancia": ganancia, "cantidad": cantidad}


def guardar_pedido(con, pedido_id, datos, items):
    if not datos.get("fecha"):
        raise ErrorVenta("Elegí la fecha del pedido.")
    if datos.get("canal") not in CANALES:
        raise ErrorVenta("Elegí el canal (tienda o delivery).")
    if not items:
        raise ErrorVenta("Agregá al menos un producto.")

    total = Decimal("0")
    for item in items:
        if item["cantidad"] <= 0:
            raise ErrorVenta("La cantidad debe ser mayor a cero.")
        if item["precio_unitario"] < 0:
            raise ErrorVenta("El precio no puede ser negativo.")
        total += Decimal(str(item["precio_unitario"])) * Decimal(str(item["cantidad"]))

    descuento = Decimal(str(datos.get("descuento") or 0))
    if descuento < 0:
        raise ErrorVenta("El descuento no puede ser negativo.")
    total_final = total - descuento
    if total_final < 0:
        total_final = Decimal("0")

    valores = (datos["fecha"], datos["canal"], datos.get("cliente_nombre", ""),
               datos.get("forma_pago", ""), float(descuento), datos.get("estado", "nuevo"),
               datos.get("notas", ""))
    if pedido_id is None:
        pedido_id = con.execute(
            "INSERT INTO pedidos"
            " (fecha, canal, cliente_nombre, forma_pago, descuento, estado, notas, total)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, 0)", valores).lastrowid
    else:
        con.execute(
            "UPDATE pedidos SET fecha = ?, canal = ?, cliente_nombre = ?, forma_pago = ?,"
            " descuento = ?, estado = ?, notas = ?, total = 0 WHERE id = ?",
            valores + (pedido_id,))
        con.execute("DELETE FROM pedido_items WHERE pedido_id = ?", (pedido_id,))

    for item in items:
        con.execute(
            "INSERT INTO pedido_items (pedido_id, producto_fabricado_id, presentacion_id,"
            " descripcion, cantidad, precio_unitario) VALUES (?, ?, ?, ?, ?, ?)",
            (pedido_id, item.get("producto_fabricado_id"), item.get("presentacion_id"),
             item["descripcion"], float(item["cantidad"]), float(item["precio_unitario"])))
    con.execute("UPDATE pedidos SET total = ? WHERE id = ?",
                (float(_q(total_final)), pedido_id))
    con.commit()
    return pedido_id


def cambiar_estado(con, pedido_id, estado):
    if estado not in ESTADOS:
        raise ErrorVenta("Estado no válido.")
    con.execute("UPDATE pedidos SET estado = ? WHERE id = ?", (estado, pedido_id))
    con.commit()


def eliminar_pedido(con, pedido_id):
    con.execute("DELETE FROM pedido_items WHERE pedido_id = ?", (pedido_id,))
    con.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
    con.commit()


# FIN services/ventas.py
