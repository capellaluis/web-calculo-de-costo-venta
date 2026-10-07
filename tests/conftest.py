"""Configuración común de las pruebas.

Cada prueba corre contra una base TEMPORAL (carpeta temporal de pytest), nunca
contra `database/negocio.db`. El fixture `db_temporal` crea el esquema desde
`schema.sql` y apunta `database.db.RUTA_DB` a esa base.
"""

import sqlite3
from pathlib import Path

import pytest

import database.db as dbmod


@pytest.fixture
def db_temporal(tmp_path, monkeypatch):
    ruta = tmp_path / "test.db"
    schema = Path(dbmod.__file__).with_name("schema.sql").read_text(encoding="utf-8")
    con = sqlite3.connect(ruta)
    con.executescript(schema)
    con.close()
    monkeypatch.setattr(dbmod, "RUTA_DB", ruta)
    return ruta


@pytest.fixture
def con(db_temporal):
    """Conexión a la base temporal; se cierra al terminar cada prueba."""
    conexion = dbmod.obtener_conexion()
    try:
        yield conexion
    finally:
        conexion.close()


@pytest.fixture(autouse=True)
def _backups_temporales(tmp_path, monkeypatch):
    """Aísla las copias de seguridad en una carpeta temporal en cada prueba."""
    import services.copias as copias
    monkeypatch.setattr(copias, "carpeta_backups_por_defecto",
                        lambda: tmp_path / "backups")
    yield


# FIN tests/conftest.py
