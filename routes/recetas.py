from decimal import InvalidOperation

from flask import Blueprint, abort, redirect, render_template, request, url_for

from database.db import obtener_conexion
from services.gastos import leer_gastos
from services.margenes import calcular_precios_venta, leer_margenes, leer_redondeo
from services.numeros import leer_decimal
from services.recetas import ErrorReceta, calcular_receta, validar_ingredientes

bp = Blueprint("recetas", __name__, url_prefix="/recetas")

COLORES_MARGEN = ["#16a34a", "#2563eb", "#7c3aed"]

AVISOS = {
    "creado": "Receta creada correctamente.",
    "editado": "Cambios guardados correctamente.",
    "eliminado": "Receta eliminada.",
    "con_fabricados": "No se puede eliminar: la receta se usa en productos fabricados.",
}


def cargar_listas(con):
    return {
        "unidades": [dict(f) for f in con.execute(
            "SELECT * FROM unidades ORDER BY tipo, nombre")],
        "productos": [dict(f) for f in con.execute(
            "SELECT p.id, p.nombre, p.unidad_compra_id, p.unidad_uso_id, p.precio_actual,"
            "       u.abreviatura AS abrev_compra "
            "FROM productos p JOIN unidades u ON u.id = p.unidad_compra_id "
            "ORDER BY p.nombre")],
    }


@bp.route("/")
def lista():
    aviso = AVISOS.get(request.args.get("aviso", ""))
    con = obtener_conexion()
    try:
        recetas = con.execute("SELECT * FROM recetas ORDER BY nombre").fetchall()
        unidades = {f["id"]: f for f in con.execute("SELECT * FROM unidades")}
        filas = []
        for receta in recetas:
            calculo = calcular_receta(con, receta["id"], unidades=unidades)
            filas.append({
                "id": receta["id"],
                "nombre": receta["nombre"],
                "rendimiento_cantidad": receta["rendimiento_cantidad"],
                "rendimiento_unidad": receta["rendimiento_unidad"],
                "total": calculo["total"],
                "costo_unidad": calculo["costo_unidad"],
                "n_ingredientes": len(calculo["lineas"]),
            })
    finally:
        con.close()
    return render_template("recetas_lista.html", seccion="recetas",
                           recetas=filas, aviso=aviso)


def _leer_datos():
    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
        "rendimiento_cantidad": request.form.get("rendimiento_cantidad", "").strip(),
        "rendimiento_unidad": request.form.get("rendimiento_unidad", "").strip() or "unidades",
        "notas": request.form.get("notas", "").strip(),
    }
    try:
        rendimiento = leer_decimal(datos["rendimiento_cantidad"])
    except (InvalidOperation, ValueError):
        return datos, "El rendimiento debe ser un número. Ejemplo: 10 o 10,5."
    if rendimiento <= 0:
        return datos, "El rendimiento tiene que ser mayor a cero."
    datos["rendimiento_cantidad"] = rendimiento
    return datos, None


def _leer_ingredientes():
    ids = request.form.getlist("producto_id")
    cantidades = request.form.getlist("cantidad")
    unidades = request.form.getlist("unidad_id")

    ingredientes = []
    for producto, cantidad, unidad in zip(ids, cantidades, unidades):
        if not producto:
            continue
        if not unidad:
            return None, "Elegí la unidad de cada ingrediente."
        try:
            cant = leer_decimal(cantidad)
        except (InvalidOperation, ValueError):
            return None, "La cantidad debe ser un número. Ejemplo: 300 o 300,5."
        ingredientes.append({
            "producto_id": int(producto),
            "cantidad": cant,
            "unidad_id": int(unidad),
        })

    if not ingredientes:
        return None, "Agregá al menos un ingrediente."
    return ingredientes, None


def _ingredientes_mostrados():
    ids = request.form.getlist("producto_id")
    cantidades = request.form.getlist("cantidad")
    unidades = request.form.getlist("unidad_id")
    filas = []
    for producto, cantidad, unidad in zip(ids, cantidades, unidades):
        if not producto and not cantidad:
            continue
        filas.append({"producto_id": producto, "cantidad": cantidad, "unidad_id": unidad})
    return filas


def _guardar(con, receta_id, datos, ingredientes):
    valores = (datos["nombre"], datos["descripcion"],
               float(datos["rendimiento_cantidad"]), datos["rendimiento_unidad"],
               datos["notas"])
    if receta_id is None:
        receta_id = con.execute(
            "INSERT INTO recetas"
            " (nombre, descripcion, rendimiento_cantidad, rendimiento_unidad, notas)"
            " VALUES (?, ?, ?, ?, ?)", valores).lastrowid
    else:
        con.execute(
            "UPDATE recetas SET nombre = ?, descripcion = ?, rendimiento_cantidad = ?,"
            " rendimiento_unidad = ?, notas = ? WHERE id = ?", valores + (receta_id,))
        con.execute("DELETE FROM receta_ingredientes WHERE receta_id = ?", (receta_id,))

    for item in ingredientes:
        con.execute(
            "INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad_id)"
            " VALUES (?, ?, ?, ?)",
            (receta_id, item["producto_id"], float(item["cantidad"]), item["unidad_id"]))
    con.commit()
    return receta_id


