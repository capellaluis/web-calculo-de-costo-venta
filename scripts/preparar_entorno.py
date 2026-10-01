"""Prepara el entorno local de MI NEGOCIO.

- Crea las carpetas necesarias (database, exports, backups).
- Crea el archivo .env a partir de .env.example, con una SECRET_KEY nueva.
  Si .env ya existe NO lo toca.

Se ejecuta solo desde setup.sh / setup.bat. Tambien se puede ejecutar a mano:
    python scripts/preparar_entorno.py
"""
import os
import secrets
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MARCA = "CAMBIAR_POR_UNA_CLAVE_ALEATORIA"


def main():
    for carpeta in ("database", "exports", "backups"):
        (RAIZ / carpeta).mkdir(exist_ok=True)

    env = RAIZ / ".env"
    ejemplo = RAIZ / ".env.example"

    if env.exists():
        print("  El archivo .env ya existe: no se modifica.")
        return 0

    if not ejemplo.exists():
        print("  ERROR: falta el archivo .env.example, no se puede crear .env.")
        return 1

    texto = ejemplo.read_text(encoding="utf-8").replace(MARCA, secrets.token_hex(32))
    env.write_text(texto, encoding="utf-8")
    if os.name == "posix":
        env.chmod(0o600)  # solo el dueno puede leerlo
    print("  Se creo el archivo .env con una SECRET_KEY nueva.")
    print("  Puedes abrirlo para cambiar el puerto o la direccion (APP_HOST, APP_PORT).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
