from flask import Blueprint, render_template, request

from database.db import obtener_conexion
from services.costos import ranking_ingredientes, resumen_recetas
from services.gastos import leer_gastos
from services.margenes import (
    REDONDEOS,
    calcular_precios_venta,
    leer_margenes,
    leer_redondeo,
)

bp = Blueprint("costos", __name__, url_prefix="/costos")

COLORES_MARGEN = ["#16a34a", "#2563eb", "#7c3aed"]
COSTO_EJEMPLO = 500


@bp.route("/")
def lista():
    aviso = ("Cambios guardados. Los precios se recalcularon."
             if request.args.get("aviso") == "guardado" else None)
    con = obtener_conexion()
    try:
        unidades = {fila["id"]: fila for fila in con.execute("SELECT * FROM unidades")}
        recetas = resumen_recetas(con, unidades=unidades)
        ingredientes, total = ranking_ingredientes(con, unidades=unidades)
        gastos = leer_gastos(con)
        margenes = leer_margenes(con)
        redondeo = leer_redondeo(con)
        for receta in recetas:
            receta["precio"] = calcular_precios_venta(
                receta["costo_unidad"], gastos, margenes, redondeo)
        preview = calcular_precios_venta(COSTO_EJEMPLO, gastos, margenes, redondeo)
    finally:
        con.close()

    promedio = (total / len(recetas)) if recetas else 0
    return render_template("costos_lista.html", seccion="costos",
                           recetas=recetas, ingredientes=ingredientes,
                           total=total, promedio=promedio,
                           gastos=gastos, margenes=margenes, redondeo=redondeo,
                           redondeos=REDONDEOS, ejemplo=COSTO_EJEMPLO,
                           preview=preview, colores=COLORES_MARGEN, aviso=aviso)


# FIN routes/costos.py
