"""Reportes con filtros (Fase 14).

Cada reporte devuelve: título, encabezados, filas, formatos (para Excel),
y un resumen opcional (label/valor/formato).
"""

from openpyxl import Workbook

from services.exportar_excel import a_fecha, agregar_hoja
from services.fabricados import calcular_fabricado
from services.recetas import calcular_receta
from services.ventas import CANALES, ESTADOS, listar_pedidos

TIPOS = {
    "compras": "Compras",
    "proveedores": "Proveedores",
    "productos": "Productos",
    "historial": "Historial de precios",
    "costos": "Costos de recetas",
    "fabricados": "Productos fabricados",
    "ventas": "Ventas",
}


def construir_reporte(con, tipo, filtros=None):
    filtros = filtros or {}
    if tipo == "proveedores":
        return _proveedores(con)
    if tipo == "productos":
        return _productos(con, filtros)
    if tipo == "historial":
        return _historial(con, filtros)
    if tipo == "costos":
        return _costos(con)
    if tipo == "fabricados":
        return _fabricados(con)
    if tipo == "ventas":
        return _ventas(con, filtros)
    return _compras(con, filtros)


def _resumen(label, valor, formato="money"):
    return {"label": label, "valor": valor, "formato": formato}


def _compras(con, filtros):
    sql = ("SELECT c.id, pr.nombre AS proveedor, c.fecha,"
           " COALESCE(c.numero_documento, '') AS doc,"
           " COALESCE(c.observaciones, '') AS obs, c.total"
           " FROM compras c JOIN proveedores pr ON pr.id = c.proveedor_id WHERE 1 = 1")
    params = []
    if filtros.get("desde"):
        sql += " AND c.fecha >= ?"
        params.append(filtros["desde"])
    if filtros.get("hasta"):
        sql += " AND c.fecha <= ?"
        params.append(filtros["hasta"])
    if filtros.get("proveedor"):
        sql += " AND c.proveedor_id = ?"
        params.append(filtros["proveedor"])
    sql += " ORDER BY c.fecha DESC, c.id DESC"

    filas = []
    total = 0
    for compra in con.execute(sql, params):
        filas.append([compra["id"], compra["proveedor"], a_fecha(compra["fecha"]),
                      compra["doc"], compra["obs"], compra["total"]])
        total += compra["total"] or 0
    return {"titulo": "Compras",
            "encabezados": ["ID", "Proveedor", "Fecha", "Nº factura/remito",
                            "Observaciones", "Total"],
            "filas": filas,
            "formatos": [None, None, "date", None, None, "money"],
            "resumen": _resumen("Total del período", total)}


def _proveedores(con):
    filas = []
    total = 0
    for fila in con.execute(
        "SELECT pr.id, pr.nombre, COALESCE(pr.cuit_rut, '') AS cuit,"
        " COALESCE(pr.telefono, '') AS tel, COUNT(c.id) AS n,"
        " COALESCE(SUM(c.total), 0) AS total"
        " FROM proveedores pr LEFT JOIN compras c ON c.proveedor_id = pr.id"
        " GROUP BY pr.id ORDER BY total DESC, pr.nombre"):
        filas.append([fila["id"], fila["nombre"], fila["cuit"], fila["tel"],
                      fila["n"], fila["total"]])
        total += fila["total"] or 0
    return {"titulo": "Proveedores",
            "encabezados": ["ID", "Proveedor", "CUIT/RUT", "Teléfono",
                            "Compras", "Total comprado"],
            "filas": filas,
            "formatos": [None, None, None, None, None, "money"],
            "resumen": _resumen("Total comprado", total)}


def _productos(con, filtros):
    sql = ("SELECT p.id, p.nombre, COALESCE(c.nombre, '') AS categoria,"
           " uc.abreviatura AS ucompra, uu.abreviatura AS uso, p.precio_actual,"
           " COALESCE(pr.nombre, '') AS proveedor"
           " FROM productos p"
           " LEFT JOIN categorias c ON c.id = p.categoria_id"
           " JOIN unidades uc ON uc.id = p.unidad_compra_id"
           " JOIN unidades uu ON uu.id = p.unidad_uso_id"
           " LEFT JOIN proveedores pr ON pr.id = p.proveedor_principal_id WHERE 1 = 1")
    params = []
    if filtros.get("categoria"):
        sql += " AND COALESCE(c.nombre, 'Sin categoría') = ?"
        params.append(filtros["categoria"])
    sql += " ORDER BY p.nombre"
    filas = [[f["id"], f["nombre"], f["categoria"], f["ucompra"], f["uso"],
              f["precio_actual"], f["proveedor"]] for f in con.execute(sql, params)]
    return {"titulo": "Productos",
            "encabezados": ["ID", "Nombre", "Categoría", "Unidad compra", "Unidad uso",
                            "Precio actual", "Proveedor"],
            "filas": filas,
            "formatos": [None, None, None, None, None, "money", None],
            "resumen": _resumen("Productos", len(filas), "number")}


