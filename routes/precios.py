from flask import Blueprint, abort, render_template, request

from database.db import obtener_conexion
from services.precios import (
    historial_producto,
    listar_precios,
    resumen_ultimo,
)

bp = Blueprint("precios", __name__, url_prefix="/precios")


@bp.route("/")
def lista():
    categoria = request.args.get("categoria", "").strip()
    solo_aumentos = request.args.get("solo_aumentos", "") == "1"

    con = obtener_conexion()
    try:
        items = listar_precios(con, categoria=categoria or None)
        categorias = [f["nombre"] for f in con.execute(
            "SELECT nombre FROM categorias ORDER BY nombre")]
    finally:
        con.close()

    if solo_aumentos:
        items = [item for item in items if item["aumento"]]

    return render_template("precios_lista.html", seccion="precios",
                           items=items, categorias=categorias,
                           categoria=categoria, solo_aumentos=solo_aumentos)


def _buscar_producto(con, producto_id):
    fila = con.execute(
        "SELECT p.*, COALESCE(c.nombre, 'Sin categoría') AS categoria,"
        "       u.abreviatura AS unidad "
        "FROM productos p "
        "LEFT JOIN categorias c ON c.id = p.categoria_id "
        "JOIN unidades u ON u.id = p.unidad_compra_id "
        "WHERE p.id = ?", (producto_id,)).fetchone()
    if fila is None:
        abort(404)
    return fila


@bp.route("/<int:producto_id>")
def ver(producto_id):
    con = obtener_conexion()
    try:
        producto = _buscar_producto(con, producto_id)
        historial = historial_producto(con, producto_id)
        resumen = resumen_ultimo(con, producto_id)
    finally:
        con.close()

    grafico = {
        "etiquetas": [f["fecha"] for f in historial],
        "valores": [round(f["precio_unitario"], 2) for f in historial],
        "unidad": historial[0]["unidad"] if historial else "",
    }

    return render_template("precios_ver.html", seccion="precios",
                           producto=producto, historial=list(reversed(historial)),
                           resumen=resumen, grafico=grafico)


# FIN routes/precios.py
