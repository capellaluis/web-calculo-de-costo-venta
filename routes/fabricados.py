from decimal import InvalidOperation

from flask import Blueprint, abort, redirect, render_template, request, url_for

from database.db import obtener_conexion
from services.fabricados import (
    ErrorFabricado,
    calcular_fabricado,
    guardar_fabricado,
    presentaciones_de,
)
from services.gastos import leer_gastos
from services.margenes import REDONDEOS, leer_margenes, leer_redondeo
from services.numeros import leer_decimal
from services.recetas import calcular_receta

bp = Blueprint("fabricados", __name__, url_prefix="/fabricados")

AVISOS = {
    "creado": "Producto fabricado creado correctamente.",
    "editado": "Cambios guardados correctamente.",
    "eliminado": "Producto fabricado eliminado.",
}


def cargar_listas(con):
    unidades = {fila["id"]: fila for fila in con.execute("SELECT * FROM unidades")}
    recetas = []
    for receta in con.execute("SELECT id, nombre FROM recetas ORDER BY nombre"):
        total = calcular_receta(con, receta["id"], unidades=unidades)["total"]
        recetas.append({"id": receta["id"], "nombre": receta["nombre"],
                        "costo_total": float(total)})
    return {
        "recetas": recetas,
        "gastos": leer_gastos(con),
        "margenes": leer_margenes(con),
        "redondeo": leer_redondeo(con),
        "redondeos": REDONDEOS,
    }


@bp.route("/")
def lista():
    aviso = AVISOS.get(request.args.get("aviso", ""))
    con = obtener_conexion()
    try:
        gastos = leer_gastos(con)
        margenes = leer_margenes(con)
        redondeo = leer_redondeo(con)
        fabricados = [
            calcular_fabricado(con, fila["id"], gastos, margenes, redondeo)
            for fila in con.execute(
                "SELECT id FROM productos_fabricados ORDER BY nombre")
        ]
    finally:
        con.close()
    return render_template("fabricados_lista.html", seccion="fabricados",
                           fabricados=fabricados, aviso=aviso)


def _leer_datos():
    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "receta_id": request.form.get("receta_id", "").strip(),
        "cantidad_fabricada": request.form.get("cantidad_fabricada", "").strip(),
        "notas": request.form.get("notas", "").strip(),
    }
    try:
        datos["cantidad_fabricada"] = leer_decimal(datos["cantidad_fabricada"])
    except (InvalidOperation, ValueError):
        return datos, "La cantidad fabricada debe ser un número. Ejemplo: 20."
    return datos, None


def _leer_presentaciones():
    nombres = request.form.getlist("pres_nombre")
    cantidades = request.form.getlist("pres_cantidad")
    presentaciones = []
    for nombre, texto in zip(nombres, cantidades):
        if not nombre.strip() and not texto.strip():
            continue
        try:
            cantidad = leer_decimal(texto)
        except (InvalidOperation, ValueError):
            return None, "La cantidad de cada presentación debe ser un número."
        presentaciones.append({"nombre": nombre.strip(), "cantidad_unidades": cantidad})
    return presentaciones, None


def _presentaciones_mostradas():
    nombres = request.form.getlist("pres_nombre")
    cantidades = request.form.getlist("pres_cantidad")
    filas = []
    for nombre, cantidad in zip(nombres, cantidades):
        if not nombre and not cantidad:
            continue
        filas.append({"nombre": nombre, "cantidad_unidades": cantidad})
    return filas


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    con = obtener_conexion()
    datos = {"nombre": "", "receta_id": "", "cantidad_fabricada": "", "notas": ""}
    presentaciones = []
    error = None
    try:
        if request.method == "POST":
            datos, error = _leer_datos()
            if error is None:
                presentaciones, error = _leer_presentaciones()
            if error is None and not datos["receta_id"]:
                error = "Elegí una receta."
            if error is None:
                try:
                    fabricado_id = guardar_fabricado(con, None, datos, presentaciones)
                    return redirect(url_for("fabricados.ver",
                                            fabricado_id=fabricado_id, aviso="creado"))
                except ErrorFabricado as exc:
                    error = str(exc)
            presentaciones = _presentaciones_mostradas()
        listas = cargar_listas(con)
    finally:
        con.close()
    return render_template("fabricados_form.html", seccion="fabricados", datos=datos,
                           presentaciones=presentaciones, error=error, editando=False,
                           fabricado_id=None, **listas)


@bp.route("/<int:fabricado_id>")
def ver(fabricado_id):
    con = obtener_conexion()
    try:
        gastos = leer_gastos(con)
        margenes = leer_margenes(con)
        redondeo = leer_redondeo(con)
        calculo = calcular_fabricado(con, fabricado_id, gastos, margenes, redondeo)
    except ErrorFabricado:
        abort(404)
    finally:
        con.close()
    return render_template("fabricados_ver.html", seccion="fabricados", calculo=calculo,
                           aviso=AVISOS.get(request.args.get("aviso", "")))


@bp.route("/<int:fabricado_id>/editar", methods=["GET", "POST"])
def editar(fabricado_id):
    con = obtener_conexion()
    error = None
    try:
        fila = con.execute(
            "SELECT * FROM productos_fabricados WHERE id = ?", (fabricado_id,)).fetchone()
        if fila is None:
            abort(404)
        datos = {"nombre": fila["nombre"], "receta_id": str(fila["receta_id"]),
                 "cantidad_fabricada": ("%g" % fila["cantidad_fabricada"]),
                 "notas": fila["notas"] or ""}
        presentaciones = [
            {"nombre": p["nombre"], "cantidad_unidades": ("%g" % p["cantidad_unidades"])}
            for p in presentaciones_de(con, fabricado_id)
        ]
        if request.method == "POST":
            datos, error = _leer_datos()
            if error is None:
                presentaciones, error = _leer_presentaciones()
            if error is None and not datos["receta_id"]:
                error = "Elegí una receta."
            if error is None:
                try:
                    guardar_fabricado(con, fabricado_id, datos, presentaciones)
                    return redirect(url_for("fabricados.ver",
                                            fabricado_id=fabricado_id, aviso="editado"))
                except ErrorFabricado as exc:
                    error = str(exc)
            presentaciones = _presentaciones_mostradas()
        listas = cargar_listas(con)
    finally:
        con.close()
    return render_template("fabricados_form.html", seccion="fabricados", datos=datos,
                           presentaciones=presentaciones, error=error, editando=True,
                           fabricado_id=fabricado_id, **listas)


@bp.route("/<int:fabricado_id>/eliminar", methods=["POST"])
def eliminar(fabricado_id):
    con = obtener_conexion()
    try:
        fila = con.execute(
            "SELECT id FROM productos_fabricados WHERE id = ?", (fabricado_id,)).fetchone()
        if fila is None:
            abort(404)
        con.execute("DELETE FROM presentaciones WHERE producto_fabricado_id = ?",
                    (fabricado_id,))
        con.execute("DELETE FROM productos_fabricados WHERE id = ?", (fabricado_id,))
        con.commit()
    finally:
        con.close()
    return redirect(url_for("fabricados.lista", aviso="eliminado"))


# FIN routes/fabricados.py
