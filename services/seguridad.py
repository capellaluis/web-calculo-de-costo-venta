"""Clave secreta de la aplicación (para las sesiones/login)."""

import os
from pathlib import Path

RUTA_CLAVE = Path(__file__).resolve().parent.parent / ".secret_key"


def obtener_secret_key():
    """Usa SECRET_KEY del entorno (.env); si no, un archivo local; si no, la crea."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    clave = os.environ.get("SECRET_KEY")
    if clave:
        return clave

    if RUTA_CLAVE.exists():
        contenido = RUTA_CLAVE.read_text(encoding="utf-8").strip()
        if contenido:
            return contenido

    clave = os.urandom(32).hex()
    try:
        RUTA_CLAVE.write_text(clave, encoding="utf-8")
    except OSError:
        pass
    return clave


# FIN services/seguridad.py
