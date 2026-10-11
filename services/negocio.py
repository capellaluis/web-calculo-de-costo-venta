"""Datos del negocio: nombre y logo.

Se guardan en la tabla `configuracion` (claves `nombre_negocio` y `logo`).
El logo se guarda como archivo en `static/uploads/`.
"""

from pathlib import Path

CARPETA_UPLOADS = Path(__file__).resolve().parent.parent / "static" / "uploads"
EXTENSIONES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}  # SVG: vulnera XSS
TAMANO_MAXIMO = 2 * 1024 * 1024  # 2 MB
NOMBRE_DEFECTO = "Mi Negocio"


class ErrorNegocio(ValueError):
    """Error de validación con mensaje en español para mostrar al usuario."""


def leer_negocio(con):
    filas = {fila["clave"]: fila["valor"] for fila in con.execute(
        "SELECT clave, valor FROM configuracion"
        " WHERE clave IN ('nombre_negocio', 'logo')")}
    return {"nombre": filas.get("nombre_negocio") or NOMBRE_DEFECTO,
            "logo": filas.get("logo") or ""}


def guardar_nombre(con, nombre):
    nombre = (nombre or "").strip() or NOMBRE_DEFECTO
    con.execute(
        "INSERT INTO configuracion (clave, valor) VALUES ('nombre_negocio', ?)"
        " ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor", (nombre,))
    con.commit()
    return nombre


def _borrar_logos():
    if CARPETA_UPLOADS.exists():
        for archivo in CARPETA_UPLOADS.glob("logo*"):
            try:
                archivo.unlink()
            except OSError:
                pass


def guardar_logo(con, archivo):
    nombre = (archivo.filename or "").strip()
    if not nombre:
        raise ErrorNegocio("Elegí un archivo de imagen.")
    extension = Path(nombre).suffix.lower()
    if extension not in EXTENSIONES:
        raise ErrorNegocio("Formato no permitido. Usá PNG, JPG, GIF o WEBP.")

    archivo.seek(0, 2)
    tamano = archivo.tell()
    archivo.seek(0)
    if tamano > TAMANO_MAXIMO:
        raise ErrorNegocio("La imagen es muy grande (máximo 2 MB).")

    CARPETA_UPLOADS.mkdir(parents=True, exist_ok=True)
    _borrar_logos()
    destino = CARPETA_UPLOADS / ("logo" + extension)
    archivo.save(destino)

    con.execute(
        "INSERT INTO configuracion (clave, valor) VALUES ('logo', ?)"
        " ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor", (destino.name,))
    con.commit()
    return destino.name


def quitar_logo(con):
    con.execute(
        "INSERT INTO configuracion (clave, valor) VALUES ('logo', '')"
        " ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor")
    con.commit()
    _borrar_logos()


# FIN services/negocio.py
