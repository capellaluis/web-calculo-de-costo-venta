from decimal import InvalidOperation

from flask import Blueprint, redirect, render_template, request, url_for

from database.db import obtener_conexion
from services.costos import ranking_ingredientes, resumen_recetas
from services.fabricados import (
    calcular_fabricado,
    guardar_config_fabricado,
    sembrar_config_fabricado,
    tiene_config,
)
from services.margenes import leer_redondeo
from services.numeros import leer_decimal

bp = Blueprint("costos", __name__, url_prefix="/costos")


def _leer_filas(nombre_campo, pct_campo, etiqueta):
    nombres = request.form.getlist(nombre_campo)
    porcentajes = request.form.getlist(pct_campo)
    filas = []
    for nombre, texto in zip(nombres, porcentajes):
        if not nombre.strip() and not texto.strip():
            continue
        try:
            porcentaje = leer_decimal(texto)
        except (InvalidOperation, ValueError):
            return None, "Los porcentajes de %s deben ser números." % etiqueta
        filas.append({"nombre": nombre.strip(), "porcentaje": porcentaje})
    return filas, None


def _leer_config_form():
    gastos, error = _leer_filas("gasto_nombre", "gasto_porcentaje", "gastos")
    if error:
        return None, error
    delivery, error = _leer_filas("del_nombre", "del_porcentaje", "delivery")
    if error:
        return None, error

    elegido = request.form.get("margen_elegido", "1")
    margenes = []
    for numero in (1, 2, 3):
        nombre = request.form.get("margen%d_nombre" % numero, "").strip()
        try:
            porcentaje = leer_decimal(
                request.form.get("margen%d_porcentaje" % numero, ""))
        except (InvalidOperation, ValueError):
            return None, "Los porcentajes de los márgenes deben ser números."
        margenes.append({"numero": numero, "nombre": nombre, "porcentaje": porcentaje,
                         "elegido": 1 if str(numero) == elegido else 0})
    return {"gastos": gastos, "margenes": margenes, "delivery": delivery}, None


def _validar(config):
    for gasto in config["gastos"]:
        if gasto["porcentaje"] < 0:
            return "Los gastos no pueden ser negativos."
    for margen in config["margenes"]:
        if margen["porcentaje"] < 0 or margen["porcentaje"] >= 100:
            return "Cada margen de ganancia debe estar entre 0 y 99,99 %."
    suma_delivery = 0
    for item in config["delivery"]:
        if item["porcentaje"] < 0:
            return "Los porcentajes de delivery no pueden ser negativos."
        suma_delivery += item["porcentaje"]
    if suma_delivery >= 100:
        return "La suma de los % de delivery debe ser menor a 100 %."
    return None


def _contexto(con, seleccionado, config_override=None, error=None, aviso=None):
    fabricados = [{"id": f["id"], "nombre": f["nombre"]}
                  for f in con.execute("SELECT id, nombre FROM productos_fabricados ORDER BY nombre")]
    calculo = None
    if fabricados:
        ids = [str(f["id"]) for f in fabricados]
        if seleccionado not in ids:
            seleccionado = ids[0]
        if not tiene_config(con, int(seleccionado)):
            sembrar_config_fabricado(con, int(seleccionado))
        calculo = calcular_fabricado(con, int(seleccionado))
        if config_override is not None:
            calculo["config"] = config_override
    ingredientes, total = ranking_ingredientes(con)
    return {
        "fabricados": fabricados,
        "seleccionado": seleccionado,
        "calculo": calculo,
        "recetas": resumen_recetas(con),
        "ingredientes": ingredientes,
        "total": total,
        "redondeo": leer_redondeo(con),
        "error": error,
        "aviso": aviso,
    }


@bp.route("/")
def lista():
    aviso = ("Configuración guardada. Precios actualizados."
             if request.args.get("aviso") == "guardado" else None)
    con = obtener_conexion()
    try:
        contexto = _contexto(con, request.args.get("fabricado", "").strip(), aviso=aviso)
    finally:
        con.close()
    return render_template("costos_lista.html", seccion="costos", **contexto)


@bp.route("/guardar", methods=["POST"])
def guardar():
    fabricado_id = request.form.get("fabricado_id", "").strip()
    config, error = _leer_config_form()
    if error is None:
        error = _validar(config)

    con = obtener_conexion()
    try:
        if error is None and fabricado_id.isdigit():
            guardar_config_fabricado(con, int(fabricado_id), config["gastos"],
                                     config["margenes"], config["delivery"])
            return redirect(url_for("costos.lista", fabricado=fabricado_id,
                                    aviso="guardado"))
        contexto = _contexto(con, fabricado_id, config_override=config, error=error)
    finally:
        con.close()
    return render_template("costos_lista.html", seccion="costos", **contexto)


# FIN routes/costos.py
