"""Gastos fijos (gas, agua, luz, alquiler, ...).

Cada gasto es un porcentaje que se SUMA al costo del producto/receta.
El usuario puede agregar, renombrar y quitar renglones.
"""

from decimal import Decimal


class ErrorGasto(ValueError):
    """Error de validación con mensaje en español para mostrar al usuario."""


def leer_gastos(con):
    return [dict(fila) for fila in con.execute(
        "SELECT * FROM gastos ORDER BY orden, id")]


def monto(costo, porcentaje):
    """Cuánto representa un porcentaje del costo (se suma)."""
    return Decimal(str(costo or 0)) * Decimal(str(porcentaje or 0)) / 100


def guardar_gastos(con, gastos):
    """Reemplaza todos los renglones de gastos.

    `gastos` es una lista de {'nombre': str, 'porcentaje': Decimal/float}.
    """
    for gasto in gastos:
        if gasto["porcentaje"] < 0:
            raise ErrorGasto("Los porcentajes de gastos no pueden ser negativos.")

    con.execute("DELETE FROM gastos")
    for orden, gasto in enumerate(gastos):
        nombre = (gasto.get("nombre") or "").strip() or ("Gasto %d" % (orden + 1))
        con.execute(
            "INSERT INTO gastos (nombre, porcentaje, orden) VALUES (?, ?, ?)",
            (nombre, float(gasto["porcentaje"]), orden))
    con.commit()


# FIN services/gastos.py
