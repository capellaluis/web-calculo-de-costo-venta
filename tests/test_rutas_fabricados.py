"""Pruebas de las rutas de Productos fabricados (base temporal)."""

import app as appmod


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def crear_receta(con):
    producto = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id, precio_actual)"
        " VALUES ('Masa', ?, ?, 4860)", (uid(con, "kg"), uid(con, "g"))).lastrowid
    receta = con.execute(
        "INSERT INTO recetas (nombre, rendimiento_cantidad, rendimiento_unidad)"
        " VALUES ('Tequeños', 1, 'lote')").lastrowid
    con.execute(
        "INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad_id)"
        " VALUES (?, ?, 1000, ?)", (receta, producto, uid(con, "g")))
    con.commit()
    return receta


def test_lista_vacia(db_temporal):
    respuesta = appmod.app.test_client().get("/fabricados/")
    assert respuesta.status_code == 200
    assert "Productos fabricados" in respuesta.get_data(as_text=True)


def test_crear_y_ver_tequenos(db_temporal, con):
    receta = crear_receta(con)
    cliente = appmod.app.test_client()

    respuesta = cliente.post("/fabricados/nuevo", data={
        "nombre": "Tequeños",
        "receta_id": str(receta),
        "cantidad_fabricada": "20",
        "notas": "",
        "pres_nombre": ["x6", "x12"],
        "pres_cantidad": ["6", "12"],
    })
    assert respuesta.status_code == 302

    fabricado_id = con.execute("SELECT id FROM productos_fabricados").fetchone()[0]
    texto = cliente.get("/fabricados/%d" % fabricado_id).get_data(as_text=True)
    assert "243" in texto      # costo por unidad
    assert "1.458" in texto    # costo de la presentación x6
    assert "2.083" in texto    # 1458 / 0,70


# FIN tests/test_rutas_fabricados.py
