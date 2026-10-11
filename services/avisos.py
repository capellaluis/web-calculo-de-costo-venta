"""Avisos que se muestran después de una acción (notificaciones flotantes).

Cada módulo de rutas define su diccionario AVISOS {clave: aviso} y la URL lleva
?aviso=<clave>. Un valor de texto suelto es un aviso de éxito; para otro tipo se
usa crear_aviso(texto, tipo="error").

El tiempo hasta que se oculta sale de APP_AVISO_SEGUNDOS (5 por defecto,
0 = no se oculta solo) o de `segundos` en el aviso.
"""

import os

TIPOS = ("info", "exito", "advertencia", "error")
SEGUNDOS_POR_DEFECTO = 5


class ErrorAviso(ValueError):
    """Aviso mal armado (error de programación, no del usuario)."""


def crear_aviso(texto, tipo="exito", segundos=None):
    """Arma un aviso. `segundos` None = usar el tiempo por defecto."""
    if tipo not in TIPOS:
        raise ErrorAviso(f"Tipo de aviso no válido: {tipo}. Usar uno de {TIPOS}.")
    if segundos is not None and segundos < 0:
        raise ErrorAviso("Los segundos del aviso no pueden ser negativos.")
    return {"texto": texto, "tipo": tipo, "segundos": segundos}


def leer_aviso(avisos, clave):
    """Devuelve el aviso de la clave (?aviso=...) o None si no hay."""
    valor = avisos.get(clave or "")
    if valor is None:
        return None
    if isinstance(valor, str):
        return crear_aviso(valor)
    return valor


def segundos_por_defecto():
    """Lee APP_AVISO_SEGUNDOS en cada pedido (así respeta el .env cargado al iniciar)."""
    try:
        valor = float(os.environ.get("APP_AVISO_SEGUNDOS", SEGUNDOS_POR_DEFECTO))
    except ValueError:
        return SEGUNDOS_POR_DEFECTO
    if valor < 0:
        return SEGUNDOS_POR_DEFECTO
    return int(valor) if valor.is_integer() else valor


# FIN services/avisos.py
