from decimal import InvalidOperation

from flask import Blueprint, redirect, render_template, request, url_for

from database.db import obtener_conexion
from services.fabricados import guardar_plantilla, leer_plantilla
from services.margenes import REDONDEOS, ErrorMargen, calcular_precio, leer_redondeo, guardar_redondeo
from services.numeros import leer_decimal

bp = Blueprint("configuracion", __name__, url_prefix="/config")

COSTO_EJEMPLO = 500


def _leer_filas(nombre_campo, pct_campo, etiqueta):
    nombres = request.form.getlist(nombre_campo)
    porcentajes = request.form.getlist(pct_campo)
    filas = []
    for nombre, texto in zip(nombres, porcentajes):
        if not nombre.strip() and not texto.strip():
            continue
        try:
            valor = leer_decimal(texto)
        except (InvalidOperation, ValueError):
            return None, "Los porcentajes de %s deben ser números." % etiqueta
        filas.append({"nombre": nombre.strip(), "porcentaje": valor})
    return filas, None


def _leer_config():
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
    suma = 0
    for item in config["delivery"]:
        if item["porcentaje"] < 0:
            return "Los porcentajes de delivery no pueden ser negativos."
        suma += item["porcentaje"]
    if suma >= 100:
        return "La suma de los % de delivery debe ser menor a 100 %."
    return None


def _margen_elegido_pct(margenes):
    for margen in margenes:
        if margen.get("elegido"):
            return margen["porcentaje"]
    return margenes[0]["porcentaje"] if margenes else 0


@bp.route("/", methods=["GET", "POST"])
def inicio():
    con = obtener_conexion()
    error = None
    try:
        if request.method == "POST":
            redondeo = request.form.get("redondeo", "entero")
            config, error = _leer_config()
            if error is None:
                error = _validar(config)
            if error is None:
                try:
                    guardar_plantilla(con, config["gastos"], config["margenes"],
                                      config["delivery"])
                    guardar_redondeo(con, redondeo)
                    return redirect(url_for("configuracion.inicio", aviso="guardado"))
                except ErrorMargen as exc:
                    error = str(exc)
            plantilla = config or leer_plantilla(con)
        else:
            plantilla = leer_plantilla(con)
            redondeo = leer_redondeo(con)

        try:
            ejemplo = leer_decimal(request.form.get("costo_ejemplo", "")) or COSTO_EJEMPLO
        except (InvalidOperation, ValueError):
            ejemplo = COSTO_EJEMPLO
        preview = calcular_precio(ejemplo, plantilla["gastos"],
                                  _margen_elegido_pct(plantilla["margenes"]),
                                  plantilla["delivery"], redondeo)
    finally:
        con.close()

    aviso = ("Valores por defecto guardados."
             if request.args.get("aviso") == "guardado" else None)
    return render_template("config_margenes.html", seccion="config",
                           gastos=plantilla["gastos"], margenes=plantilla["margenes"],
                           delivery=plantilla["delivery"], redondeo=redondeo,
                           redondeos=REDONDEOS, ejemplo=ejemplo, preview=preview,
                           error=error, aviso=aviso)


# FIN routes/configuracion.py
