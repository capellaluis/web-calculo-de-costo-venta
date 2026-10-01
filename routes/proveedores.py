from flask import Blueprint, render_template, request, redirect, url_for, abort

from database.db import obtener_conexion

bp = Blueprint("proveedores", __name__, url_prefix="/proveedores")

CAMPOS = ["nombre", "razon_social", "cuit_rut", "telefono", "whatsapp",
          "email", "direccion", "persona_contacto", "notas"]

AVISOS = {
    "creado": "Proveedor creado correctamente.",
    "editado": "Cambios guardados correctamente.",
    "eliminado": "Proveedor eliminado.",
}


def leer_formulario():
    return {campo: request.form.get(campo, "").strip() for campo in CAMPOS}


@bp.route("/")
def lista():
    busqueda = request.args.get("q", "").strip()
    aviso = AVISOS.get(request.args.get("aviso", ""))
    con = obtener_conexion()
    try:
        if busqueda:
            patron = "%" + busqueda + "%"
            filas = con.execute(
                "SELECT * FROM proveedores WHERE nombre LIKE ? "
                "OR razon_social LIKE ? OR cuit_rut LIKE ? "
                "OR persona_contacto LIKE ? ORDER BY nombre",
                (patron, patron, patron, patron),
            ).fetchall()
        else:
            filas = con.execute(
                "SELECT * FROM proveedores ORDER BY nombre").fetchall()
    finally:
        con.close()
    return render_template("proveedores_lista.html", seccion="proveedores",
                           proveedores=filas, busqueda=busqueda, aviso=aviso)
# (aqui termina la parte 1)

@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    datos = {campo: "" for campo in CAMPOS}
    error = None
    if request.method == "POST":
        datos = leer_formulario()
        if not datos["nombre"]:
            error = "El nombre es obligatorio."
        else:
            con = obtener_conexion()
            try:
                con.execute(
                    "INSERT INTO proveedores (" + ", ".join(CAMPOS) + ") "
                    "VALUES (" + ", ".join("?" for _ in CAMPOS) + ")",
                    [datos[c] for c in CAMPOS],
                )
                con.commit()
            finally:
                con.close()
            return redirect(url_for("proveedores.lista", aviso="creado"))
    return render_template("proveedores_form.html", seccion="proveedores",
                           datos=datos, error=error, editando=False,
                           proveedor_id=None)


def buscar_proveedor(con, proveedor_id):
    fila = con.execute(
        "SELECT * FROM proveedores WHERE id = ?", (proveedor_id,)).fetchone()
    if fila is None:
        abort(404)
    return fila


@bp.route("/<int:proveedor_id>")
def ver(proveedor_id):
    con = obtener_conexion()
    try:
        proveedor = buscar_proveedor(con, proveedor_id)
        compras = con.execute(
            "SELECT id, fecha, numero_documento, total FROM compras "
            "WHERE proveedor_id = ? ORDER BY fecha DESC", (proveedor_id,)
        ).fetchall()
    finally:
        con.close()
    return render_template("proveedores_ver.html", seccion="proveedores",
                           proveedor=proveedor, compras=compras)
# (aqui termina la parte 2a)

AVISOS["con_compras"] = (
    "No se puede eliminar: el proveedor tiene compras registradas."
)


@bp.route("/<int:proveedor_id>/editar", methods=["GET", "POST"])
def editar(proveedor_id):
    con = obtener_conexion()
    try:
        proveedor = buscar_proveedor(con, proveedor_id)
        datos = {c: proveedor[c] or "" for c in CAMPOS}
        error = None
        if request.method == "POST":
            datos = leer_formulario()
            if not datos["nombre"]:
                error = "El nombre es obligatorio."
            else:
                con.execute(
                    "UPDATE proveedores SET "
                    + ", ".join(c + " = ?" for c in CAMPOS)
                    + " WHERE id = ?",
                    [datos[c] for c in CAMPOS] + [proveedor_id],
                )
                con.commit()
                return redirect(url_for("proveedores.lista", aviso="editado"))
    finally:
        con.close()
    return render_template("proveedores_form.html", seccion="proveedores",
                           datos=datos, error=error, editando=True,
                           proveedor_id=proveedor_id)


@bp.route("/<int:proveedor_id>/eliminar", methods=["POST"])
def eliminar(proveedor_id):
    con = obtener_conexion()
    try:
        buscar_proveedor(con, proveedor_id)
        compras = con.execute(
            "SELECT COUNT(*) FROM compras WHERE proveedor_id = ?",
            (proveedor_id,),
        ).fetchone()[0]
        if compras:
            aviso = "con_compras"
        else:
            con.execute(
                "UPDATE productos SET proveedor_principal_id = NULL "
                "WHERE proveedor_principal_id = ?", (proveedor_id,))
            con.execute("DELETE FROM proveedores WHERE id = ?", (proveedor_id,))
            con.commit()
            aviso = "eliminado"
    finally:
        con.close()
    return redirect(url_for("proveedores.lista", aviso=aviso))


# FIN proveedores.py
