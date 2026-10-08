"""Pruebas de la exportación a Excel (Fase 13)."""

from decimal import Decimal

import app as appmod
import routes.excel as excelmod
from services.exportar_excel import construir_libro

HOJAS = ["Proveedores", "Productos", "Compras", "Detalle Compras", "Historial Precios",
         "Recetas", "Ingredientes", "Productos Fabricados", "Costos y Precios",
         "Ventas", "Detalle Ventas"]


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def sembrar(con):
    producto = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id, precio_actual)"
        " VALUES ('Azúcar', ?, ?, 1200)", (uid(con, "kg"), uid(con, "g"))).lastrowid
    receta = con.execute(
        "INSERT INTO recetas (nombre, rendimiento_cantidad, rendimiento_unidad)"
        " VALUES ('Chicha', 10, 'vasos')").lastrowid
    con.execute(
        "INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad_id)"
        " VALUES (?, ?, 300, ?)", (receta, producto, uid(con, "g")))
    con.commit()
    return receta


def test_libro_tiene_todas_las_hojas(con):
    assert construir_libro(con).sheetnames == HOJAS


def test_libro_con_datos(con):
    sembrar(con)
    libro = construir_libro(con)
    assert libro["Productos"].max_row == 2      # encabezado + 1
    assert libro["Recetas"].max_row == 2
    assert libro["Ingredientes"].max_row == 2


def test_pantalla_excel(db_temporal):
    respuesta = appmod.app.test_client().get("/excel/")
    assert respuesta.status_code == 200
    assert "Exportar a Excel" in respuesta.get_data(as_text=True)


def test_descarga_genera_xlsx(db_temporal, tmp_path, monkeypatch):
    monkeypatch.setattr(excelmod, "CARPETA_EXPORTS", tmp_path / "exports")
    respuesta = appmod.app.test_client().get("/excel/descargar")
    assert respuesta.status_code == 200
    assert "spreadsheetml" in respuesta.headers["Content-Type"]
    assert respuesta.data[:2] == b"PK"  # firma de un archivo xlsx (zip)
    assert list((tmp_path / "exports").glob("*.xlsx"))


# FIN tests/test_excel.py
