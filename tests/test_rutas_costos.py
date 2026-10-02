"""Pruebas de la pantalla de Costos y del Panel (base temporal)."""

import app as appmod


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def sembrar_chicha(con):
    azucar = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id, precio_actual)"
        " VALUES ('Azúcar', ?, ?, 1200)", (uid(con, "kg"), uid(con, "g"))).lastrowid
    receta = con.execute(
        "INSERT INTO recetas (nombre, rendimiento_cantidad, rendimiento_unidad)"
        " VALUES ('Chicha', 10, 'vasos')").lastrowid
    con.execute(
        "INSERT INTO receta_ingredientes (receta_id, producto_id, cantidad, unidad_id)"
        " VALUES (?, ?, 300, ?)", (receta, azucar, uid(con, "g")))
    con.commit()
    return receta


def test_pantalla_costos_se_abre(db_temporal):
    respuesta = appmod.app.test_client().get("/costos/")
    assert respuesta.status_code == 200
    assert "Costos" in respuesta.get_data(as_text=True)


def test_pantalla_costos_muestra_la_receta(db_temporal, con):
    sembrar_chicha(con)
    texto = appmod.app.test_client().get("/costos/").get_data(as_text=True)
    # Azúcar 300 g a $1.200/kg = $360; /10 vasos = $36.
    assert "Chicha" in texto
    assert "36" in texto


def test_panel_muestra_costo_de_recetas(db_temporal, con):
    sembrar_chicha(con)
    texto = appmod.app.test_client().get("/").get_data(as_text=True)
    assert "Costo de las recetas" in texto
    assert "360" in texto


# FIN tests/test_rutas_costos.py
