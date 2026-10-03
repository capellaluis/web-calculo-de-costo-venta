-- Migración 001: agrega la tabla de GASTOS fijos (gas, agua, luz, ...).
-- Es aditiva: no borra ni modifica datos existentes.
CREATE TABLE IF NOT EXISTS gastos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    porcentaje  REAL NOT NULL DEFAULT 0,
    orden       INTEGER NOT NULL DEFAULT 0,
    creado_en   TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Gastos iniciales (solo si la tabla está vacía)
INSERT INTO gastos (nombre, porcentaje, orden)
SELECT nombre, 0, orden FROM (
    SELECT 'Gas' AS nombre, 0 AS orden
    UNION ALL SELECT 'Agua', 1
    UNION ALL SELECT 'Luz', 2
) WHERE NOT EXISTS (SELECT 1 FROM gastos);
