"""Pruebas de Reportes (Fase 14)."""

import app as appmod
import routes.reportes as reportesmod
from services.reportes import construir_reporte


def test_reporte_compras_filtra_por_proveedor_y_fecha(con):
    sur = con.execute("INSERT INTO proveedores (nombre) VALUES ('Sur')").lastrowid
    norte = con.execute("INSERT INTO proveedores (nombre) VALUES ('Norte')").lastrowid
    con.execute("INSERT INTO compras (proveedor_id, fecha, total)"
                " VALUES (?, '2026-09-10', 30000)", (sur,))
    con.execute("INSERT INTO compras (proveedor_id, fecha, total)"
                " VALUES (?, '2026-09-15', 5000)", (sur,))
    con.execute("INSERT INTO compras (proveedor_id, fecha, total)"
                " VALUES (?, '2026-09-20', 9999)", (norte,))
    con.commit()

    reporte = construir_reporte(con, "compras", {
        "proveedor": str(sur), "desde": "2026-09-01", "hasta": "2026-09-30"})

    assert len(reporte["filas"]) == 2
    assert reporte["resumen"]["valor"] == 35000


def test_todos_los_tipos_se_construyen(con):
    for tipo in ["compras", "proveedores", "productos", "historial", "costos", "fabricados"]:
        reporte = construir_reporte(con, tipo, {})
        assert reporte["encabezados"]
        assert "filas" in reporte


def test_pantalla_reportes(db_temporal):
    respuesta = appmod.app.test_client().get("/reportes/")
    assert respuesta.status_code == 200
    assert "Reportes" in respuesta.get_data(as_text=True)


def test_exportar_reporte(db_temporal, tmp_path, monkeypatch):
    monkeypatch.setattr(reportesmod, "CARPETA_EXPORTS", tmp_path / "exports")
    respuesta = appmod.app.test_client().get("/reportes/exportar?tipo=compras")
    assert respuesta.status_code == 200
    assert "spreadsheetml" in respuesta.headers["Content-Type"]
    assert list((tmp_path / "exports").glob("*.xlsx"))


# FIN tests/test_reportes.py
