"""Pruebas del menú base: botones de tema en TopBar y sidebar (base temporal)."""

import app as appmod


def test_botones_de_tema_en_topbar_y_sidebar(db_temporal):
    html = appmod.app.test_client().get("/precios/").get_data(as_text=True)
    topbar = html.split('<header class="topbar">')[1].split("</header>")[0]
    sidebar = html.split('<nav class="menu"')[1].split("</nav>")[0]
    assert "data-tema-toggle" in topbar
    assert "data-tema-toggle" in sidebar
    # Ya no hay botón flotante fuera de TopBar y sidebar.
    assert html.count("data-tema-toggle") == 2
    assert 'id="botonTema"' not in html


# FIN tests/test_rutas_menu.py
