"""Pruebas del modal que confirma acciones destructivas (base temporal)."""

from pathlib import Path

import app as appmod

PLANTILLAS = Path(__file__).resolve().parent.parent / "templates"


def _fuente(nombre):
    return (PLANTILLAS / nombre).read_text(encoding="utf-8")


def test_ninguna_plantilla_usa_confirm_del_navegador():
    con_confirm = [
        p.name for p in PLANTILLAS.glob("*.html")
        if "confirm(" in p.read_text(encoding="utf-8")
    ]
    assert con_confirm == []


def test_base_carga_componentes_de_interfaz(db_temporal):
    cliente = appmod.app.test_client()
    html = cliente.get("/precios/").get_data(as_text=True)
    assert "js/ui.js" in html


def test_borrar_proveedor_pide_confirmacion_con_modal(con):
    con.execute("INSERT INTO proveedores (nombre) VALUES ('Distribuidora')")
    con.commit()
    cliente = appmod.app.test_client()
    html = cliente.get("/proveedores/").get_data(as_text=True)
    form = html.split('action="/proveedores/1/eliminar"')[1]
    form = form.split("</form>")[0]
    assert 'data-confirmar="¿Eliminar este proveedor?"' in form
    assert 'name="csrf_token"' in form
    # El botón de la fila sigue discreto; el rojo va en el modal.
    assert "btn-peligro" not in form


def test_restaurar_copia_usa_boton_de_restaurar():
    assert 'boton="Sí, restaurar"' in _fuente("copias.html")


def test_quitar_logo_pide_confirmacion():
    fuente = _fuente("config_margenes.html")
    assert '"¿Quitar el logo?"' in fuente
    assert 'campos={"accion": "quitar_logo"}' in fuente


# FIN tests/test_rutas_confirmacion.py
