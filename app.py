from flask import Flask

from routes.dashboard import bp as dashboard_bp
from routes.proveedores import bp as proveedores_bp
from routes.productos import bp as productos_bp
from routes.compras import bp as compras_bp
from routes.precios import bp as precios_bp
from routes.recetas import bp as recetas_bp
from routes.costos import bp as costos_bp
from routes.configuracion import bp as configuracion_bp
from routes.fabricados import bp as fabricados_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)
app.register_blueprint(proveedores_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(precios_bp)
app.register_blueprint(recetas_bp)
app.register_blueprint(costos_bp)
app.register_blueprint(configuracion_bp)
app.register_blueprint(fabricados_bp)


def formato_moneda(valor):
    """Muestra 30000 como $30.000 y 1234.5 como $1.234,50."""
    valor = valor or 0
    texto = "{:,.2f}".format(valor)
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    if texto.endswith(",00"):
        texto = texto[:-3]
    return "$" + texto


app.add_template_filter(formato_moneda, "moneda")


if __name__ == "__main__":
    # Aplica migraciones pendientes (hace copia de seguridad antes de tocar la base)
    from database.migrar import migrar
    migrar()
    # host 0.0.0.0 permite entrar desde otros dispositivos de tu red Wi-Fi
    app.run(host="0.0.0.0", port=5000, debug=True)


# FIN app.py
