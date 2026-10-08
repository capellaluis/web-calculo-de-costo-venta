from flask import Blueprint, redirect, render_template, request, session, url_for

from database.db import obtener_conexion
from services import correo
from services.negocio import leer_negocio
from services.usuarios import (
    MINUTOS_VIGENCIA,
    ErrorUsuario,
    cambiar_password,
    crear_usuario,
    generar_codigo_recuperacion,
    hay_usuario,
    leer_usuario,
    limpiar_codigo_recuperacion,
    verificar,
    verificar_codigo_recuperacion,
)

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    con = obtener_conexion()
    try:
        primer_uso = not hay_usuario(con)
        error = None
        if request.method == "POST":
            if primer_uso:
                usuario = request.form.get("usuario", "")
                password = request.form.get("password", "")
                repetir = request.form.get("password2", "")
                email = request.form.get("email", "")
                if password != repetir:
                    error = "Las contraseñas no coinciden."
                else:
                    try:
                        crear_usuario(con, usuario, password, email)
                        session.clear()
                        session["usuario"] = usuario.strip()
                        return redirect(url_for("dashboard.inicio"))
                    except ErrorUsuario as exc:
                        error = str(exc)
            else:
                if verificar(con, request.form.get("usuario", ""),
                             request.form.get("password", "")):
                    session.clear()
                    session["usuario"] = request.form.get("usuario", "").strip()
                    return redirect(url_for("dashboard.inicio"))
                error = "Usuario o contraseña incorrectos."
    finally:
        con.close()
    return render_template("login.html", primer_uso=primer_uso, error=error)


@bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


def _ocultar_email(email):
    if not email or "@" not in email:
        return email or "(sin correo)"
    usuario, dominio = email.split("@", 1)
    visible = usuario[:1]
    return "%s%s@%s" % (visible, "*" * max(len(usuario) - 1, 0), dominio)


@bp.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    con = obtener_conexion()
    try:
        if not hay_usuario(con):
            return redirect(url_for("auth.login"))
        datos = leer_usuario(con)
        email = datos["email"]
        error = None
        paso = "iniciar"
        if request.method == "POST":
            if not email:
                error = "No hay un correo guardado para recuperar el acceso."
            elif not correo.configurado(con):
                error = ("Todavía no está configurado el correo de envío "
                         "(Configuración → Correo).")
            else:
                codigo = generar_codigo_recuperacion(con)
                nombre = leer_negocio(con)["nombre"]
                cuerpo = (
                    "Hola.\n\n"
                    "Para recuperar el acceso a %s:\n\n"
                    "  Usuario: %s\n"
                    "  Código: %s\n\n"
                    "Escribí ese código en la pantalla de recuperación. "
                    "Vale por %d minutos.\n\n"
                    "Si no fuiste vos, ignorá este correo."
                ) % (nombre, datos["usuario"], codigo, MINUTOS_VIGENCIA)
                try:
                    correo.enviar(con, email, "Recuperar acceso - %s" % nombre, cuerpo)
                    paso = "codigo"
                except correo.ErrorCorreo as exc:
                    error = str(exc)
    finally:
        con.close()
    return render_template("recuperar.html", paso=paso, error=error,
                           email=_ocultar_email(email))


@bp.route("/recuperar/cambiar", methods=["POST"])
def recuperar_cambiar():
    con = obtener_conexion()
    try:
        if not hay_usuario(con):
            return redirect(url_for("auth.login"))
        datos = leer_usuario(con)
        email = datos["email"]
        paso = "codigo"
        error = None
        codigo = request.form.get("codigo", "")
        password = request.form.get("password", "")
        repetir = request.form.get("password2", "")

        if verificar_codigo_recuperacion(con, codigo):
            if password != repetir:
                error = "Las contraseñas no coinciden."
            else:
                try:
                    cambiar_password(con, password)
                    limpiar_codigo_recuperacion(con)
                    paso = "listo"
                except ErrorUsuario as exc:
                    error = str(exc)
        else:
            error = "Código incorrecto o vencido. Pedí uno nuevo."
    finally:
        con.close()
    return render_template("recuperar.html", paso=paso, error=error,
                           email=_ocultar_email(email),
                           usuario=datos["usuario"] if paso == "listo" else "")


# FIN routes/auth.py
