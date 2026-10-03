"""Pruebas de las migraciones versionadas (database/migrar.py)."""

import sqlite3
from pathlib import Path

import database.migrar as migmod


def _schema():
    return Path(migmod.__file__).with_name("schema.sql").read_text(encoding="utf-8")


def test_migracion_agrega_gastos_y_hace_copia(tmp_path):
    ruta = tmp_path / "vieja.db"
    con = sqlite3.connect(ruta)
    con.executescript(_schema())
    # Simulamos una base vieja: sin tabla de gastos y versión 0.
    con.execute("DROP TABLE gastos")
    con.execute("PRAGMA user_version = 0")
    con.commit()
    con.close()

    backups = tmp_path / "backups"
    aplicadas = migmod.migrar(ruta, backups)

    assert aplicadas == ["001_gastos.sql"]
    assert list(backups.glob("negocio_antes_migrar_*.db"))

    con = sqlite3.connect(ruta)
    nombres = [fila[0] for fila in con.execute(
        "SELECT nombre FROM gastos ORDER BY orden")]
    version = con.execute("PRAGMA user_version").fetchone()[0]
    con.close()
    assert nombres == ["Gas", "Agua", "Luz"]
    assert version == 1

    # Segunda corrida: no aplica nada y no vuelve a copiar.
    assert migmod.migrar(ruta, backups) == []


def test_migrar_sin_base(tmp_path):
    assert migmod.migrar(tmp_path / "no_existe.db", tmp_path / "b") == []


# FIN tests/test_migrar.py
