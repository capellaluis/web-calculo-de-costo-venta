"""Descarga los iconos y la libreria de graficos si faltan en static/.

Solo necesita Internet la primera vez. Si los archivos ya existen no hace nada.
Se ejecuta desde setup.sh / setup.bat. Tambien a mano:
    python scripts/descargar_recursos.py
"""
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

VERSION_ICONOS = "1.11.3"
VERSION_GRAFICOS = "4.4.7"
BASE_ICONOS = "https://cdn.jsdelivr.net/npm/bootstrap-icons@%s/font/" % VERSION_ICONOS
BASE_GRAFICOS = "https://cdn.jsdelivr.net/npm/chart.js@%s/dist/" % VERSION_GRAFICOS

# (direccion de descarga, ruta dentro del proyecto)
RECURSOS = [
    (BASE_ICONOS + "bootstrap-icons.css", "static/icons/bootstrap-icons.css"),
    (BASE_ICONOS + "fonts/bootstrap-icons.woff2", "static/icons/fonts/bootstrap-icons.woff2"),
    (BASE_ICONOS + "fonts/bootstrap-icons.woff", "static/icons/fonts/bootstrap-icons.woff"),
    (BASE_GRAFICOS + "chart.umd.js", "static/js/chart.umd.js"),
]

TAMANO_MINIMO = 1000  # un archivo de menos de 1 KB se considera una descarga fallida


def descargar(url, destino):
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(destino.name + ".descarga")
    pedido = urllib.request.Request(url, headers={"User-Agent": "MiNegocio-instalador"})
    with urllib.request.urlopen(pedido, timeout=30) as respuesta:
        contenido = respuesta.read()
    if len(contenido) < TAMANO_MINIMO:
        raise ValueError("el archivo descargado es demasiado pequeno")
    temporal.write_bytes(contenido)
    temporal.replace(destino)


def main():
    fallos = []
    for url, ruta in RECURSOS:
        destino = RAIZ / ruta
        if destino.exists() and destino.stat().st_size >= TAMANO_MINIMO:
            print("  Ya existe: " + ruta)
            continue
        try:
            print("  Descargando: " + ruta)
            descargar(url, destino)
        except Exception as error:  # red caida, sin Internet, etc.
            fallos.append(ruta)
            print("  NO se pudo descargar %s (%s)" % (ruta, error))

    if fallos:
        print("")
        print("  Faltan %d archivo(s). Revisa tu conexion a Internet y vuelve a" % len(fallos))
        print("  ejecutar el instalador. La aplicacion abre igual, pero sin iconos/graficos.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
