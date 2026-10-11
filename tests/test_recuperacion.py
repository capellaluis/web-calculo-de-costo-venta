"""Pruebas de recuperación de acceso por correo."""

import re

import app as appmod
from services import correo
from services.usuarios import crear_usuario


def _activar_login():
    appmod.app.config["REQUIERE_LOGIN"] = True


def _preparar(con):
    crear_usuario(con, "luis", "MiPassword123", "luis@example.com")
    correo.guardar_config(con, "smtp.gmail.com", "587",
                          "envio@gmail.com", "claveapp", "envio@gmail.com")


def test_recuperar_envia_codigo_y_cambia_la_clave(db_temporal, con, monkeypatch):
    _preparar(con)
    enviados = {}

    def falso_enviar(conexion, destino, asunto, cuerpo):
        enviados["destino"] = destino
        enviados["cuerpo"] = cuerpo

    monkeypatch.setattr(correo, "enviar", falso_enviar)
    _activar_login()
    cliente = appmod.app.test_client()

    # Paso 1: pedir el código
    respuesta = cliente.post("/recuperar")
    assert respuesta.status_code == 200
    assert enviados["destino"] == "luis@example.com"
    codigo = re.search(r"\s+Código:\s*([A-Z0-9]{8})", enviados["cuerpo"]).group(1)

    # Paso 2: cambiar la clave con el código
    respuesta = cliente.post("/recuperar/cambiar", data={
        "codigo": codigo, "password": "NuevaPassword123", "password2": "NuevaPassword123"})
    assert respuesta.status_code == 200
    assert "luis" in respuesta.get_data(as_text=True)

    # Ya se puede entrar con la clave nueva
    assert cliente.post("/login", data={
        "usuario": "luis", "password": "NuevaPassword123"}).status_code == 302


def test_codigo_incorrecto(db_temporal, con):
    _preparar(con)
    _activar_login()
    cliente = appmod.app.test_client()
    respuesta = cliente.post("/recuperar/cambiar", data={
        "codigo": "000000", "password": "nueva123", "password2": "nueva123"})
    assert respuesta.status_code == 200
    assert "incorrecto" in respuesta.get_data(as_text=True).lower()


def test_sin_correo_configurado(db_temporal, con):
    crear_usuario(con, "luis", "MiPassword123", "luis@example.com")
    _activar_login()
    cliente = appmod.app.test_client()
    respuesta = cliente.post("/recuperar")
    assert respuesta.status_code == 200
    assert "configurado" in respuesta.get_data(as_text=True).lower()


# FIN tests/test_recuperacion.py
