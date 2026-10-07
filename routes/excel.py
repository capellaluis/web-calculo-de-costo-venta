from datetime import date
from pathlib import Path

from flask import Blueprint, render_template, send_file

from database.db import obtener_conexion
from services.exportar_excel import construir_libro

bp = Blueprint("excel", __name__, url_prefix="/excel")

CARPETA_EXPORTS = Path(__file__).resolve().parent.parent / "exports"


@bp.route("/")
def inicio():
    return render_template("excel.html", seccion="excel")


@bp.route("/descargar")
def descargar():
    con = obtener_conexion()
    try:
        libro = construir_libro(con)
    finally:
        con.close()

    CARPETA_EXPORTS.mkdir(parents=True, exist_ok=True)
    nombre = "Mi_Negocio_%s.xlsx" % date.today().isoformat()
    ruta = CARPETA_EXPORTS / nombre
    libro.save(ruta)
    return send_file(ruta, as_attachment=True, download_name=nombre)


# FIN routes/excel.py
