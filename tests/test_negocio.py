"""Pruebas de nombre y logo del negocio (Fase 23)."""

import io
from pathlib import Path

import pytest
from werkzeug.datastructures import FileStorage

import app as appmod
import services.negocio as negocio
from services.negocio import (
    ErrorNegocio,
    guardar_logo,
    guardar_nombre,
    leer_negocio,
    quitar_logo,
)


def test_guardar_nombre(con):
    guardar_nombre(con, "Panadería Luis")
    assert leer_negocio(con)["nombre"] == "Panadería Luis"


def test_nombre_vacio_usa_defecto(con):
    guardar_nombre(con, "   ")
    assert leer_negocio(con)["nombre"] == "Mi Negocio"


def test_logo_guardar_y_quitar(con, tmp_path, monkeypatch):
    monkeypatch.setattr(negocio, "CARPETA_UPLOADS", tmp_path / "uploads")
    archivo = FileStorage(stream=io.BytesIO(b"\x89PNG\r\n\x1a\n datos"), filename="mi-logo.png")

    nombre = guardar_logo(con, archivo)

    assert nombre == "logo.png"
    assert leer_negocio(con)["logo"] == "logo.png"
    assert (tmp_path / "uploads" / "logo.png").exists()

    quitar_logo(con)
    assert leer_negocio(con)["logo"] == ""


def test_logo_extension_invalida(con, tmp_path, monkeypatch):
    monkeypatch.setattr(negocio, "CARPETA_UPLOADS", tmp_path / "uploads")
    archivo = FileStorage(stream=io.BytesIO(b"x"), filename="logo.exe")
    with pytest.raises(ErrorNegocio):
        guardar_logo(con, archivo)


def test_ruta_negocio_guarda_y_se_ve(db_temporal, con, tmp_path, monkeypatch):
    monkeypatch.setattr(negocio, "CARPETA_UPLOADS", tmp_path / "uploads")
    cliente = appmod.app.test_client()

    respuesta = cliente.post("/config/negocio", data={"nombre_negocio": "Mi Panadería"})
    assert respuesta.status_code == 302
    assert leer_negocio(con)["nombre"] == "Mi Panadería"

    html = cliente.get("/").get_data(as_text=True)
    assert "Mi Panadería" in html


# FIN tests/test_negocio.py
