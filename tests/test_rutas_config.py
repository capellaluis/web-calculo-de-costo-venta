"""Pruebas de Configuración (gastos y márgenes) y su efecto en Costos."""

import app as appmod


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def sembrar_receta_costo_294(con):
    producto = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id, precio_actual)"
        " VALUES ('Azúcar', ?, ?, 2940)", (uid(con, "kg"), uid(con, "g"))).lastrowid
    receta = con.execute(
        "INSERT INTO recetas (nombre, rendimiento_cantidad, rendimiento_unidad)"
        " VALUES ('Chicha', 1, 'vaso')").lastrowid
    con.execute(
        "INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad_id)"
        " VALUES (?, ?, 100, ?)", (receta, producto, uid(con, "g")))
    con.commit()


def test_pantalla_configuracion(db_temporal):
    respuesta = appmod.app.test_client().get("/config/")
    assert respuesta.status_code == 200
    assert "Gastos fijos" in respuesta.get_data(as_text=True)


def test_costos_sin_gastos_usa_margenes_por_defecto(db_temporal, con):
    sembrar_receta_costo_294(con)
    texto = appmod.app.test_client().get("/costos/").get_data(as_text=True)
    # 294 / 0,70 = 420 ; 294 / 0,50 = 588 ; 294 / 0,30 = 980
    assert "420" in texto and "588" in texto and "980" in texto


def test_guardar_gastos_y_margenes_recalcula(db_temporal, con):
    sembrar_receta_costo_294(con)
    cliente = appmod.app.test_client()

    respuesta = cliente.post("/config/", data={
        "costo_ejemplo": "500",
        "gasto_nombre": ["Gas", "Agua", "Luz"],
        "gasto_porcentaje": ["5", "3", "4"],
        "margen1_nombre": "Margen 1", "margen1_porcentaje": "30",
        "margen2_nombre": "Margen 2", "margen2_porcentaje": "50",
        "margen3_nombre": "Margen 3", "margen3_porcentaje": "70",
        "redondeo": "entero",
    })
    assert respuesta.status_code == 302

    texto = cliente.get("/costos/").get_data(as_text=True)
    # 294 + 12 % = 329,28 -> /0,70 = 470 ; /0,50 = 659 ; /0,30 = 1098 -> "$1.098"
    assert "470" in texto and "659" in texto and "1.098" in texto


def test_costos_tiene_el_formulario_para_escribir(db_temporal):
    texto = appmod.app.test_client().get("/costos/").get_data(as_text=True)
    assert "Escribí tus porcentajes" in texto
    assert 'name="gasto_porcentaje"' in texto
    assert 'name="margen1_porcentaje"' in texto


def test_guardar_desde_costos_vuelve_a_costos(db_temporal, con):
    sembrar_receta_costo_294(con)
    respuesta = appmod.app.test_client().post("/config/", data={
        "destino": "costos",
        "costo_ejemplo": "500",
        "gasto_nombre": ["Gas"], "gasto_porcentaje": ["10"],
        "margen1_nombre": "Margen 1", "margen1_porcentaje": "30",
        "margen2_nombre": "Margen 2", "margen2_porcentaje": "50",
        "margen3_nombre": "Margen 3", "margen3_porcentaje": "70",
        "redondeo": "entero",
    })
    assert respuesta.status_code == 302
    assert "/costos/" in respuesta.headers["Location"]


def test_agregar_y_quitar_gastos(db_temporal, con):
    cliente = appmod.app.test_client()
    cliente.post("/config/", data={
        "costo_ejemplo": "500",
        "gasto_nombre": ["Gas", "Alquiler"],
        "gasto_porcentaje": ["5", "10"],
        "margen1_nombre": "Margen 1", "margen1_porcentaje": "30",
        "margen2_nombre": "Margen 2", "margen2_porcentaje": "50",
        "margen3_nombre": "Margen 3", "margen3_porcentaje": "70",
        "redondeo": "entero",
    })
    nombres = [f[0] for f in con.execute("SELECT nombre FROM gastos ORDER BY orden")]
    assert nombres == ["Gas", "Alquiler"]


# FIN tests/test_rutas_config.py
