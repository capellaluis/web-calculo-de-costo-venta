import sqlite3
from pathlib import Path

# Rutas: este archivo está dentro de la carpeta database/
CARPETA = Path(__file__).resolve().parent
RUTA_DB = CARPETA / "negocio.db"
RUTA_SCHEMA = CARPETA / "schema.sql"


def crear_base_de_datos():
    ya_existia = RUTA_DB.exists()

    conexion = sqlite3.connect(RUTA_DB)
    conexion.execute("PRAGMA foreign_keys = ON")

    # Ejecuta el plano. Como usa IF NOT EXISTS e INSERT OR IGNORE,
    # es seguro repetirlo: no borra ni duplica datos existentes.
    conexion.executescript(RUTA_SCHEMA.read_text(encoding="utf-8"))
    conexion.commit()

    if ya_existia:
        print("La base de datos ya existía. Se revisó y está al día.")
    else:
        print("Base de datos creada:", RUTA_DB)

    tablas = conexion.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    ).fetchall()
    print()
    print("Tablas creadas (%d):" % len(tablas))
    for (nombre,) in tablas:
        print("  -", nombre)

    margenes = conexion.execute(
        "SELECT numero, nombre, porcentaje FROM margenes ORDER BY numero"
    ).fetchall()
    print()
    print("Márgenes configurados:")
    for numero, nombre, porcentaje in margenes:
        print("  %s: %s%%" % (nombre, int(porcentaje)))

    unidades = conexion.execute("SELECT COUNT(*) FROM unidades").fetchone()[0]
    print()
    print("Unidades cargadas:", unidades)

    conexion.close()


if __name__ == "__main__":
    crear_base_de_datos()
