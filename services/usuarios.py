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
        " ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor",
        (clave, valor))


def _leer(con, *claves):
    marcas = ", ".join("?" for _ in claves)
    sql = "SELECT clave, valor FROM configuracion WHERE clave IN (%s)" % marcas
    return {fila["clave"]: fila["valor"]
            for fila in con.execute(sql, claves)}


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
    if len(password or "") < 10:
        raise ErrorUsuario("La contraseña debe tener al menos 10 caracteres.")
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
    if len(password or "") < 10:
        raise ErrorUsuario("La contraseña debe tener al menos 10 caracteres.")
    _guardar(con, "password_hash", generate_password_hash(password))
    con.commit()


def verificar(con, usuario, password):
    datos = leer_usuario(con)
    usuario_ingresado = (usuario or "").strip()
    password_ingresado = password or ""

    usuario_existe = bool(datos["usuario"] and datos["hash"])
    usuario_coincide = datos["usuario"] == usuario_ingresado

    # Timing attack mitigation: SIEMPRE ejecutar check_password_hash con el mismo tiempo,
    # incluso si el usuario no existe. Usa un hash dummy en ese caso.
    hash_a_verificar = datos["hash"] if usuario_existe else "pbkdf2:sha256$260000$dummy$dummy"
    password_valido = check_password_hash(hash_a_verificar, password_ingresado)

    return usuario_existe and usuario_coincide and password_valido


def generar_codigo_recuperacion(con):
    """Crea un código alfanumérico de 8 caracteres, lo guarda (hash) y devuelve el código."""
    codigo = secrets.token_urlsafe(6)[:8].upper()  # 8 caracteres alfanuméricos
    expira = (datetime.now() + timedelta(minutes=MINUTOS_VIGENCIA)).isoformat()
    _guardar(con, "reset_hash", generate_password_hash(codigo))
    _guardar(con, "reset_expira", expira)
    _guardar(con, "reset_intentos", "0")  # Reiniciar contador de intentos
    con.commit()
    return codigo


def verificar_codigo_recuperacion(con, codigo):
    filas = _leer(con, "reset_hash", "reset_expira", "reset_intentos")
    hash_guardado = filas.get("reset_hash", "")
    expira = filas.get("reset_expira", "")
    intentos_str = filas.get("reset_intentos", "0")

    if not hash_guardado or not expira:
        return False

    try:
        if datetime.now() > datetime.fromisoformat(expira):
            return False
    except ValueError:
        return False

    # Verificar límite de intentos (máx 5)
    try:
        intentos = int(intentos_str)
    except (ValueError, TypeError):
        intentos = 0

    if intentos >= 5:
        return False

    # Verificar código
    es_correcto = check_password_hash(hash_guardado, (codigo or "").strip())

    if not es_correcto:
        # Incrementar contador de intentos fallidos
        _guardar(con, "reset_intentos", str(intentos + 1))
        con.commit()

    return es_correcto


def limpiar_codigo_recuperacion(con):
    _guardar(con, "reset_hash", "")
    _guardar(con, "reset_expira", "")
    con.commit()


def generar_token_instalacion(con, ruta_archivo=None):
    """Genera un token alfanumérico de un solo uso para crear el primer admin.

    Solo se genera una vez. Si ya existe, devuelve el existente (sin regenerar).
    Si ruta_archivo es dada, guarda el token en un archivo (ej: INSTALL_TOKEN.txt).
    """
    from pathlib import Path
    token_actual = _leer(con, "install_token").get("install_token", "")
    if token_actual and token_actual != "USADO":
        return token_actual

    token = secrets.token_urlsafe(16)
    _guardar(con, "install_token", token)
    con.commit()

    if ruta_archivo:
        try:
            Path(ruta_archivo).write_text(token, encoding="utf-8")
        except (OSError, IOError):
            pass  # No falla si no puede escribir (ej: tests)

    return token


def obtener_token_instalacion(con):
    """Obtiene el token de instalación si aún no fue usado."""
    token = _leer(con, "install_token").get("install_token", "")
    if token == "USADO" or not token:
        return None
    return token


def verificar_token_instalacion(con, token_ingresado):
    """Valida el token antes de crear el primer admin.

    Devuelve True si el token es válido y aún no fue usado.
    Marca el token como USADO después de validar correctamente.
    """
    token_guardado = _leer(con, "install_token").get("install_token", "")
    if not token_guardado or token_guardado == "USADO":
        return False
    ingresado = (token_ingresado or "").strip()
    if token_guardado != ingresado:
        return False
    _guardar(con, "install_token", "USADO")
    con.commit()
    return True


# FIN services/usuarios.py
