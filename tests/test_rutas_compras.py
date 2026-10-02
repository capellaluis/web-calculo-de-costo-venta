"""Pruebas de las rutas de Compras con el cliente de pruebas de Flask.

Usan la base TEMPORAL (fixture db_temporal), nunca database/negocio.db.
"""

import app as appmod


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def preparar(con):
    proveedor = con.execute(
        "INSERT INTO proveedores (nombre) VALUES ('Distribuidora Sur')").lastrowid
    producto = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id, precio_actual)"
        " VALUES ('Azúcar', ?, ?, 0)", (uid(con, "kg"), uid(con, "g"))).lastrowid
    con.commit()
    return proveedor, producto


def test_lista_de_compras_se_abre(db_temporal):
    respuesta = appmod.app.test_client().get("/compras/")
    assert respuesta.status_code == 200
    assert "Compras" in respuesta.get_data(as_text=True)


def test_nueva_compra_guarda_y_redirige(db_temporal, con):
    proveedor, producto = preparar(con)
    cliente = appmod.app.test_client()

    respuesta = cliente.post("/compras/nueva", data={
        "proveedor_id": str(proveedor),
        "fecha": "2026-01-10",
        "numero_documento": "A-0001",
        "observaciones": "",
        "producto_id": [str(producto)],
        "cantidad": ["25"],
        "unidad_id": [str(uid(con, "kg"))],
        "precio_total": ["30000"],
    })

    assert respuesta.status_code == 302
    assert "/compras/" in respuesta.headers["Location"]
    assert con.execute(
        "SELECT precio_actual FROM productos WHERE id = ?", (producto,)).fetchone()[0] == 1200
    assert con.execute("SELECT COUNT(*) FROM compras").fetchone()[0] == 1


def test_nueva_compra_con_unidad_incompatible_no_guarda(db_temporal, con):
    proveedor, producto = preparar(con)
    cliente = appmod.app.test_client()

    respuesta = cliente.post("/compras/nueva", data={
        "proveedor_id": str(proveedor),
        "fecha": "2026-01-10",
        "numero_documento": "",
        "observaciones": "",
        "producto_id": [str(producto)],
        "cantidad": ["1"],
        "unidad_id": [str(uid(con, "ml"))],
        "precio_total": ["100"],
    })

    assert respuesta.status_code == 200
    assert "no es compatible" in respuesta.get_data(as_text=True)
    assert con.execute("SELECT COUNT(*) FROM compras").fetchone()[0] == 0


# FIN tests/test_rutas_compras.py
