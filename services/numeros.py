"""Lectura de números escritos por el usuario (formato argentino).

Acepta "1200", "1200,50", "$1.200,50" y espacios. Se usa en Productos y Compras
para no duplicar la misma lógica en dos lugares.
"""

from decimal import Decimal


def _limpiar(texto):
    """Quita símbolos y normaliza separadores. '1.200,50' -> '1200.50'."""
    texto = (texto or "").replace("$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return texto


def leer_precio(texto):
    """Devuelve un float. Acepta '1200' y '1200,50' (y '1.200,50')."""
    limpio = _limpiar(texto)
    if not limpio:
        return 0.0
    return float(limpio)


def leer_decimal(texto):
    """Igual que leer_precio pero devuelve un Decimal (más preciso)."""
    limpio = _limpiar(texto)
    if not limpio:
        return Decimal("0")
    return Decimal(limpio)


# FIN services/numeros.py
