"""Clave secreta de la aplicación (para las sesiones/login).

También proporciona funciones para cifrar/descifrar datos sensibles (SMTP password).
"""

import os
from pathlib import Path
import base64

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


def _obtener_cipher():
    """Obtiene cipher de Fernet para cifrado simétrico."""
    from cryptography.fernet import Fernet
    clave = obtener_secret_key()
    clave_bytes = clave.encode()[:32]  # Fernet requiere 32 bytes
    # Derivar clave usando base64 (Fernet requiere clave codificada en base64)
    clave_fernet = base64.urlsafe_b64encode(clave_bytes.ljust(32, b'\0'))
    return Fernet(clave_fernet)


def cifrar(texto):
    """Cifra un texto sensible (ej: contraseña SMTP)."""
    if not texto:
        return ""
    cipher = _obtener_cipher()
    return cipher.encrypt(texto.encode()).decode()


def descifrar(texto_cifrado):
    """Descifra un texto previamente cifrado."""
    if not texto_cifrado:
        return ""
    try:
        cipher = _obtener_cipher()
        return cipher.decrypt(texto_cifrado.encode()).decode()
    except Exception:
        return ""  # Si falla descifrado (clave diferente), devuelve vacío


# FIN services/seguridad.py
