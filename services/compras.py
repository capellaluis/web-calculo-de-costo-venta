"""Lógica de compras.

Todo se hace en UNA sola transacción: si algo falla se deshace todo (rollback).
El precio se calcula siempre por la unidad de COMPRA del producto (por ejemplo
$/kg), aunque la línea se cargue en otra unidad compatible (por ejemplo gramos).
"""

from decimal import Decimal, ROUND_HALF_UP

from database.db import obtener_conexion
from services.unidades import convertir


class ErrorCompra(ValueError):
    """Error de validación con mensaje en español para mostrar al usuario."""


def _q(valor, decimales="0.0001"):
    return Decimal(valor).quantize(Decimal(decimales), rounding=ROUND_HALF_UP)


def _unidad(con, unidad_id):
    return con.execute("SELECT * FROM unidades WHERE id = ?", (unidad_id,)).fetchone()


def registrar_compra(proveedor_id, fecha, numero_documento, observaciones, lineas):
    """Registra una compra completa y devuelve su id.

    `lineas` es una lista de diccionarios con:
    producto_id, cantidad (Decimal), unidad_id, precio_total (Decimal).
    """
    if not proveedor_id:
        raise ErrorCompra("Elegí el proveedor de la compra.")
    if not fecha:
        raise ErrorCompra("Elegí la fecha de la compra.")
    if not lineas:
        raise ErrorCompra("Agregá al menos un producto a la compra.")

    con = obtener_conexion()
    try:
        cursor = con.execute(
            "INSERT INTO compras (proveedor_id, fecha, numero_documento, observaciones, total)"
            " VALUES (?, ?, ?, ?, 0)",
            (proveedor_id, fecha, numero_documento, observaciones))
        compra_id = cursor.lastrowid
        total = Decimal("0")

        for linea in lineas:
            cantidad = Decimal(linea["cantidad"])
            precio_total = Decimal(linea["precio_total"])
            if cantidad <= 0 or precio_total <= 0:
                raise ErrorCompra("La cantidad y el precio deben ser mayores a cero.")

            producto = con.execute(
                "SELECT * FROM productos WHERE id = ?",
                (linea["producto_id"],)).fetchone()
            if producto is None:
                raise ErrorCompra("Uno de los productos elegidos no existe.")

            u_linea = _unidad(con, linea["unidad_id"])
            u_compra = _unidad(con, producto["unidad_compra_id"])
            if u_linea is None or u_compra is None:
                raise ErrorCompra("La unidad elegida no es válida.")

            try:
                cantidad_en_compra = convertir(cantidad, u_linea, u_compra)
            except ValueError:
                raise ErrorCompra(
                    "La unidad elegida no es compatible con la del producto "
                    "(por ejemplo, un producto que se compra por kg no acepta litros).")

            precio_unitario = _q(precio_total / cantidad_en_compra)

            detalle = con.execute(
                "INSERT INTO detalle_compras"
                " (compra_id, producto_id, cantidad, unidad_id, precio_total, precio_unitario)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (compra_id, producto["id"], float(cantidad), u_linea["id"],
                 float(precio_total), float(precio_unitario)))

            ultimo = con.execute(
                "SELECT MAX(fecha) FROM historial_precios WHERE producto_id = ?",
                (producto["id"],)).fetchone()[0]
            con.execute(
                "INSERT INTO historial_precios"
                " (producto_id, fecha, precio_unitario, unidad_id, detalle_compra_id)"
                " VALUES (?, ?, ?, ?, ?)",
                (producto["id"], fecha, float(precio_unitario),
                 producto["unidad_compra_id"], detalle.lastrowid))

            # Una factura vieja cargada hoy NO debe pisar un precio más reciente.
            if ultimo is None or fecha >= ultimo:
                con.execute(
                    "UPDATE productos SET precio_actual = ? WHERE id = ?",
                    (float(precio_unitario), producto["id"]))

            total += precio_total

        con.execute("UPDATE compras SET total = ? WHERE id = ?",
                    (float(_q(total, "0.01")), compra_id))
        con.commit()
        return compra_id
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def eliminar_compra(compra_id):
    """Elimina la compra y recalcula el precio actual de los productos afectados.

    Devuelve la lista con los nombres de los productos que quedaron sin ningún
    registro de historial: en esos casos se conserva el precio actual.
    """
    con = obtener_conexion()
    try:
        compra = con.execute(
            "SELECT * FROM compras WHERE id = ?", (compra_id,)).fetchone()
        if compra is None:
            raise ErrorCompra("La compra no existe.")

        afectados = con.execute(
            "SELECT DISTINCT producto_id FROM detalle_compras WHERE compra_id = ?",
            (compra_id,)).fetchall()

        # 1) Borrar los precios de historial que apuntan a los detalles de esta compra
        #    (la foreign key es SET NULL y si no quedarían huérfanos).
        con.execute(
            "DELETE FROM historial_precios WHERE detalle_compra_id IN"
            " (SELECT id FROM detalle_compras WHERE compra_id = ?)", (compra_id,))

        # 2) Borrar la compra (el detalle se borra en cascada).
        con.execute("DELETE FROM compras WHERE id = ?", (compra_id,))

        # 3) Recalcular precio_actual con el registro de historial más reciente.
        sin_historial = []
        for fila in afectados:
            producto_id = fila["producto_id"]
            ultimo = con.execute(
                "SELECT precio_unitario FROM historial_precios"
                " WHERE producto_id = ? ORDER BY fecha DESC, id DESC LIMIT 1",
                (producto_id,)).fetchone()
            if ultimo is None:
                nombre = con.execute(
                    "SELECT nombre FROM productos WHERE id = ?",
                    (producto_id,)).fetchone()
                sin_historial.append(nombre["nombre"] if nombre else "?")
            else:
                con.execute(
                    "UPDATE productos SET precio_actual = ? WHERE id = ?",
                    (ultimo["precio_unitario"], producto_id))

        con.commit()
        return sin_historial
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


# FIN services/compras.py
