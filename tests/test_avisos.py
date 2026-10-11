"""Pruebas de los avisos (notificaciones) que se muestran tras una acción."""

import pytest

from services.avisos import (
    ErrorAviso,
    crear_aviso,
    leer_aviso,
    segundos_por_defecto,
)

AVISOS = {
    "eliminado": "Proveedor eliminado.",
    "con_compras": crear_aviso("No se puede eliminar.", tipo="error"),
}


def test_texto_simple_es_aviso_de_exito():
    aviso = leer_aviso(AVISOS, "eliminado")
    assert aviso == {"texto": "Proveedor eliminado.", "tipo": "exito",
                     "segundos": None}


def test_aviso_con_tipo_se_respeta():
    assert leer_aviso(AVISOS, "con_compras")["tipo"] == "error"


@pytest.mark.parametrize("clave", [None, "", "inexistente"])
def test_clave_desconocida_no_muestra_nada(clave):
    assert leer_aviso(AVISOS, clave) is None


@pytest.mark.parametrize("tipo", ["info", "exito", "advertencia", "error"])
def test_cuatro_tipos_validos(tipo):
    assert crear_aviso("Hola", tipo=tipo)["tipo"] == tipo


def test_tipo_invalido_falla():
    with pytest.raises(ErrorAviso):
        crear_aviso("Hola", tipo="success")


def test_segundos_negativos_fallan():
    with pytest.raises(ErrorAviso):
        crear_aviso("Hola", segundos=-1)


@pytest.mark.parametrize("valor, esperado", [
    (None, 5), ("8", 8), ("2.5", 2.5), ("0", 0), ("-1", 5), ("abc", 5),
])
def test_segundos_por_defecto_desde_entorno(monkeypatch, valor, esperado):
    if valor is None:
        monkeypatch.delenv("APP_AVISO_SEGUNDOS", raising=False)
    else:
        monkeypatch.setenv("APP_AVISO_SEGUNDOS", valor)
    assert segundos_por_defecto() == esperado


# FIN tests/test_avisos.py
