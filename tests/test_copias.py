"""Pruebas de Copias de seguridad (Fase 15)."""

import sqlite3
from pathlib import Path

import app as appmod
import services.copias as copias


def _nombres(ruta_db):
    con = sqlite3.connect(ruta_db)
    try:
        return [f[0] for f in con.execute("SELECT nombre FROM proveedores ORDER BY nombre")]
    finally:
        con.close()


def test_crear_copia_y_restaurar(db_temporal, tmp_path):
    con = sqlite3.connect(db_temporal)
    con.execute("INSERT INTO proveedores (nombre) VALUES ('Antes')")
    con.commit()
    con.close()

    carpeta = tmp_path / "backups"
    ruta = copias.crear_copia(carpeta)
    assert ruta.exists()

    con = sqlite3.connect(db_temporal)
    con.execute("INSERT INTO proveedores (nombre) VALUES ('Despues')")
    con.commit()
    con.close()
    assert _nombres(db_temporal) == ["Antes", "Despues"]

    copias.restaurar_copia(ruta, carpeta)
    assert _nombres(db_temporal) == ["Antes"]


def test_listar_y_borrar(db_temporal, tmp_path):
    carpeta = tmp_path / "backups"
    ruta = copias.crear_copia(carpeta)

    lista = copias.listar_copias(carpeta)
    assert any(c["nombre"] == ruta.name for c in lista)

    assert copias.borrar_copia(ruta.name, carpeta) is True
    assert not ruta.exists()


def test_limitar_copias(db_temporal, tmp_path):
    carpeta = tmp_path / "backups"
    carpeta.mkdir()
    for i in range(12):
        (carpeta / ("negocio_2026-01-%02d_120000.db" % (i + 1))).write_bytes(b"x")
    borradas = copias.limitar_copias(carpeta, limite=10)
    assert len(borradas) == 2
    assert len(list(carpeta.glob("negocio_*.db"))) == 10


def test_pantalla_copias(db_temporal):
    respuesta = appmod.app.test_client().get("/copias/")
    assert respuesta.status_code == 200
    assert "Copias de seguridad" in respuesta.get_data(as_text=True)


def test_copia_automatica_tras_un_cambio(db_temporal, tmp_path):
    cliente = appmod.app.test_client()
    carpeta = tmp_path / "backups"

    # Un GET no genera copia.
    cliente.get("/proveedores/")
    if carpeta.exists():
        assert not list(carpeta.glob("*.db"))

    # Un cambio que guarda (POST -> redirect) genera copia automática.
    respuesta = cliente.post("/proveedores/nuevo", data={"nombre": "Auto Copia"})
    assert respuesta.status_code == 302
    assert list(carpeta.glob("*.db"))


# FIN tests/test_copias.py
