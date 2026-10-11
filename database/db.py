import sqlite3
from pathlib import Path

RUTA_DB = Path(__file__).resolve().parent / "negocio.db"


def obtener_conexion():
    """Abre una conexión a la base de datos. Las filas se leen por nombre de columna."""
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_base(ruta_db=None):
    """Crea la base de datos desde schema.sql si no existe.

    Agnóstico al DB: cuando cambies a MySQL/PostgreSQL, actualiza schema.sql
    con la sintaxis correspondiente. Esta función sigue siendo la misma.
    """
    ruta_db = Path(ruta_db or RUTA_DB)
    if ruta_db.exists():
        return False  # Base ya existe

    schema = Path(__file__).with_name("schema.sql").read_text(
        encoding="utf-8")
    con = sqlite3.connect(ruta_db)
    try:
        con.executescript(schema)
        con.execute("PRAGMA user_version = 999")
        con.commit()
    finally:
        con.close()
    return True  # Base creada


# FIN db.py
