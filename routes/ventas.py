from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, redirect, render_template, request, url_for

from database.db import obtener_conexion
from services.numeros import leer_decimal
from services.ventas import (
    CANALES,
    ESTADOS,
    FORMAS_PAGO,
    ErrorVenta,
    cambiar_estado,
    datos_para_form,
    datos_presentacion,
    eliminar_pedido,
    guardar_pedido,
    leer_pedido,
    listar_pedidos,
)

bp = Blueprint("ventas", __name__, url_prefix="/ventas")

AVISOS = {
    "creado": "Venta registrada correctamente.",
    "editado": "Cambios guardados correctamente.",
    "eliminado": "Venta eliminada.",
    "estado": "Estado actualizado.",
}


def _filtros():
    return {
        "desde": request.args.get("desde", "").strip(),
        "hasta": request.args.get("hasta", "").strip(),
        "canal": request.args.get("canal", "").strip(),
        "estado": request.args.get("estado", "").strip(),
        "cliente": request.args.get("cliente", "").strip(),
    }


def _presentaciones_json(con):
    planas = []
    for fabricado in datos_para_form(con):
        for pres in fabricado["presentaciones"]:
            planas.append({"id": pres["id"], "fabricado": fabricado["nombre"],
                           "nombre": pres["nombre"], "tienda": pres["tienda"],
                           "delivery": pres["delivery"]})
    return planas


def _leer_datos():
    try:
        descuento = leer_decimal(request.form.get("descuento", ""))
    except (InvalidOperation, ValueError):
        descuento = Decimal("0")
    return {
        "fecha": request.form.get("fecha", "").strip(),
        "canal": request.form.get("canal", "tienda").strip(),
        "cliente_nombre": request.form.get("cliente_nombre", "").strip(),
        "forma_pago": request.form.get("forma_pago", "").strip(),
        "descuento": descuento,
        "estado": request.form.get("estado", "nuevo").strip(),
        "notas": request.form.get("notas", "").strip(),
    }


def _leer_items(con):
    presentaciones = request.form.getlist("presentacion_id")
    cantidades = request.form.getlist("cantidad")
    precios = request.form.getlist("precio_unitario")
    items = []
    for pres, cant, precio in zip(presentaciones, cantidades, precios):
        if not pres:
            continue
        try:
            cantidad = leer_decimal(cant)
            precio_unitario = leer_decimal(precio)
        except (InvalidOperation, ValueError):
            return None, "La cantidad y el precio deben ser números."
        datos = datos_presentacion(con, int(pres))
        if datos is None:
            return None, "Una de las presentaciones elegidas no existe."
        items.append({"presentacion_id": int(pres),
                      "producto_fabricado_id": datos["producto_fabricado_id"],
                      "descripcion": datos["descripcion"],
                      "cantidad": cantidad, "precio_unitario": precio_unitario})
    if not items:
        return None, "Agregá al menos un producto."
    return items, None


def _items_mostrados(con):
    presentaciones = request.form.getlist("presentacion_id")
    cantidades = request.form.getlist("cantidad")
    precios = request.form.getlist("precio_unitario")
    filas = []
    for pres, cant, precio in zip(presentaciones, cantidades, precios):
        if not pres and not cant:
            continue
        filas.append({"presentacion_id": pres, "cantidad": cant, "precio_unitario": precio})
    return filas


@bp.route("/")
def lista():
    filtros = _filtros()
    aviso = AVISOS.get(request.args.get("aviso", ""))
    con = obtener_conexion()
    try:
        pedidos = listar_pedidos(con, filtros)
    finally:
        con.close()
    total = sum(p["total"] or 0 for p in pedidos)
    ganancia = sum(p["ganancia"] for p in pedidos)
    return render_template("ventas_lista.html", seccion="ventas", pedidos=pedidos,
                           total=total, ganancia=ganancia, filtros=filtros,
                           canales=CANALES, estados=ESTADOS, aviso=aviso)


