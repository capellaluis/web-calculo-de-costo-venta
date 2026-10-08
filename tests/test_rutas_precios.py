"""Pruebas de las rutas de Historial de precios y del Panel principal (base temporal)."""

import app as appmod


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def crear_producto_con_aumento(con):
    producto_id = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id)"
        " VALUES ('Azúcar', ?, ?)", (uid(con, "kg"), uid(con, "g"))).lastrowid
    for fecha, precio in [("2026-01-01", 1200), ("2026-02-01", 1350), ("2026-03-01", 1500)]:
        con.execute(
            "INSERT INTO historial_precios (producto_id, fecha, precio_unitario, unidad_id)"
            " VALUES (?, ?, ?, ?)", (producto_id, fecha, precio, uid(con, "kg")))
    con.commit()
    return producto_id


def test_lista_de_precios_se_abre(db_temporal):
    respuesta = appmod.app.test_client().get("/precios/")
    assert respuesta.status_code == 200
    assert "Historial de precios" in respuesta.get_data(as_text=True)


def test_lista_muestra_el_aumento(db_temporal, con):
    crear_producto_con_aumento(con)
    respuesta = appmod.app.test_client().get("/precios/")
    texto = respuesta.get_data(as_text=True)
    assert "Azúcar" in texto
    assert "1.500" in texto


def test_filtro_solo_aumentos(db_temporal, con):
    cliente = appmod.app.test_client()

    # Un producto que sube y otro que no tiene variación.
    crear_producto_con_aumento(con)
    otro = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id)"
        " VALUES ('SalFina', ?, ?)", (uid(con, "kg"), uid(con, "g"))).lastrowid
    con.execute(
        "INSERT INTO historial_precios (producto_id, fecha, precio_unitario, unidad_id)"
        " VALUES (?, '2026-01-01', 500, ?)", (otro, uid(con, "kg")))
    con.commit()

    texto = cliente.get("/precios/?solo_aumentos=1").get_data(as_text=True)
    assert "Azúcar" in texto
    assert "SalFina" not in texto


def test_detalle_del_producto(db_temporal, con):
    producto_id = crear_producto_con_aumento(con)
    respuesta = appmod.app.test_client().get("/precios/%d" % producto_id)
    texto = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 200
    assert "Evolución del precio" in texto
    assert "Aumentó" in texto


def test_panel_principal_muestra_aumentos(db_temporal, con):
    crear_producto_con_aumento(con)
    texto = appmod.app.test_client().get("/").get_data(as_text=True)
    assert "Productos cuyo costo aumentó" in texto
    assert "Azúcar" in texto


# FIN tests/test_rutas_precios.py