def _historial(con, filtros):
    sql = ("SELECT h.fecha, p.nombre AS producto, h.precio_unitario, u.abreviatura"
           " FROM historial_precios h"
           " JOIN productos p ON p.id = h.producto_id"
           " JOIN unidades u ON u.id = h.unidad_id WHERE 1 = 1")
    params = []
    if filtros.get("producto"):
        sql += " AND h.producto_id = ?"
        params.append(filtros["producto"])
    if filtros.get("desde"):
        sql += " AND h.fecha >= ?"
        params.append(filtros["desde"])
    if filtros.get("hasta"):
        sql += " AND h.fecha <= ?"
        params.append(filtros["hasta"])
    sql += " ORDER BY h.fecha DESC, h.id DESC"
    filas = [[a_fecha(f["fecha"]), f["producto"], f["precio_unitario"], f["abreviatura"]]
             for f in con.execute(sql, params)]
    return {"titulo": "Historial de precios",
            "encabezados": ["Fecha", "Producto", "Precio unitario", "Unidad"],
            "filas": filas,
            "formatos": ["date", None, "money", None],
            "resumen": _resumen("Registros", len(filas), "number")}


def _costos(con):
    unidades = {u["id"]: u for u in con.execute("SELECT * FROM unidades")}
    filas = []
    for receta in con.execute("SELECT * FROM recetas ORDER BY nombre"):
        calculo = calcular_receta(con, receta["id"], unidades=unidades)
        filas.append([receta["nombre"],
                      "%s %s" % (receta["rendimiento_cantidad"], receta["rendimiento_unidad"]),
                      float(calculo["total"]), float(calculo["costo_unidad"])])
    return {"titulo": "Costos de recetas",
            "encabezados": ["Receta", "Rendimiento", "Costo total", "Costo por unidad"],
            "filas": filas, "formatos": [None, None, "money", "money"],
            "resumen": _resumen("Recetas", len(filas), "number")}


def _fabricados(con):
    filas = []
    for fila in con.execute("SELECT id FROM productos_fabricados ORDER BY nombre"):
        calculo = calcular_fabricado(con, fila["id"])
        filas.append([calculo["nombre"], calculo["receta"], calculo["cantidad_fabricada"],
                      float(calculo["costo_lote"]), float(calculo["costo_unidad"])])
    return {"titulo": "Productos fabricados",
            "encabezados": ["Producto", "Receta", "Cantidad fabricada", "Costo lote",
                            "Costo por unidad"],
            "filas": filas, "formatos": [None, None, None, "money", "money"],
            "resumen": _resumen("Productos", len(filas), "number")}


def _ventas(con, filtros):
    datos = listar_pedidos(con, {
        "desde": filtros.get("desde", ""),
        "hasta": filtros.get("hasta", ""),
        "canal": filtros.get("canal", ""),
        "estado": filtros.get("estado", ""),
        "cliente": filtros.get("cliente", ""),
    })
    filas = [[d["id"], a_fecha(d["fecha"]), CANALES.get(d["canal"], d["canal"]),
              d["cliente_nombre"] or "", ESTADOS.get(d["estado"], d["estado"]),
              d["total"], float(d["ganancia"])] for d in datos]
    total = sum(d["total"] or 0 for d in datos)
    return {"titulo": "Ventas",
            "encabezados": ["ID", "Fecha", "Canal", "Cliente", "Estado", "Total", "Ganancia"],
            "filas": filas, "formatos": [None, "date", None, None, None, "money", "money"],
            "resumen": _resumen("Total vendido", total)}


def reporte_a_libro(con, tipo, filtros=None):
    reporte = construir_reporte(con, tipo, filtros)
    wb = Workbook()
    wb.remove(wb.active)
    agregar_hoja(wb, reporte["titulo"][:31], reporte["encabezados"],
                 reporte["filas"], reporte["formatos"])
    return wb


# FIN services/reportes.py