@bp.route("/nueva", methods=["GET", "POST"])
def nueva():
    con = obtener_conexion()
    datos = {"nombre": "", "descripcion": "", "rendimiento_cantidad": "",
             "rendimiento_unidad": "unidades", "notas": ""}
    ingredientes = []
    error = None
    try:
        if request.method == "POST":
            datos, error = _leer_datos()
            if error is None:
                ingredientes, error = _leer_ingredientes()
            if error is None and not datos["nombre"]:
                error = "El nombre de la receta es obligatorio."
            if error is None:
                error = validar_ingredientes(con, ingredientes)
            if error is None:
                receta_id = _guardar(con, None, datos, ingredientes)
                return redirect(url_for("recetas.ver", receta_id=receta_id, aviso="creado"))
            ingredientes = _ingredientes_mostrados()
        listas = cargar_listas(con)
    finally:
        con.close()
    return render_template("recetas_form.html", seccion="recetas", datos=datos,
                           ingredientes=ingredientes, error=error, editando=False,
                           receta_id=None, **listas)


@bp.route("/<int:receta_id>")
def ver(receta_id):
    con = obtener_conexion()
    try:
        calculo = calcular_receta(con, receta_id)
        gastos = leer_gastos(con)
        margenes = leer_margenes(con)
        redondeo = leer_redondeo(con)
        precio = calcular_precios_venta(
            calculo["costo_unidad"], gastos, margenes, redondeo)
    except ErrorReceta:
        abort(404)
    finally:
        con.close()
    return render_template("recetas_ver.html", seccion="recetas", calculo=calculo,
                           margenes=margenes, precio=precio, colores=COLORES_MARGEN,
                           aviso=AVISOS.get(request.args.get("aviso", "")))


def _datos_de_receta(receta):
    return {
        "nombre": receta["nombre"],
        "descripcion": receta["descripcion"] or "",
        "rendimiento_cantidad": ("%g" % receta["rendimiento_cantidad"]),
        "rendimiento_unidad": receta["rendimiento_unidad"] or "unidades",
        "notas": receta["notas"] or "",
    }


@bp.route("/<int:receta_id>/editar", methods=["GET", "POST"])
def editar(receta_id):
    con = obtener_conexion()
    error = None
    try:
        receta = con.execute("SELECT * FROM recetas WHERE id = ?", (receta_id,)).fetchone()
        if receta is None:
            abort(404)
        datos = _datos_de_receta(receta)
        ingredientes = [
            {"producto_id": str(f["producto_id"]), "cantidad": ("%g" % f["cantidad"]),
             "unidad_id": str(f["unidad_id"])}
            for f in con.execute(
                "SELECT producto_id, cantidad, unidad_id FROM receta_ingredientes"
                " WHERE receta_id = ? ORDER BY id", (receta_id,))
        ]
        if request.method == "POST":
            datos, error = _leer_datos()
            if error is None:
                ingredientes, error = _leer_ingredientes()
            if error is None and not datos["nombre"]:
                error = "El nombre de la receta es obligatorio."
            if error is None:
                error = validar_ingredientes(con, ingredientes)
            if error is None:
                _guardar(con, receta_id, datos, ingredientes)
                return redirect(url_for("recetas.ver", receta_id=receta_id, aviso="editado"))
            ingredientes = _ingredientes_mostrados()
        listas = cargar_listas(con)
    finally:
        con.close()
    return render_template("recetas_form.html", seccion="recetas", datos=datos,
                           ingredientes=ingredientes, error=error, editando=True,
                           receta_id=receta_id, **listas)


@bp.route("/<int:receta_id>/eliminar", methods=["POST"])
def eliminar(receta_id):
    con = obtener_conexion()
    try:
        receta = con.execute(
            "SELECT id FROM recetas WHERE id = ?", (receta_id,)).fetchone()
        if receta is None:
            abort(404)
        usos = con.execute(
            "SELECT COUNT(*) FROM productos_fabricados WHERE receta_id = ?",
            (receta_id,)).fetchone()[0]
        if usos:
            aviso = "con_fabricados"
        else:
            con.execute("DELETE FROM recetas WHERE id = ?", (receta_id,))
            con.commit()
            aviso = "eliminado"
    finally:
        con.close()
    return redirect(url_for("recetas.lista", aviso=aviso))


# FIN routes/recetas.py
