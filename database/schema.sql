-- =====================================================
-- MI NEGOCIO - Plano de la base de datos (SQLite)
-- =====================================================

-- ---------- UNIDADES ----------
-- factor_base: cuántas unidades base contiene esta unidad.
-- Base de masa = gramo, base de volumen = mililitro, base de conteo = unidad.
-- Ejemplo: 1 kg = 1000 g  ->  factor_base = 1000
CREATE TABLE IF NOT EXISTS unidades (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL UNIQUE,
    abreviatura   TEXT NOT NULL UNIQUE,
    tipo          TEXT NOT NULL CHECK (tipo IN ('masa', 'volumen', 'conteo', 'empaque')),
    factor_base   REAL NOT NULL DEFAULT 1
);

-- ---------- CATEGORIAS ----------
CREATE TABLE IF NOT EXISTS categorias (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL UNIQUE,
    creado_en     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ---------- PROVEEDORES ----------
CREATE TABLE IF NOT EXISTS proveedores (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre            TEXT NOT NULL,
    razon_social      TEXT,
    cuit_rut          TEXT,
    telefono          TEXT,
    whatsapp          TEXT,
    email             TEXT,
    direccion         TEXT,
    persona_contacto  TEXT,
    notas             TEXT,
    creado_en         TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ---------- PRODUCTOS (materias primas) ----------
-- precio_actual = precio por 1 unidad de compra (ej: $/kg)
CREATE TABLE IF NOT EXISTS productos (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre                 TEXT NOT NULL,
    categoria_id           INTEGER REFERENCES categorias(id),
    unidad_compra_id       INTEGER NOT NULL REFERENCES unidades(id),
    unidad_uso_id          INTEGER NOT NULL REFERENCES unidades(id),
    precio_actual          REAL NOT NULL DEFAULT 0,
    proveedor_principal_id INTEGER REFERENCES proveedores(id),
    sku                    TEXT,
    notas                  TEXT,
    creado_en              TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ---------- COMPRAS ----------
CREATE TABLE IF NOT EXISTS compras (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    proveedor_id       INTEGER NOT NULL REFERENCES proveedores(id),
    fecha              TEXT NOT NULL,
    numero_documento   TEXT,
    observaciones      TEXT,
    total              REAL NOT NULL DEFAULT 0,
    creado_en          TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ---------- DETALLE DE COMPRAS ----------
-- precio_unitario = precio_total / cantidad (por la unidad indicada)
CREATE TABLE IF NOT EXISTS detalle_compras (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    compra_id        INTEGER NOT NULL REFERENCES compras(id) ON DELETE CASCADE,
    producto_id      INTEGER NOT NULL REFERENCES productos(id),
    cantidad         REAL NOT NULL,
    unidad_id        INTEGER NOT NULL REFERENCES unidades(id),
    precio_total     REAL NOT NULL,
    precio_unitario  REAL NOT NULL
);

-- ---------- HISTORIAL DE PRECIOS ----------
-- Nunca se borra: cada compra deja un registro del precio de ese día.
CREATE TABLE IF NOT EXISTS historial_precios (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id        INTEGER NOT NULL REFERENCES productos(id),
    fecha              TEXT NOT NULL,
    precio_unitario    REAL NOT NULL,
    unidad_id          INTEGER NOT NULL REFERENCES unidades(id),
    detalle_compra_id  INTEGER REFERENCES detalle_compras(id) ON DELETE SET NULL,
    creado_en          TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ---------- RECETAS ----------
-- rendimiento: cuánto produce la receta (ej: 10 "vasos")
CREATE TABLE IF NOT EXISTS recetas (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre                TEXT NOT NULL,
    descripcion           TEXT,
    rendimiento_cantidad  REAL NOT NULL DEFAULT 1,
    rendimiento_unidad    TEXT NOT NULL DEFAULT 'unidades',
    notas                 TEXT,
    creado_en             TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ---------- INGREDIENTES DE RECETAS ----------
CREATE TABLE IF NOT EXISTS receta_ingredientes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    receta_id     INTEGER NOT NULL REFERENCES recetas(id) ON DELETE CASCADE,
    producto_id   INTEGER NOT NULL REFERENCES productos(id),
    cantidad      REAL NOT NULL,
    unidad_id     INTEGER NOT NULL REFERENCES unidades(id)
);

-- ---------- PRODUCTOS FABRICADOS ----------
-- cantidad_fabricada: unidades que produce un lote (ej: 20 tequeños)
CREATE TABLE IF NOT EXISTS productos_fabricados (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre              TEXT NOT NULL,
    receta_id           INTEGER NOT NULL REFERENCES recetas(id),
    cantidad_fabricada  REAL NOT NULL DEFAULT 1,
    notas               TEXT,
    creado_en           TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ---------- PRESENTACIONES ----------
-- Ej: Tequeños x 6, x 12, x 20
CREATE TABLE IF NOT EXISTS presentaciones (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_fabricado_id   INTEGER NOT NULL REFERENCES productos_fabricados(id) ON DELETE CASCADE,
    nombre                  TEXT NOT NULL,
    cantidad_unidades       REAL NOT NULL
);

-- ---------- CONFIGURACION ----------
CREATE TABLE IF NOT EXISTS configuracion (
    clave   TEXT PRIMARY KEY,
    valor   TEXT NOT NULL
);

-- ---------- MARGENES ----------
CREATE TABLE IF NOT EXISTS margenes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    numero      INTEGER NOT NULL UNIQUE CHECK (numero IN (1, 2, 3)),
    nombre      TEXT NOT NULL,
    porcentaje  REAL NOT NULL
);

-- ---------- INDICES (hacen las búsquedas más rápidas) ----------
CREATE INDEX IF NOT EXISTS idx_productos_nombre      ON productos(nombre);
CREATE INDEX IF NOT EXISTS idx_compras_fecha         ON compras(fecha);
CREATE INDEX IF NOT EXISTS idx_detalle_compra        ON detalle_compras(compra_id);
CREATE INDEX IF NOT EXISTS idx_historial_producto    ON historial_precios(producto_id, fecha);
CREATE INDEX IF NOT EXISTS idx_receta_ingredientes   ON receta_ingredientes(receta_id);

-- =====================================================
-- DATOS INICIALES
-- =====================================================

INSERT OR IGNORE INTO unidades (nombre, abreviatura, tipo, factor_base) VALUES
    ('Gramo',     'g',    'masa',    1),
    ('Kilogramo', 'kg',   'masa',    1000),
    ('Mililitro', 'ml',   'volumen', 1),
    ('Litro',     'l',    'volumen', 1000),
    ('Unidad',    'un',   'conteo',  1),
    ('Docena',    'doc',  'conteo',  12),
    ('Paquete',   'paq',  'empaque', 1),
    ('Caja',      'caja', 'empaque', 1);

INSERT OR IGNORE INTO margenes (numero, nombre, porcentaje) VALUES
    (1, 'Margen 1', 30),
    (2, 'Margen 2', 50),
    (3, 'Margen 3', 70);

INSERT OR IGNORE INTO configuracion (clave, valor) VALUES
    ('nombre_negocio', 'Mi Negocio'),
    ('moneda', '$'),
    ('metodo_precio', 'sobre_costo');
