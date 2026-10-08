from datetime import date
from pathlib import Path

from flask import Blueprint, render_template, request, send_file

from database.db import obtener_conexion
from services.reportes import TIPOS, construir_reporte, reporte_a_libro
from services.ventas import CANALES, ESTADOS

bp = Blueprint("reportes", __name__, url_prefix="/reportes")

CARPETA_EXPORTS = Path(__file__).resolve().parent.parent / "exports"


def _filtros():
    return {
        "desde": request.args.get("desde", "").strip(),
        "hasta": request.args.get("hasta", "").strip(),
        "proveedor": request.args.get("proveedor", "").strip(),
        "producto": request.args.get("producto", "").strip(),
        "categoria": request.args.get("categoria", "").strip(),
        "canal": request.args.get("canal", "").strip(),
        "estado": request.args.get("estado", "").strip(),
        "cliente": request.args.get("cliente", "").strip(),
    }


def _tipo():
    tipo = request.args.get("tipo", "compras")
    return tipo if tipo in TIPOS else "compras"


@bp.route("/")
def inicio():
    tipo = _tipo()
    filtros = _filtros()
    con = obtener_conexion()
    try:
        reporte = construir_reporte(con, tipo, filtros)
        proveedores = [dict(f) for f in con.execute(
            "SELECT id, nombre FROM proveedores ORDER BY nombre")]
        productos = [dict(f) for f in con.execute(
            "SELECT id, nombre FROM productos ORDER BY nombre")]
        categorias = [f["nombre"] for f in con.execute(
            "SELECT nombre FROM categorias ORDER BY nombre")]
    finally:
        con.close()
    return render_template("reportes.html", seccion="reportes", tipo=tipo,
                           filtros=filtros, reporte=reporte, tipos=TIPOS,
                           proveedores=proveedores, productos=productos,
                           categorias=categorias, canales=CANALES, estados=ESTADOS)


@bp.route("/exportar")
def exportar():
    tipo = _tipo()
    filtros = _filtros()
    con = obtener_conexion()
    try:
        libro = reporte_a_libro(con, tipo, filtros)
    finally:
        con.close()

    CARPETA_EXPORTS.mkdir(parents=True, exist_ok=True)
    nombre = "Reporte_%s_%s.xlsx" % (tipo, date.today().isoformat())
    ruta = CARPETA_EXPORTS / nombre
    libro.save(ruta)
    return send_file(ruta, as_attachment=True, download_name=nombre)


# FIN routes/reportes.py
