from flask import Flask

from routes.dashboard import bp as dashboard_bp
from routes.proveedores import bp as proveedores_bp
from routes.productos import bp as productos_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)
app.register_blueprint(proveedores_bp)
app.register_blueprint(productos_bp)


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
    # host 0.0.0.0 permite entrar desde otros dispositivos de tu red Wi-Fi
    app.run(host="0.0.0.0", port=5000, debug=True)


# FIN app.py
