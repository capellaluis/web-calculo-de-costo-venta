"""Pruebas de Configuración (valores por defecto) y de la plantilla."""

import app as appmod
from services.fabricados import leer_plantilla


def _datos_plantilla():
    return {
        "costo_ejemplo": "500",
        "gasto_nombre": ["Gas", "Agua", "Luz"],
        "gasto_porcentaje": ["5", "3", "4"],
        "margen1_nombre": "Margen 1", "margen1_porcentaje": "30",
        "margen2_nombre": "Margen 2", "margen2_porcentaje": "50",
        "margen3_nombre": "Margen 3", "margen3_porcentaje": "70",
        "margen_elegido": "1",
        "del_nombre": ["Comisión", "IVA", "2,9%"],
        "del_porcentaje": ["5", "0", "2.9"],
        "redondeo": "entero",
    }


def test_pantalla_configuracion(db_temporal):
    texto = appmod.app.test_client().get("/config/").get_data(as_text=True)
    assert "Gastos fijos" in texto
    assert "Delivery" in texto
    assert "Márgenes de ganancia" in texto


def test_guardar_plantilla(db_temporal, con):
    respuesta = appmod.app.test_client().post("/config/", data=_datos_plantilla())
    assert respuesta.status_code == 302

    plantilla = leer_plantilla(con)
    assert plantilla["gastos"] == [{"nombre": "Gas", "porcentaje": 5},
                                   {"nombre": "Agua", "porcentaje": 3},
                                   {"nombre": "Luz", "porcentaje": 4}]
    assert plantilla["margenes"][0]["porcentaje"] == 30
    assert plantilla["delivery"][2]["porcentaje"] == 2.9


def test_validacion_delivery_mayor_100(db_temporal):
    datos = _datos_plantilla()
    datos["del_porcentaje"] = ["60", "0", "50"]
    respuesta = appmod.app.test_client().post("/config/", data=datos)
    assert respuesta.status_code == 200
    assert "delivery" in respuesta.get_data(as_text=True).lower()


# FIN tests/test_rutas_config.py
