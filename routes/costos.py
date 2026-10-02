from flask import Blueprint, render_template

from database.db import obtener_conexion
from services.costos import ranking_ingredientes, resumen_recetas

bp = Blueprint("costos", __name__, url_prefix="/costos")


@bp.route("/")
def lista():
    con = obtener_conexion()
    try:
        unidades = {fila["id"]: fila for fila in con.execute("SELECT * FROM unidades")}
        recetas = resumen_recetas(con, unidades=unidades)
        ingredientes, total = ranking_ingredientes(con, unidades=unidades)
    finally:
        con.close()

    promedio = (total / len(recetas)) if recetas else 0
    return render_template("costos_lista.html", seccion="costos",
                           recetas=recetas, ingredientes=ingredientes,
                           total=total, promedio=promedio)


# FIN routes/costos.py