def _form_vacio():
    return {"fecha": date.today().isoformat(), "canal": "tienda", "cliente_nombre": "",
            "forma_pago": "", "descuento": "", "estado": "nuevo", "notas": ""}


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    con = obtener_conexion()
    datos = _form_vacio()
    items = []
    error = None
    try:
        if request.method == "POST":
            datos = _leer_datos()
            items, error = _leer_items(con)
            if error is None:
                try:
                    pedido_id = guardar_pedido(con, None, datos, items)
                    return redirect(url_for("ventas.ver", pedido_id=pedido_id, aviso="creado"))
                except ErrorVenta as exc:
                    error = str(exc)
            items = _items_mostrados(con)
        presentaciones = _presentaciones_json(con)
    finally:
        con.close()
    return render_template("ventas_form.html", seccion="ventas", datos=datos, items=items,
                           presentaciones=presentaciones, error=error, editando=False,
                           pedido_id=None, canales=CANALES, estados=ESTADOS,
                           formas_pago=FORMAS_PAGO)


@bp.route("/<int:pedido_id>")
def ver(pedido_id):
    con = obtener_conexion()
    try:
        calculo = leer_pedido(con, pedido_id)
    finally:
        con.close()
    if calculo is None:
        abort(404)
    return render_template("ventas_ver.html", seccion="ventas", calculo=calculo,
                           canales=CANALES, estados=ESTADOS,
                           aviso=AVISOS.get(request.args.get("aviso", "")))


@bp.route("/<int:pedido_id>/editar", methods=["GET", "POST"])
def editar(pedido_id):
    con = obtener_conexion()
    error = None
    try:
        calculo = leer_pedido(con, pedido_id)
        if calculo is None:
            abort(404)
        pedido = calculo["pedido"]
        datos = {"fecha": pedido["fecha"], "canal": pedido["canal"],
                 "cliente_nombre": pedido["cliente_nombre"] or "",
                 "forma_pago": pedido["forma_pago"] or "",
                 "descuento": ("%g" % pedido["descuento"]) if pedido["descuento"] else "",
                 "estado": pedido["estado"], "notas": pedido["notas"] or ""}
        items = [{"presentacion_id": str(i["presentacion_id"]),
                  "cantidad": ("%g" % i["cantidad"]),
                  "precio_unitario": ("%g" % i["precio_unitario"])} for i in calculo["items"]]
        if request.method == "POST":
            datos = _leer_datos()
            items, error = _leer_items(con)
            if error is None:
                try:
                    guardar_pedido(con, pedido_id, datos, items)
                    return redirect(url_for("ventas.ver", pedido_id=pedido_id, aviso="editado"))
                except ErrorVenta as exc:
                    error = str(exc)
            items = _items_mostrados(con)
        presentaciones = _presentaciones_json(con)
    finally:
        con.close()
    return render_template("ventas_form.html", seccion="ventas", datos=datos, items=items,
                           presentaciones=presentaciones, error=error, editando=True,
                           pedido_id=pedido_id, canales=CANALES, estados=ESTADOS,
                           formas_pago=FORMAS_PAGO)


@bp.route("/<int:pedido_id>/estado", methods=["POST"])
def estado(pedido_id):
    con = obtener_conexion()
    try:
        cambiar_estado(con, pedido_id, request.form.get("estado", ""))
    except ErrorVenta:
        pass
    finally:
        con.close()
    return redirect(url_for("ventas.ver", pedido_id=pedido_id, aviso="estado"))


@bp.route("/<int:pedido_id>/eliminar", methods=["POST"])
def eliminar(pedido_id):
    con = obtener_conexion()
    try:
        eliminar_pedido(con, pedido_id)
    finally:
        con.close()
    return redirect(url_for("ventas.lista", aviso="eliminado"))


# FIN routes/ventas.py
