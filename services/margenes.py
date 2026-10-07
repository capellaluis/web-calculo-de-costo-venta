"""Márgenes de ganancia, precios de venta y gastos fijos.

Cómo se calcula el precio de venta:
  1) Al costo se le SUMAN los gastos fijos (gas, agua, luz, ...):
         costo_con_gastos = costo x (1 + suma de gastos %)
  2) Sobre ese total se aplica el margen de ganancia DIVIDIENDO:
         precio = costo_con_gastos / (1 - margen % / 100)
     (por eso "30 % de ganancia" sobre $500 es $500 / 0,70).
"""

from decimal import Decimal, ROUND_HALF_UP

from services.gastos import monto

REDONDEOS = {
    "ninguno": "Sin redondear",
    "entero": "Al peso entero (sin centavos)",
    "centavos": "A los centavos",
}


class ErrorMargen(ValueError):
    """Error de validación con mensaje en español para mostrar al usuario."""


def _decimal(valor):
    return Decimal(str(valor or 0))


def precio_margen_real(costo, porcentaje):
    """El porcentaje es la ganancia sobre el precio final (se divide)."""
    pct = _decimal(porcentaje)
    if pct >= 100:
        raise ErrorMargen("El margen de ganancia debe ser menor a 100 %.")
    return _decimal(costo) / (1 - pct / 100)


def redondear(valor, modo="ninguno"):
    valor = _decimal(valor)
    if modo == "entero":
        return valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    if modo == "centavos":
        return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return valor


def leer_configuracion(con):
    return {fila["clave"]: fila["valor"]
            for fila in con.execute("SELECT clave, valor FROM configuracion")}


def leer_margenes(con):
    return [dict(fila) for fila in con.execute(
        "SELECT * FROM margenes ORDER BY numero")]


def leer_redondeo(con):
    return leer_configuracion(con).get("redondeo", "entero")


def guardar_redondeo(con, redondeo):
    if redondeo not in REDONDEOS:
        raise ErrorMargen("Elegí una forma de redondeo válida.")
    con.execute(
        "INSERT INTO configuracion (clave, valor) VALUES ('redondeo', ?)"
        " ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor", (redondeo,))
    con.commit()


def guardar_margenes(con, margenes, redondeo):
    """`margenes`: lista de {'numero', 'nombre', 'porcentaje'}."""
    if redondeo not in REDONDEOS:
        raise ErrorMargen("Elegí una forma de redondeo válida.")
    for margen in margenes:
        if margen["porcentaje"] < 0:
            raise ErrorMargen("Los márgenes no pueden ser negativos.")
        if margen["porcentaje"] >= 100:
            raise ErrorMargen("Cada margen de ganancia debe ser menor a 100 %.")

    for margen in margenes:
        nombre = (margen.get("nombre") or "").strip() or ("Margen %d" % margen["numero"])
        con.execute("UPDATE margenes SET nombre = ?, porcentaje = ? WHERE numero = ?",
                    (nombre, float(margen["porcentaje"]), margen["numero"]))
    con.execute(
        "INSERT INTO configuracion (clave, valor) VALUES ('redondeo', ?)"
        " ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor", (redondeo,))
    con.commit()


def total_porcentaje(lista):
    """Suma de los porcentajes de una lista de diccionarios."""
    total = Decimal("0")
    for item in lista:
        total += _decimal(item.get("porcentaje"))
    return total


def precio_delivery(tienda, delivery, redondeo="entero"):
    """Precio de delivery: divide el precio de tienda por (1 - suma de % delivery)."""
    total = total_porcentaje(delivery)
    if total >= 100:
        raise ErrorMargen("La suma de los % de delivery debe ser menor a 100 %.")
    return redondear(_decimal(tienda) / (1 - total / 100), redondeo)


def calcular_precio(costo, gastos, margen_porcentaje, delivery, redondeo="entero"):
    """Desglose completo para un costo: con gastos, tienda, delivery y ganancia."""
    costo = _decimal(costo)
    con_gastos = costo * (1 + total_porcentaje(gastos) / 100)
    tienda = None
    precio_deliv = None
    ganancia = None
    if _decimal(margen_porcentaje) < 100:
        tienda = redondear(con_gastos / (1 - _decimal(margen_porcentaje) / 100), redondeo)
        ganancia = tienda - con_gastos
        if total_porcentaje(delivery) < 100:
            precio_deliv = redondear(
                tienda / (1 - total_porcentaje(delivery) / 100), redondeo)
    return {"costo": costo, "con_gastos": con_gastos, "tienda": tienda,
            "delivery": precio_deliv, "ganancia": ganancia}


def calcular_precios_venta(costo, gastos, margenes, redondeo="entero"):
    """Devuelve el desglose completo: costo, gastos con su monto, total y precios."""
    costo = _decimal(costo)

    detalle_gastos = []
    total_gastos = Decimal("0")
    for gasto in gastos:
        valor = monto(costo, gasto["porcentaje"])
        total_gastos += valor
        detalle_gastos.append({
            "nombre": gasto["nombre"],
            "porcentaje": gasto["porcentaje"],
            "monto": valor,
        })
    costo_con_gastos = costo + total_gastos

    precios = []
    for margen in margenes:
        precio = redondear(
            precio_margen_real(costo_con_gastos, margen["porcentaje"]), redondeo)
        precios.append({
            "nombre": margen["nombre"],
            "porcentaje": margen["porcentaje"],
            "precio": precio,
            "ganancia": precio - costo_con_gastos,
        })

    return {
        "costo": costo,
        "gastos": detalle_gastos,
        "total_gastos": total_gastos,
        "costo_con_gastos": costo_con_gastos,
        "precios": precios,
    }


# FIN services/margenes.py
