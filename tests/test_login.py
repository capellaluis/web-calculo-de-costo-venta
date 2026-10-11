"""Pruebas del login (una sola empresa)."""

import re
import app as appmod
from services.usuarios import crear_usuario, hay_usuario


def _activar_login():
    appmod.app.config["REQUIERE_LOGIN"] = True


def _obtener_token_instalacion(html):
    """Extrae el token de instalación del HTML de login."""
    match = re.search(r'<code[^>]*>([^<]+)</code>', html)
    if match:
        return match.group(1).strip()
    return None


def test_sin_login_redirige(db_temporal):
    _activar_login()
    cliente = appmod.app.test_client()
    respuesta = cliente.get("/")
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_primer_uso_muestra_crear_usuario(db_temporal):
    _activar_login()
    texto = appmod.app.test_client().get("/login").get_data(as_text=True)
    assert "Crear y entrar" in texto


def test_crear_usuario_y_entrar(db_temporal, con):
    _activar_login()
    cliente = appmod.app.test_client()

    # Obtener token en GET
    get_resp = cliente.get("/login")
    html = get_resp.get_data(as_text=True)
    token = _obtener_token_instalacion(html)
    assert token, "No se encontró token de instalación"

    # Crear usuario con token
    respuesta = cliente.post("/login", data={
        "usuario": "luis", "email": "luis@example.com",
        "password": "1234", "password2": "1234",
        "install_token": token})
    assert respuesta.status_code == 302
    assert hay_usuario(con)
    assert cliente.get("/").status_code == 200


def test_password_incorrecta(db_temporal, con):
    crear_usuario(con, "luis", "1234", "luis@example.com")
    _activar_login()
    cliente = appmod.app.test_client()
    respuesta = cliente.post("/login", data={"usuario": "luis", "password": "mala"})
    assert respuesta.status_code == 200
    assert "incorrectos" in respuesta.get_data(as_text=True) or "incorrecto" in respuesta.get_data(as_text=True)
    assert cliente.get("/").status_code == 302


def test_login_correcto_y_logout(db_temporal, con):
    crear_usuario(con, "luis", "1234", "luis@example.com")
    _activar_login()
    cliente = appmod.app.test_client()

    assert cliente.post("/login", data={"usuario": "luis", "password": "1234"}).status_code == 302
    assert cliente.get("/").status_code == 200

    cliente.get("/logout")
    respuesta = cliente.get("/")
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


# FIN tests/test_login.py
