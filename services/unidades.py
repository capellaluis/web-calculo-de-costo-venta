"""Conversión de unidades de medida.

Las unidades viven en la tabla `unidades` (ver database/schema.sql). Cada fila
tiene: id, nombre, abreviatura, tipo (masa / volumen / conteo / empaque) y
factor_base (cuántas unidades base contiene).

Base de masa = gramo, base de volumen = mililitro, base de conteo = unidad.
Ejemplo: 1 kg = 1000 g  ->  factor_base = 1000
"""

from decimal import Decimal


class ErrorUnidad(ValueError):
    """Error de conversión con mensaje en español, listo para mostrar al usuario."""


def _factor(unidad):
    return Decimal(str(unidad["factor_base"]))


def convertir(cantidad, desde, hacia):
    """Convierte `cantidad` desde la unidad `desde` a la unidad `hacia`.

    `desde` y `hacia` son filas de la tabla `unidades` (sqlite3.Row o dict).
    Devuelve un Decimal. Levanta ErrorUnidad si no son compatibles.
    """
    if desde["tipo"] != hacia["tipo"]:
        raise ErrorUnidad("Las unidades no son compatibles entre sí.")
    if desde["tipo"] == "empaque" and desde["id"] != hacia["id"]:
        raise ErrorUnidad("Paquete y caja solo se pueden convertir a sí mismos.")
    return Decimal(str(cantidad)) * _factor(desde) / _factor(hacia)


# FIN services/unidades.py
