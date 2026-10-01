import sqlite3
from pathlib import Path

RUTA_DB = Path(__file__).resolve().parent / "negocio.db"


def obtener_conexion():
    """Abre una conexión a la base de datos. Las filas se leen por nombre de columna."""
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


# FIN db.py
