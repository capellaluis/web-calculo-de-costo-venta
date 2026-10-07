-- Migración 002: precios por producto fabricado.
-- Cada producto fabricado guarda sus gastos, sus 3 márgenes y sus % de delivery.
-- Es aditiva: no borra ni modifica datos existentes.
CREATE TABLE IF NOT EXISTS fabricado_gastos (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_fabricado_id  INTEGER NOT NULL REFERENCES productos_fabricados(id) ON DELETE CASCADE,
    nombre                 TEXT NOT NULL,
    porcentaje             REAL NOT NULL DEFAULT 0,
    orden                  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fabricado_margenes (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_fabricado_id  INTEGER NOT NULL REFERENCES productos_fabricados(id) ON DELETE CASCADE,
    numero                 INTEGER NOT NULL,
    nombre                 TEXT NOT NULL,
    porcentaje             REAL NOT NULL DEFAULT 0,
    elegido                INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fabricado_delivery (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_fabricado_id  INTEGER NOT NULL REFERENCES productos_fabricados(id) ON DELETE CASCADE,
    nombre                 TEXT NOT NULL,
    porcentaje             REAL NOT NULL DEFAULT 0,
    orden                  INTEGER NOT NULL DEFAULT 0
);
