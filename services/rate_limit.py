"""Rate limiting para login y recuperación de contraseña.

Usa Flask-Limiter con almacenamiento en memoria (adecuado para LAN).
Las reglas se aplican por IP remota.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# FIN services/rate_limit.py
