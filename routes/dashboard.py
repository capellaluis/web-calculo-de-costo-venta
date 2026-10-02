from flask import Blueprint, render_template

from database.db import obtener_conexion
from services.precios import productos_con_aumento

bp = Blueprint("dashboard", __name__)

NOMBRES_MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def etiqueta_mes(texto):
    # Convierte "2026-09" en "Sep 2026"
    anio, mes = texto.split("-")
    return NOMBRES_MESES[int(mes) - 1] + " " + anio


@bp.route("/")
def inicio():
    con = obtener_conexion()
    try:
        def uno(sql):
            return con.execute(sql).fetchone()[0]

        stats = {
            "proveedores": uno("SELECT COUNT(*) FROM proveedores"),
            "compras_mes": uno(
                "SELECT COALESCE(SUM(total), 0) FROM compras "
                "WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')"
            ),
            "productos": uno("SELECT COUNT(*) FROM productos"),
            "recetas": uno("SELECT COUNT(*) FROM recetas"),
            "fabricados": uno("SELECT COUNT(*) FROM productos_fabricados"),
            "costo_total": uno("SELECT COALESCE(SUM(total), 0) FROM compras"),
        }
# (aqui termina la parte 1)

        filas_meses = con.execute(
            "SELECT strftime('%Y-%m', fecha) AS mes, SUM(total) AS total "
            "FROM compras GROUP BY mes ORDER BY mes DESC LIMIT 6"
        ).fetchall()
        filas_meses = list(reversed(filas_meses))

        filas_top = con.execute(
            "SELECT p.nombre AS nombre, COUNT(*) AS veces "
            "FROM detalle_compras d JOIN productos p ON p.id = d.producto_id "
            "GROUP BY p.id ORDER BY veces DESC LIMIT 5"
        ).fetchall()

        filas_cat = con.execute(
            "SELECT COALESCE(c.nombre, 'Sin categoría') AS categoria, "
            "SUM(d.precio_total) AS total "
            "FROM detalle_compras d "
            "JOIN productos p ON p.id = d.producto_id "
            "LEFT JOIN categorias c ON c.id = p.categoria_id "
            "GROUP BY categoria ORDER BY total DESC"
        ).fetchall()

        aumentos = productos_con_aumento(con, limite=5)
# (aqui termina la parte 2a)
    finally:
        con.close()

    graficos = {
        "meses": {
            "etiquetas": [etiqueta_mes(f["mes"]) for f in filas_meses],
            "valores": [round(f["total"], 2) for f in filas_meses],
        },
        "top": {
            "etiquetas": [f["nombre"] for f in filas_top],
            "valores": [f["veces"] for f in filas_top],
        },
        "categorias": {
            "etiquetas": [f["categoria"] for f in filas_cat],
            "valores": [round(f["total"], 2) for f in filas_cat],
        },
    }

    return render_template("dashboard.html", seccion="dashboard",
                           stats=stats, graficos=graficos, aumentos=aumentos)


# FIN dashboard.py
