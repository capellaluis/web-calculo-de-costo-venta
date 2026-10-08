-- Migración 003: pedidos/ventas y su detalle. Aditiva.
CREATE TABLE IF NOT EXISTS pedidos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha           TEXT NOT NULL,
    canal           TEXT NOT NULL DEFAULT 'tienda',
    cliente_nombre  TEXT,
    forma_pago      TEXT,
    descuento       REAL NOT NULL DEFAULT 0,
    estado          TEXT NOT NULL DEFAULT 'nuevo',
    notas           TEXT,
    total           REAL NOT NULL DEFAULT 0,
    creado_en       TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS pedido_items (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id              INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_fabricado_id  INTEGER REFERENCES productos_fabricados(id),
    presentacion_id        INTEGER REFERENCES presentaciones(id),
    descripcion            TEXT NOT NULL,
    cantidad               REAL NOT NULL,
    precio_unitario        REAL NOT NULL
);
