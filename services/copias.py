"""Copias de seguridad de la base (Fase 15).

Se usa la API de copia de SQLite (`backup`), que es segura incluso con el
servidor encendido. No se copia el archivo a mano.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

import database.db as dbmod

LIMITE_COPIAS = 10


def carpeta_backups_por_defecto():
    return Path(dbmod.RUTA_DB).resolve().parent.parent / "backups"


def carpeta_backups(carpeta=None):
    return Path(carpeta) if carpeta else carpeta_backups_por_defecto()


def _carpeta(carpeta=None):
    return carpeta_backups(carpeta)


def _ruta_unica(carpeta, base):
    destino = carpeta / base
    contador = 1
    while destino.exists():
        destino = carpeta / (base[:-3] + "_%d.db" % contador)
        contador += 1
    return destino


def crear_copia(carpeta=None):
    """Crea una copia de la base y devuelve su ruta (nombre único)."""
    carpeta = _carpeta(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    base = "negocio_%s.db" % datetime.now().strftime("%Y-%m-%d_%H%M%S")
    destino = _ruta_unica(carpeta, base)
    origen = sqlite3.connect(dbmod.RUTA_DB)
    copia = sqlite3.connect(destino)
    try:
        with copia:
            origen.backup(copia)
    finally:
        copia.close()
        origen.close()
    return destino


def listar_copias(carpeta=None):
    carpeta = _carpeta(carpeta)
    if not carpeta.exists():
        return []
    copias = []
    for archivo in carpeta.glob("*.db"):
        stat = archivo.stat()
        copias.append({"nombre": archivo.name, "tamano": stat.st_size,
                       "fecha": datetime.fromtimestamp(stat.st_mtime)})
    copias.sort(key=lambda c: c["nombre"], reverse=True)
    return copias


def restaurar_copia(ruta_copia, carpeta=None):
    """Vuelca la copia elegida SOBRE la base actual (guardando la actual antes)."""
    ruta_copia = Path(ruta_copia)
    if not ruta_copia.exists():
        raise FileNotFoundError("La copia no existe.")

    carpeta = _carpeta(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    seguridad = carpeta / (
        "negocio_antes_restaurar_%s.db" % datetime.now().strftime("%Y-%m-%d_%H%M%S"))

    actual = sqlite3.connect(dbmod.RUTA_DB)
    respaldo = sqlite3.connect(seguridad)
    try:
        with respaldo:
            actual.backup(respaldo)
    finally:
        respaldo.close()
        actual.close()

    origen = sqlite3.connect(ruta_copia)
    destino = sqlite3.connect(dbmod.RUTA_DB)
    try:
        with destino:
            origen.backup(destino)
    finally:
        destino.close()
        origen.close()
    return seguridad


def borrar_copia(nombre, carpeta=None):
    carpeta = _carpeta(carpeta)
    ruta = (carpeta / Path(nombre).name).resolve()
    if ruta.exists() and ruta.parent == carpeta.resolve():
        ruta.unlink()
        return True
    return False


def limitar_copias(carpeta=None, limite=LIMITE_COPIAS):
    """Borra las copias automáticas más viejas si hay más de `limite`."""
    carpeta = _carpeta(carpeta)
    if not carpeta.exists():
        return []
    copias = sorted(carpeta.glob("negocio_????-??-??_*.db"))
    borradas = []
    while len(copias) > limite:
        vieja = copias.pop(0)
        try:
            vieja.unlink()
            borradas.append(vieja.name)
        except OSError:
            pass
    return borradas


# FIN services/copias.py
