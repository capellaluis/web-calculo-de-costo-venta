from datetime import date
from decimal import InvalidOperation

from flask import Blueprint, abort, redirect, render_template, request, url_for

from database.db import obtener_conexion
from services.compras import ErrorCompra, eliminar_compra, registrar_compra
from services.numeros import leer_decimal

bp = Blueprint("compras", __name__, url_prefix="/compras")

AVISOS = {
    "creado": "Compra registrada correctamente.",
    "eliminado": "Compra eliminada.",
    "error": "No se pudo eliminar la compra.",
}


def cargar_listas(con):
    return {
        "proveedores": [dict(f) for f in con.execute(
            "SELECT id, nombre FROM proveedores ORDER BY nombre")],
        "productos": [dict(f) for f in con.execute(
            "SELECT p.id, p.nombre, p.unidad_compra_id, u.abreviatura AS abrev_compra "
            "FROM productos p JOIN unidades u ON u.id = p.unidad_compra_id "
            "ORDER BY p.nombre")],
        "unidades": [dict(f) for f in con.execute(
            "SELECT * FROM unidades ORDER BY tipo, nombre")],
    }


@bp.route("/")
def lista():
    desde = request.args.get("desde", "").strip()
    hasta = request.args.get("hasta", "").strip()
    proveedor = request.args.get("proveedor", "").strip()
    aviso = AVISOS.get(request.args.get("aviso", ""))
    sin_historial = request.args.get("sin_historial", "").strip()

    sql = ("SELECT c.*, p.nombre AS proveedor FROM compras c "
           "JOIN proveedores p ON p.id = c.proveedor_id WHERE 1 = 1")
    params = []
    if desde:
        sql += " AND c.fecha >= ?"
        params.append(desde)
    if hasta:
        sql += " AND c.fecha <= ?"
        params.append(hasta)
    if proveedor:
        sql += " AND c.proveedor_id = ?"
        params.append(proveedor)
    sql += " ORDER BY c.fecha DESC, c.id DESC"

    con = obtener_conexion()
    try:
        filas = con.execute(sql, params).fetchall()
        proveedores = [dict(f) for f in con.execute(
            "SELECT id, nombre FROM proveedores ORDER BY nombre")]
    finally:
        con.close()

    total = sum(f["total"] or 0 for f in filas)
    return render_template("compras_lista.html", seccion="compras",
                           compras=filas, proveedores=proveedores, total=total,
                           desde=desde, hasta=hasta, proveedor=proveedor,
                           aviso=aviso, sin_historial=sin_historial)


def _leer_lineas():
    ids = request.form.getlist("producto_id")
    cantidades = request.form.getlist("cantidad")
    unidades = request.form.getlist("unidad_id")
    precios = request.form.getlist("precio_total")

    lineas = []
    for producto, cantidad, unidad, precio in zip(ids, cantidades, unidades, precios):
        if not producto:
            continue
        if not unidad:
            return None, "Elegí la unidad de cada producto."
        try:
            cant = leer_decimal(cantidad)
            total = leer_decimal(precio)
        except (InvalidOperation, ValueError):
            return None, ("La cantidad y el precio deben ser números. "
                          "Ejemplo: 25 y 30000,50.")
        lineas.append({
            "producto_id": int(producto),
            "cantidad": cant,
            "unidad_id": int(unidad),
            "precio_total": total,
        })

    if not lineas:
        return None, "Agregá al menos un producto a la compra."
    return lineas, None


def _lineas_mostradas():
    """Las líneas tal como llegaron del formulario, para volver a mostrarlas."""
    ids = request.form.getlist("producto_id")
    cantidades = request.form.getlist("cantidad")
    unidades = request.form.getlist("unidad_id")
    precios = request.form.getlist("precio_total")
    filas = []
    for producto, cantidad, unidad, precio in zip(ids, cantidades, unidades, precios):
        if not producto and not cantidad and not precio:
            continue
        filas.append({"producto_id": producto, "cantidad": cantidad,
                      "unidad_id": unidad, "precio_total": precio})
    return filas


def _form_vacio():
    return {"proveedor_id": "", "fecha": date.today().isoformat(),
            "numero_documento": "", "observaciones": ""}


@bp.route("/nueva", methods=["GET", "POST"])
def nueva():
    datos = _form_vacio()
    lineas = []
    error = None

    if request.method == "POST":
        datos = {
            "proveedor_id": request.form.get("proveedor_id", "").strip(),
            "fecha": request.form.get("fecha", "").strip(),
            "numero_documento": request.form.get("numero_documento", "").strip(),
            "observaciones": request.form.get("observaciones", "").strip(),
        }
        lineas, error = _leer_lineas()
        if error is None:
            try:
                compra_id = registrar_compra(
                    int(datos["proveedor_id"]), datos["fecha"],
                    datos["numero_documento"], datos["observaciones"], lineas)
                return redirect(url_for("compras.ver", compra_id=compra_id,
                                        aviso="creado"))
            except ErrorCompra as exc:
                error = str(exc)
            except ValueError:
                error = "Elegí el proveedor y la fecha de la compra."
        lineas = _lineas_mostradas()

    con = obtener_conexion()
    try:
        listas = cargar_listas(con)
    finally:
        con.close()
    return render_template("compras_form.html", seccion="compras",
                           datos=datos, lineas=lineas, error=error, **listas)


@bp.route("/<int:compra_id>")
def ver(compra_id):
    con = obtener_conexion()
    try:
        compra = con.execute(
            "SELECT c.*, p.nombre AS proveedor FROM compras c "
            "JOIN proveedores p ON p.id = c.proveedor_id WHERE c.id = ?",
            (compra_id,)).fetchone()
        if compra is None:
            abort(404)
        detalle = con.execute(
            "SELECT d.*, pr.nombre AS producto, u.abreviatura AS unidad "
            "FROM detalle_compras d "
            "JOIN productos pr ON pr.id = d.producto_id "
            "JOIN unidades u ON u.id = d.unidad_id "
            "WHERE d.compra_id = ? ORDER BY d.id", (compra_id,)).fetchall()
    finally:
        con.close()
    return render_template("compras_ver.html", seccion="compras", compra=compra,
                           detalle=detalle,
                           aviso=AVISOS.get(request.args.get("aviso", "")))


@bp.route("/<int:compra_id>/eliminar", methods=["POST"])
def eliminar(compra_id):
    try:
        sin_historial = eliminar_compra(compra_id)
    except ErrorCompra:
        return redirect(url_for("compras.lista", aviso="error"))
    if sin_historial:
        return redirect(url_for("compras.lista", aviso="eliminado",
                                sin_historial=len(sin_historial)))
    return redirect(url_for("compras.lista", aviso="eliminado"))


# FIN routes/compras.py
