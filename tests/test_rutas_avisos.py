"""Pruebas de los avisos como notificaciones flotantes (base temporal)."""

from pathlib import Path

import app as appmod

PLANTILLAS = Path(__file__).resolve().parent.parent / "templates"


def _html(url):
    return appmod.app.test_client().get(url).get_data(as_text=True)


def _toast(html):
    """Marcado de la primera notificación, dentro del contenedor .toasts."""
    caja = html.split('<div class="toasts"')[1]
    return '<div class="toast ' + caja.split('<div class="toast ')[1]


def test_aviso_de_exito_es_notificacion_con_cierre(db_temporal, monkeypatch):
    monkeypatch.delenv("APP_AVISO_SEGUNDOS", raising=False)
    toast = _toast(_html("/proveedores/?aviso=eliminado"))
    assert toast.startswith('<div class="toast toast-exito"')
    assert 'role="status"' in toast
    assert 'data-segundos="5"' in toast
    assert "Proveedor eliminado." in toast
    assert 'aria-label="Cerrar aviso"' in toast


def test_aviso_de_error_usa_estilo_error(db_temporal):
    toast = _toast(_html("/proveedores/?aviso=con_compras"))
    assert toast.startswith('<div class="toast toast-error"')
    assert 'role="alert"' in toast


def test_segundos_configurables_por_entorno(db_temporal, monkeypatch):
    monkeypatch.setenv("APP_AVISO_SEGUNDOS", "8")
    html = _html("/proveedores/?aviso=eliminado")
    assert 'data-segundos="8"' in _toast(html)
    # El contenedor también lo expone para UI.notificar desde JS.
    assert 'id="toasts" data-segundos="8"' in html


def test_sin_aviso_no_hay_notificacion(db_temporal):
    html = _html("/proveedores/")
    assert 'class="toasts"' in html  # contenedor listo para UI.notificar
    assert 'class="toast ' not in html


def test_aviso_de_texto_suelto_es_exito(db_temporal):
    html = _html("/costos/?aviso=guardado")
    assert 'class="toast toast-exito"' in html


def test_plantillas_no_pintan_avisos_a_mano():
    for p in PLANTILLAS.glob("*.html"):
        fuente = p.read_text(encoding="utf-8")
        assert "{{ aviso }}" not in fuente, p.name
        assert "in aviso" not in fuente, p.name


# FIN tests/test_rutas_avisos.py
