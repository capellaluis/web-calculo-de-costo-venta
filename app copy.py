import os

from flask import Flask

# Lee el archivo .env (si existe y python-dotenv esta instalado)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from database.db import obtener_conexion
from routes.dashboard import bp as dashboard_bp
from routes.proveedores import bp as proveedores_bp
from routes.productos import bp as productos_bp
from routes.compras import bp as compras_bp
from routes.precios import bp as precios_bp
from routes.recetas import bp as recetas_bp
from routes.costos import bp as costos_bp
from routes.configuracion import bp as configuracion_bp
from routes.fabricados import bp as fabricados_bp
from routes.excel import bp as excel_bp
from routes.reportes import bp as reportes_bp
from routes.copias import bp as copias_bp
from routes.auth import bp as auth_bp
from services.seguridad import obtener_secret_key

app = Flask(__name__)
# La clave secreta viene del .env o de un archivo local (para mantener la sesión).
app.secret_key = obtener_secret_key()
app.config.setdefault("REQUIERE_LOGIN", True)

app.register_blueprint(dashboard_bp)
app.register_blueprint(proveedores_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(precios_bp)
app.register_blueprint(recetas_bp)
app.register_blueprint(costos_bp)
app.register_blueprint(configuracion_bp)
app.register_blueprint(fabricados_bp)
app.register_blueprint(excel_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(copias_bp)
app.register_blueprint(auth_bp)


ENDPOINTS_SIN_LOGIN = {"auth.login", "auth.recuperar", "auth.recuperar_cambiar", "static"}


@app.before_request
def requerir_login():
    if not app.config.get("REQUIERE_LOGIN", True):
        return None
    from flask import redirect, request, session, url_for
    if request.endpoint in ENDPOINTS_SIN_LOGIN or request.endpoint is None:
        return None
    if not session.get("usuario"):
        return redirect(url_for("auth.login"))
    return None


def formato_moneda(valor):
    """Muestra 30000 como $30.000 y 1234.5 como $1.234,50."""
    valor = valor or 0
    texto = "{:,.2f}".format(valor)
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    if texto.endswith(",00"):
        texto = texto[:-3]
    return "$" + texto


app.add_template_filter(formato_moneda, "moneda")


# Endpoints que NO disparan copia automática (ya manejan su propia copia).
ENDPOINTS_SIN_COPIA = {"copias.crear", "copias.restaurar", "copias.eliminar",
                       "auth.login", "auth.logout", "static"}


@app.after_request
def copia_automatica(response):
    """Crea una copia de seguridad automáticamente después de cada cambio."""
    from flask import request
    if (request.method == "POST" and response.status_code == 302
            and request.endpoint not in ENDPOINTS_SIN_COPIA):
        try:
            from services.copias import crear_copia, limitar_copias
            crear_copia()
            limitar_copias(limite=30)
        except Exception:
            pass
    return response


@app.context_processor
def inyectar_negocio():
    """Deja el nombre y el logo disponibles en todas las plantillas."""
    try:
        from services.negocio import leer_negocio
        conexion = obtener_conexion()
        try:
            negocio = leer_negocio(conexion)
        finally:
            conexion.close()
    except Exception:
        negocio = {"nombre": "Mi Negocio", "logo": ""}
    return {"negocio": negocio}


if __name__ == "__main__":
    # Aplica migraciones pendientes (hace copia de seguridad antes de tocar la base)
    from database.migrar import migrar
    migrar()
    # Todo se configura en el archivo .env (ver .env.example)
    host = os.environ.get("APP_HOST", "127.0.0.1")
    puerto = int(os.environ.get("APP_PORT", "5000"))
    depuracion = os.environ.get("APP_DEBUG", "0") == "1"
    app.run(host=host, port=puerto, debug=depuracion)
