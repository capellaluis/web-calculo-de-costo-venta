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

app = Flask(__name__)
# La clave secreta viene del archivo .env. Si falta, se usa una temporal
# (sirve para desarrollar, pero se pierde al reiniciar).
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32).hex()

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


def formato_moneda(valor):
    """Muestra 30000 como $30.000 y 1234.5 como $1.234,50."""
    valor = valor or 0
    texto = "{:,.2f}".format(valor)
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    if texto.endswith(",00"):
        texto = texto[:-3]
    return "$" + texto


app.add_template_filter(formato_moneda, "moneda")


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
