"""Servidor de producción (waitress) para el uso diario.

Uso:   python servidor.py
Para apagarlo:   Ctrl + C

A diferencia del servidor de desarrollo (`python app.py`), esto NO recarga solo
y NO muestra errores detallados: es el modo recomendado para usar todos los días.
La dirección y el puerto se toman del archivo `.env` (APP_HOST / APP_PORT).
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from waitress import serve

import app as appmod
from database.migrar import migrar


def main():
    # Aplica migraciones pendientes (hace copia de seguridad antes).
    migrar()

    host = os.environ.get("APP_HOST", "127.0.0.1")
    puerto = int(os.environ.get("APP_PORT", "5000"))

    print("=" * 52)
    print(" MI NEGOCIO - servidor de uso diario (waitress)")
    print(" Escuchando en:  http://%s:%d" % (host, puerto))
    print(" Para apagar:    Ctrl + C")
    print("=" * 52)
    serve(appmod.app, host=host, port=puerto)


if __name__ == "__main__":
    main()


# FIN servidor.py
