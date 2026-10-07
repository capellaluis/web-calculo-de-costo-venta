from pathlib import Path

from flask import Blueprint, abort, redirect, render_template, request, send_file, url_for

from services.copias import (
    LIMITE_COPIAS,
    borrar_copia,
    carpeta_backups,
    crear_copia,
    limitar_copias,
    listar_copias,
    restaurar_copia,
)

bp = Blueprint("copias", __name__, url_prefix="/copias")

AVISOS = {
    "creada": "Copia creada correctamente.",
    "restaurada": "Copia restaurada. Los datos volvieron a ese momento.",
    "eliminada": "Copia eliminada.",
    "error": "No se encontró esa copia.",
}


@bp.route("/")
def inicio():
    aviso = AVISOS.get(request.args.get("aviso", ""))
    return render_template("copias.html", seccion="config", copias=listar_copias(),
                           aviso=aviso, limite=LIMITE_COPIAS)


@bp.route("/crear", methods=["POST"])
def crear():
    crear_copia()
    limitar_copias()
    return redirect(url_for("copias.inicio", aviso="creada"))


@bp.route("/descargar/<nombre>")
def descargar(nombre):
    ruta = carpeta_backups() / Path(nombre).name
    if not ruta.exists():
        abort(404)
    return send_file(ruta, as_attachment=True, download_name=ruta.name)


@bp.route("/restaurar", methods=["POST"])
def restaurar():
    ruta = carpeta_backups() / Path(request.form.get("nombre", "")).name
    if not ruta.exists():
        return redirect(url_for("copias.inicio", aviso="error"))
    restaurar_copia(ruta)
    return redirect(url_for("copias.inicio", aviso="restaurada"))


@bp.route("/eliminar", methods=["POST"])
def eliminar():
    borrar_copia(request.form.get("nombre", ""))
    return redirect(url_for("copias.inicio", aviso="eliminada"))


# FIN routes/copias.py
