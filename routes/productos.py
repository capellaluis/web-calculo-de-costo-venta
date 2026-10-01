from flask import Blueprint, render_template, request, redirect, url_for, abort

from database.db import obtener_conexion

bp = Blueprint("productos", __name__, url_prefix="/productos")

AVISOS = {
    "creado": "Producto creado correctamente.",
    "editado": "Cambios guardados correctamente.",
    "eliminado": "Producto eliminado.",
    "con_compras": "No se puede eliminar: el producto tiene compras o recetas registradas.",
}


@bp.route("/")
def lista():
    busqueda = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    aviso = AVISOS.get(request.args.get("aviso", ""))
    sql = (
        "SELECT p.*, c.nombre AS categoria, uc.abreviatura AS unidad_compra, "
        "uu.abreviatura AS unidad_uso, pr.nombre AS proveedor "
        "FROM productos p "
        "LEFT JOIN categorias c ON c.id = p.categoria_id "
        "JOIN unidades uc ON uc.id = p.unidad_compra_id "
        "JOIN unidades uu ON uu.id = p.unidad_uso_id "
        "LEFT JOIN proveedores pr ON pr.id = p.proveedor_principal_id WHERE 1 = 1"
    )
    params = []
    if busqueda:
        sql += " AND (p.nombre LIKE ? OR p.sku LIKE ?)"
        params += ["%" + busqueda + "%"] * 2
    if categoria:
        sql += " AND c.nombre = ?"
        params.append(categoria)
    sql += " ORDER BY p.nombre"
    con = obtener_conexion()
    try:
        filas = con.execute(sql, params).fetchall()
        categorias = con.execute("SELECT nombre FROM categorias ORDER BY nombre").fetchall()
    finally:
        con.close()
    return render_template("productos_lista.html", seccion="productos",
                           productos=filas, categorias=categorias,
                           busqueda=busqueda, categoria=categoria, aviso=aviso)
# (aqui termina la parte 1)


COLUMNAS = ["nombre", "categoria_id", "unidad_compra_id", "unidad_uso_id",
            "precio_actual", "proveedor_principal_id", "sku", "notas"]


def cargar_listas(con):
    return {
        "unidades": con.execute(
            "SELECT * FROM unidades ORDER BY tipo, nombre").fetchall(),
        "proveedores": con.execute(
            "SELECT id, nombre FROM proveedores ORDER BY nombre").fetchall(),
        "categorias": con.execute(
            "SELECT nombre FROM categorias ORDER BY nombre").fetchall(),
    }


def leer_formulario():
    campos = ["nombre", "categoria", "unidad_compra_id", "unidad_uso_id",
              "precio_actual", "proveedor_principal_id", "sku", "notas"]
    return {c: request.form.get(c, "").strip() for c in campos}


