"""Usuario administrador (una sola empresa) y recuperación de acceso.

El usuario, el correo y la contraseña (guardada como HASH, nunca en texto)
viven en la tabla `configuracion`.
"""

import secrets
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

MINUTOS_VIGENCIA = 15


class ErrorUsuario(ValueError):
    """Error de validación con mensaje en español para mostrar al usuario."""


def _guardar(con, clave, valor):
    con.execute(
        "INSERT INTO configuracion (clave, valor) VALUES (?, ?)"
        " ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor", (clave, valor))


def _leer(con, *claves):
    marcas = ", ".join("?" for _ in claves)
    return {fila["clave"]: fila["valor"] for fila in con.execute(
        "SELECT clave, valor FROM configuracion WHERE clave IN (%s)" % marcas, claves)}


def leer_usuario(con):
    filas = _leer(con, "usuario", "password_hash", "email")
    return {"usuario": filas.get("usuario", ""),
            "hash": filas.get("password_hash", ""),
            "email": filas.get("email", "")}


def hay_usuario(con):
    datos = leer_usuario(con)
    return bool(datos["usuario"] and datos["hash"])


def crear_usuario(con, usuario, password, email=""):
    usuario = (usuario or "").strip()
    email = (email or "").strip()
    if not usuario:
        raise ErrorUsuario("Escribí un nombre de usuario.")
    if len(password or "") < 4:
        raise ErrorUsuario("La contraseña debe tener al menos 4 caracteres.")
    if "@" not in email:
        raise ErrorUsuario("Escribí un correo válido (para poder recuperar el acceso).")
    _guardar(con, "usuario", usuario)
    _guardar(con, "password_hash", generate_password_hash(password))
    _guardar(con, "email", email)
    con.commit()
    return usuario


def guardar_email(con, email):
    email = (email or "").strip()
    if "@" not in email:
        raise ErrorUsuario("Escribí un correo válido.")
    _guardar(con, "email", email)
    con.commit()


def cambiar_password(con, password):
    if len(password or "") < 4:
        raise ErrorUsuario("La contraseña debe tener al menos 4 caracteres.")
    _guardar(con, "password_hash", generate_password_hash(password))
    con.commit()


def verificar(con, usuario, password):
    datos = leer_usuario(con)
    if not datos["usuario"] or not datos["hash"]:
        return False
    return (datos["usuario"] == (usuario or "").strip()
            and check_password_hash(datos["hash"], password or ""))


def generar_codigo_recuperacion(con):
    """Crea un código de 6 dígitos, lo guarda (hash) y devuelve el código."""
    codigo = "%06d" % secrets.randbelow(1000000)
    expira = (datetime.now() + timedelta(minutes=MINUTOS_VIGENCIA)).isoformat()
    _guardar(con, "reset_hash", generate_password_hash(codigo))
    _guardar(con, "reset_expira", expira)
    con.commit()
    return codigo


def verificar_codigo_recuperacion(con, codigo):
    filas = _leer(con, "reset_hash", "reset_expira")
    hash_guardado = filas.get("reset_hash", "")
    expira = filas.get("reset_expira", "")
    if not hash_guardado or not expira:
        return False
    try:
        if datetime.now() > datetime.fromisoformat(expira):
            return False
    except ValueError:
        return False
    return check_password_hash(hash_guardado, (codigo or "").strip())


def limpiar_codigo_recuperacion(con):
    _guardar(con, "reset_hash", "")
    _guardar(con, "reset_expira", "")
    con.commit()


# FIN services/usuarios.py
