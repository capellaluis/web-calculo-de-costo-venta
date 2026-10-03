from decimal import InvalidOperation

from flask import Blueprint, redirect, render_template, request, url_for

from database.db import obtener_conexion
from services.gastos import ErrorGasto, guardar_gastos, leer_gastos
from services.margenes import (
    REDONDEOS,
    ErrorMargen,
    calcular_precios_venta,
    guardar_margenes,
    leer_margenes,
    leer_redondeo,
)
from services.numeros import leer_decimal

bp = Blueprint("configuracion", __name__, url_prefix="/config")

COSTO_EJEMPLO = 500


def _leer_gastos():
    nombres = request.form.getlist("gasto_nombre")
    porcentajes = request.form.getlist("gasto_porcentaje")
    gastos = []
    for nombre, texto in zip(nombres, porcentajes):
        nombre = nombre.strip()
        if not nombre and not texto.strip():
            continue
        try:
            gastos.append({"nombre": nombre, "porcentaje": leer_decimal(texto)})
        except (InvalidOperation, ValueError):
            return None, "Los porcentajes de gastos deben ser números. Ejemplo: 5 o 5,5."
    return gastos, None


def _leer_margenes():
    margenes = []
    for numero in (1, 2, 3):
        nombre = request.form.get("margen%d_nombre" % numero, "").strip()
        try:
            porcentaje = leer_decimal(
                request.form.get("margen%d_porcentaje" % numero, ""))
        except (InvalidOperation, ValueError):
            return None, "Los porcentajes de los márgenes deben ser números."
        margenes.append({"numero": numero, "nombre": nombre, "porcentaje": porcentaje})
    return margenes, None


def _preview(costo, gastos, margenes, redondeo):
    try:
        return calcular_precios_venta(costo, gastos, margenes, redondeo)
    except ErrorMargen:
        return None


@bp.route("/", methods=["GET", "POST"])
def inicio():
    con = obtener_conexion()
    error = None
    try:
        if request.method == "POST":
            try:
                ejemplo = leer_decimal(request.form.get("costo_ejemplo", "")) or COSTO_EJEMPLO
            except (InvalidOperation, ValueError):
                ejemplo = COSTO_EJEMPLO
            redondeo = request.form.get("redondeo", "entero")
            gastos, error = _leer_gastos()
            margenes = None
            if error is None:
                margenes, error = _leer_margenes()
            if error is None:
                for gasto in gastos:
                    if gasto["porcentaje"] < 0:
                        error = "Los gastos no pueden ser negativos."
                        break
            if error is None:
                for margen in margenes:
                    if margen["porcentaje"] < 0 or margen["porcentaje"] >= 100:
                        error = "Cada margen de ganancia debe estar entre 0 y 99,99 %."
                        break
            if error is None:
                try:
                    guardar_margenes(con, margenes, redondeo)
                    guardar_gastos(con, gastos)
                    if request.form.get("destino") == "costos":
                        return redirect(url_for("costos.lista", aviso="guardado"))
                    return redirect(url_for("configuracion.inicio", aviso="guardado"))
                except (ErrorMargen, ErrorGasto) as exc:
                    error = str(exc)
        else:
            gastos = leer_gastos(con)
            margenes = leer_margenes(con)
            redondeo = leer_redondeo(con)
            try:
                ejemplo = leer_decimal(request.args.get("ejemplo", "")) or COSTO_EJEMPLO
            except (InvalidOperation, ValueError):
                ejemplo = COSTO_EJEMPLO

        if gastos is None:
            gastos = leer_gastos(con)
        if margenes is None:
            margenes = leer_margenes(con)
        preview = _preview(ejemplo, gastos, margenes, redondeo)
    finally:
        con.close()

    aviso = ("Cambios guardados correctamente."
             if request.args.get("aviso") == "guardado" else None)
    return render_template("config_margenes.html", seccion="config",
                           gastos=gastos, margenes=margenes, redondeo=redondeo,
                           redondeos=REDONDEOS, ejemplo=ejemplo, preview=preview,
                           error=error, aviso=aviso)


# FIN routes/configuracion.py