def leer_precio(texto):
    texto = texto.replace("$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto or 0)


def id_categoria(con, nombre):
    if not nombre:
        return None
    fila = con.execute(
        "SELECT id FROM categorias WHERE nombre = ? COLLATE NOCASE",
        (nombre,)).fetchone()
    if fila:
        return fila["id"]
    cursor = con.execute(
        "INSERT INTO categorias (nombre) VALUES (?)", (nombre,))
    return cursor.lastrowid


def validar(con, datos):
    """Devuelve (mensaje_de_error, precio). Si todo está bien, el error es None."""
    if not datos["nombre"]:
        return "El nombre es obligatorio.", None
    try:
        precio = leer_precio(datos["precio_actual"])
    except ValueError:
        return "El precio debe ser un número. Ejemplo: 1200 o 1200,50.", None
    if precio < 0:
        return "El precio no puede ser negativo.", None
    if not datos["unidad_compra_id"] or not datos["unidad_uso_id"]:
        return "Elige la unidad de compra y la unidad de uso.", None
    sql = "SELECT * FROM unidades WHERE id = ?"
    compra = con.execute(sql, (datos["unidad_compra_id"],)).fetchone()
    uso = con.execute(sql, (datos["unidad_uso_id"],)).fetchone()
    if compra is None or uso is None:
        return "La unidad elegida no es válida.", None
    if compra["tipo"] != uso["tipo"]:
        return ("La unidad de compra y la de uso deben ser compatibles "
                "(por ejemplo kg con g, o litro con ml)."), None
    if compra["tipo"] == "empaque" and compra["id"] != uso["id"]:
        return "Paquete y caja solo se pueden usar con la misma unidad.", None
    return None, precio


def valores_para_guardar(con, datos, precio):
    proveedor = datos["proveedor_principal_id"]
    return [
        datos["nombre"],
        id_categoria(con, datos["categoria"]),
        int(datos["unidad_compra_id"]),
        int(datos["unidad_uso_id"]),
        precio,
        int(proveedor) if proveedor else None,
        datos["sku"],
        datos["notas"],
    ]
# (aqui termina la parte 2a)


def registrar_precio(con, producto_id, precio, unidad_id):
    con.execute(
        "INSERT INTO historial_precios (producto_id, fecha, precio_unitario, unidad_id) "
        "VALUES (?, date('now', 'localtime'), ?, ?)",
        (producto_id, precio, unidad_id))


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    con = obtener_conexion()
    try:
        datos = leer_formulario()
        error = None
        if request.method == "POST":
            error, precio = validar(con, datos)
            if error is None:
                cursor = con.execute(
                    "INSERT INTO productos (" + ", ".join(COLUMNAS) + ") "
                    "VALUES (" + ", ".join("?" for _ in COLUMNAS) + ")",
                    valores_para_guardar(con, datos, precio))
                if precio > 0:
                    registrar_precio(con, cursor.lastrowid, precio,
                                     int(datos["unidad_compra_id"]))
                con.commit()
                return redirect(url_for("productos.lista", aviso="creado"))
        listas = cargar_listas(con)
    finally:
        con.close()
    return render_template("productos_form.html", seccion="productos",
                           datos=datos, error=error, editando=False,
                           producto_id=None, **listas)


def buscar_producto(con, producto_id):
    fila = con.execute(
        "SELECT p.*, c.nombre AS categoria, uc.nombre AS unidad_compra, "
        "uc.abreviatura AS abrev_compra, uu.nombre AS unidad_uso, "
        "pr.nombre AS proveedor "
        "FROM productos p "
        "LEFT JOIN categorias c ON c.id = p.categoria_id "
        "JOIN unidades uc ON uc.id = p.unidad_compra_id "
        "JOIN unidades uu ON uu.id = p.unidad_uso_id "
        "LEFT JOIN proveedores pr ON pr.id = p.proveedor_principal_id "
        "WHERE p.id = ?", (producto_id,)).fetchone()
    if fila is None:
        abort(404)
    return fila


@bp.route("/<int:producto_id>")
def ver(producto_id):
    con = obtener_conexion()
    try:
        producto = buscar_producto(con, producto_id)
        historial = con.execute(
            "SELECT h.fecha, h.precio_unitario, u.abreviatura AS unidad "
            "FROM historial_precios h JOIN unidades u ON u.id = h.unidad_id "
            "WHERE h.producto_id = ? ORDER BY h.fecha DESC, h.id DESC LIMIT 20",
            (producto_id,)).fetchall()
    finally:
        con.close()
    return render_template("productos_ver.html", seccion="productos",
                           producto=producto, historial=historial)
# (aqui termina la parte 2b)


@bp.route("/<int:producto_id>/editar", methods=["GET", "POST"])
def editar(producto_id):
    con = obtener_conexion()
    try:
        actual = buscar_producto(con, producto_id)
        datos = {
            "nombre": actual["nombre"],
            "categoria": actual["categoria"] or "",
            "unidad_compra_id": str(actual["unidad_compra_id"]),
            "unidad_uso_id": str(actual["unidad_uso_id"]),
            "precio_actual": "{:.2f}".format(actual["precio_actual"]).rstrip("0").rstrip(".").replace(".", ","),
            "proveedor_principal_id": str(actual["proveedor_principal_id"] or ""),
            "sku": actual["sku"] or "",
            "notas": actual["notas"] or "",
        }
        error = None
        if request.method == "POST":
            datos = leer_formulario()
            error, precio = validar(con, datos)
            if error is None:
                con.execute(
                    "UPDATE productos SET "
                    + ", ".join(c + " = ?" for c in COLUMNAS)
                    + " WHERE id = ?",
                    valores_para_guardar(con, datos, precio) + [producto_id])
                if precio > 0 and precio != actual["precio_actual"]:
                    registrar_precio(con, producto_id, precio,
                                     int(datos["unidad_compra_id"]))
                con.commit()
                return redirect(url_for("productos.lista", aviso="editado"))
        listas = cargar_listas(con)
    finally:
        con.close()
    return render_template("productos_form.html", seccion="productos",
                           datos=datos, error=error, editando=True,
                           producto_id=producto_id, **listas)


@bp.route("/<int:producto_id>/eliminar", methods=["POST"])
def eliminar(producto_id):
    con = obtener_conexion()
    try:
        buscar_producto(con, producto_id)
        usos = con.execute(
            "SELECT (SELECT COUNT(*) FROM detalle_compras WHERE producto_id = ?) "
            "+ (SELECT COUNT(*) FROM receta_ingredientes WHERE producto_id = ?)",
            (producto_id, producto_id)).fetchone()[0]
        if usos:
            aviso = "con_compras"
        else:
            con.execute("DELETE FROM historial_precios WHERE producto_id = ?", (producto_id,))
            con.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
            con.commit()
            aviso = "eliminado"
    finally:
        con.close()
    return redirect(url_for("productos.lista", aviso=aviso))


# FIN productos.py
