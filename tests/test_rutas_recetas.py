"""Pruebas de las rutas de Recetas con el cliente de Flask (base temporal)."""

import app as appmod
from services.recetas import calcular_receta


def uid(con, abreviatura):
    return con.execute(
        "SELECT id FROM unidades WHERE abreviatura = ?", (abreviatura,)).fetchone()["id"]


def preparar_productos(con):
    ids = {}
    for nombre, compra, uso, precio in [
            ("Maíz", "kg", "g", 200), ("Azúcar", "kg", "g", 1200),
            ("Leche", "l", "ml", 1000), ("Canela", "kg", "g", 8000)]:
        ids[nombre] = con.execute(
            "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id, precio_actual)"
            " VALUES (?, ?, ?, ?)",
            (nombre, uid(con, compra), uid(con, uso), precio)).lastrowid
    con.commit()
    return ids


def test_lista_de_recetas_vacia(db_temporal):
    respuesta = appmod.app.test_client().get("/recetas/")
    assert respuesta.status_code == 200
    assert "Recetas" in respuesta.get_data(as_text=True)


def test_crear_receta_chicha_y_ver_costo(db_temporal, con):
    productos = preparar_productos(con)
    cliente = appmod.app.test_client()

    respuesta = cliente.post("/recetas/nueva", data={
        "nombre": "Chicha",
        "descripcion": "",
        "rendimiento_cantidad": "10",
        "rendimiento_unidad": "vasos",
        "notas": "",
        "producto_id": [str(productos["Maíz"]), str(productos["Azúcar"]),
                        str(productos["Leche"]), str(productos["Canela"])],
        "cantidad": ["500", "300", "1", "10"],
        "unidad_id": [str(uid(con, "g")), str(uid(con, "g")),
                      str(uid(con, "l")), str(uid(con, "g"))],
    })

    assert respuesta.status_code == 302
    receta_id = con.execute("SELECT id FROM recetas").fetchone()[0]

    calculo = calcular_receta(con, receta_id)
    assert calculo["total"] == 1540
    assert calculo["costo_unidad"] == 154

    texto = cliente.get("/recetas/%d" % receta_id).get_data(as_text=True)
    assert "1.540" in texto
    assert "154" in texto


def test_receta_con_unidad_incompatible_no_guarda(db_temporal, con):
    producto = con.execute(
        "INSERT INTO productos (nombre, unidad_compra_id, unidad_uso_id)"
        " VALUES ('Azúcar', ?, ?)", (uid(con, "kg"), uid(con, "g"))).lastrowid
    con.commit()

    respuesta = appmod.app.test_client().post("/recetas/nueva", data={
        "nombre": "Prueba",
        "rendimiento_cantidad": "1",
        "rendimiento_unidad": "unidad",
        "producto_id": [str(producto)],
        "cantidad": ["1"],
        "unidad_id": [str(uid(con, "ml"))],
    })

    assert respuesta.status_code == 200
    assert "no es compatible" in respuesta.get_data(as_text=True)
    assert con.execute("SELECT COUNT(*) FROM recetas").fetchone()[0] == 0


# FIN tests/test_rutas_recetas.py
