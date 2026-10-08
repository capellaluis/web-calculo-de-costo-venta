"""Envío de correos (para recuperar usuario/clave) usando SMTP.

Pensado para Gmail con "contraseña de aplicación" (smtp.gmail.com, puerto 587).
Los datos se guardan en la tabla `configuracion` (claves `smtp_*`).
"""

import smtplib
from email.mime.text import MIMEText

HOST_DEFECTO = "smtp.gmail.com"
PUERTO_DEFECTO = 587


class ErrorCorreo(ValueError):
    """Error de correo con mensaje en español para mostrar al usuario."""


def _guardar(con, clave, valor):
    con.execute(
        "INSERT INTO configuracion (clave, valor) VALUES (?, ?)"
        " ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor", (clave, valor))


def leer_config(con):
    filas = {fila["clave"]: fila["valor"] for fila in con.execute(
        "SELECT clave, valor FROM configuracion WHERE clave LIKE 'smtp_%'")}
    try:
        puerto = int(filas.get("smtp_puerto") or PUERTO_DEFECTO)
    except ValueError:
        puerto = PUERTO_DEFECTO
    usuario = filas.get("smtp_usuario", "")
    return {
        "host": filas.get("smtp_host") or HOST_DEFECTO,
        "puerto": puerto,
        "usuario": usuario,
        "password": filas.get("smtp_password", ""),
        "remitente": filas.get("smtp_remitente") or usuario,
    }


def configurado(con):
    cfg = leer_config(con)
    return bool(cfg["usuario"] and cfg["password"])


def guardar_config(con, host, puerto, usuario, password, remitente):
    _guardar(con, "smtp_host", (host or HOST_DEFECTO).strip())
    _guardar(con, "smtp_puerto", str(puerto or PUERTO_DEFECTO))
    _guardar(con, "smtp_usuario", (usuario or "").strip())
    _guardar(con, "smtp_password", (password or "").strip())
    _guardar(con, "smtp_remitente", (remitente or "").strip())
    con.commit()


def enviar(con, destinatario, asunto, cuerpo):
    cfg = leer_config(con)
    if not cfg["usuario"] or not cfg["password"]:
        raise ErrorCorreo("Todavía no configuraste el correo de envío "
                          "(Configuración → Correo).")
    if not destinatario:
        raise ErrorCorreo("Falta el correo de destino.")

    mensaje = MIMEText(cuerpo, "plain", "utf-8")
    mensaje["Subject"] = asunto
    mensaje["From"] = cfg["remitente"]
    mensaje["To"] = destinatario

    try:
        servidor = smtplib.SMTP(cfg["host"], cfg["puerto"], timeout=20)
        servidor.starttls()
        servidor.login(cfg["usuario"], cfg["password"])
        servidor.sendmail(cfg["remitente"], [destinatario], mensaje.as_string())
        servidor.quit()
    except Exception as exc:
        raise ErrorCorreo("No se pudo enviar el correo: %s" % exc)


# FIN services/correo.py
