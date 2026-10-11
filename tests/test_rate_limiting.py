"""Pruebas del rate limiting en login y recuperación."""

import pytest
import app as appmod
from services.rate_limit import limiter
from services.usuarios import crear_usuario


def test_rate_limiting_desactivado_en_tests(db_temporal):
    """Verifica que el rate limiting está desactivado en los tests normales."""
    assert limiter.enabled is False


@pytest.mark.parametrize("limite,endpoint,datos", [
    (5, "/login", {"usuario": "test", "password": "bad"}),
    (3, "/recuperar", {}),
])
def test_rate_limiting_se_puede_activar(db_temporal, con, limite, endpoint, datos):
    """Verifica que el rate limiting se puede activar y funciona."""
    if endpoint == "/recuperar":
        crear_usuario(con, "admin", "1234", "admin@test.com")

    original = limiter.enabled
    limiter.enabled = True
    appmod.app.config["REQUIERE_LOGIN"] = False

    try:
        cliente = appmod.app.test_client()

        for i in range(limite + 1):
            respuesta = cliente.post(endpoint, data=datos)
            if i < limite:
                assert respuesta.status_code != 429, (
                    f"Intento {i+1} bloqueado prematuramente (status {respuesta.status_code})"
                )
            else:
                assert respuesta.status_code == 429, (
                    f"Intento {i+1} debería ser 429, obtuvo {respuesta.status_code}"
                )
    finally:
        limiter.enabled = original


# FIN tests/test_rate_limiting.py
