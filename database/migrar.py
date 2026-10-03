"""Migraciones versionadas de la base (resumen 5.4).

- Cada archivo `migraciones/NNN_nombre.sql` se aplica una sola vez.
- La versión actual se guarda en `PRAGMA user_version`.
- Antes de aplicar cambios hace una COPIA de seguridad de la base.

Se ejecuta solo cuando arranca el servidor (`python app.py`), nunca al importar.
"""

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

CARPETA = Path(__file__).resolve().parent / "migraciones"
RUTA_DB = Path(__file__).resolve().parent / "negocio.db"
CARPETA_BACKUPS = Path(__file__).resolve().parent.parent / "backups"


def _copia_seguridad(ruta_db, carpeta_backups):
    carpeta_backups = Path(carpeta_backups)
    carpeta_backups.mkdir(parents=True, exist_ok=True)
    destino = carpeta_backups / (
        "negocio_antes_migrar_%s.db" % datetime.now().strftime("%Y-%m-%d_%H%M%S"))
    shutil.copy2(ruta_db, destino)
    return destino


def migrar(ruta_db=None, carpeta_backups=None):
    """Aplica las migraciones pendientes. Devuelve la lista de archivos aplicados."""
    ruta_db = Path(ruta_db or RUTA_DB)
    if carpeta_backups is None:
        carpeta_backups = CARPETA_BACKUPS
    if not ruta_db.exists():
        return []

    con = sqlite3.connect(ruta_db)
    try:
        actual = con.execute("PRAGMA user_version").fetchone()[0]
        pendientes = [archivo for archivo in sorted(CARPETA.glob("[0-9][0-9][0-9]_*.sql"))
                      if int(archivo.name[:3]) > actual]
        if not pendientes:
            return []

        _copia_seguridad(ruta_db, carpeta_backups)
        aplicadas = []
        for archivo in pendientes:
            version = int(archivo.name[:3])
            con.executescript(archivo.read_text(encoding="utf-8"))
            con.execute("PRAGMA user_version = %d" % version)
            con.commit()
            aplicadas.append(archivo.name)
        return aplicadas
    finally:
        con.close()


if __name__ == "__main__":
    aplicadas = migrar()
    if aplicadas:
        print("Migraciones aplicadas:", ", ".join(aplicadas))
    else:
        print("La base ya está al día.")


# FIN database/migrar.py
