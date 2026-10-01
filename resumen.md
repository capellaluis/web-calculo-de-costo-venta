# MI NEGOCIO — Documento maestro de contexto para el agente de programación

> Versión 1.0 · Redactado el 2026-10-01 · Idioma de trabajo y de la interfaz: **español**
> Colócalo en la raíz del proyecto (`~/mi_negocio/`) con el nombre que tu agente lea por defecto (por ejemplo `AGENTS.md` o `CLAUDE.md`), o pégalo como primer mensaje.

---

## 0. Léeme primero (resumen)

- **Qué es:** "MI NEGOCIO", una aplicación web para administrar un negocio de alimentos y bebidas artesanales: proveedores, compras, productos, historial de precios, recetas, costos, productos fabricados, márgenes, reportes, exportación a Excel y copias de seguridad. Después se agrega **facturación electrónica de Argentina** y **pedidos de Rappi** (Sección 11).
- **Dónde corre:** en una **Raspberry Pi 3** (Debian 13), como servidor local en la red Wi-Fi. Sin hosting, sin dominio, sin Internet obligatorio.
- **Stack:** Python 3.13 + Flask + SQLite + Jinja2 + HTML/CSS/JavaScript + openpyxl. Sin Docker, sin React, sin Node.js.
- **Quién es el usuario:** **principiante absoluto**. Hay que guiarlo paso a paso, en español sencillo.
- **Cómo se trabaja:** **por fases**. Al terminar cada fase el agente **se detiene**, presenta un informe y una guía para que el usuario vea el resultado, y **espera** que escriba `FUNCIONA` (o que pida cambios). Nunca avanza solo (Sección 1).
- **Estado:** Fases 1 a 5 completas y verificadas. Fase 6 (Productos) con el código creado y conectado; **falta que el usuario confirme la prueba en el navegador**. Fases 7 a 16 pendientes. Fases 17 a 22 (pedidos y facturación) planificadas.
- **Primera acción del agente:** leer este documento completo, revisar el proyecto real (`find`/`ls`), y pedirle al usuario que confirme la prueba de la Fase 6 (checklist en la Sección 7.3).

---

## 1. Reglas de trabajo obligatorias

### 1.1 Protocolo por fases (la regla más importante)

1. **Una fase a la vez.** No empezar la fase siguiente hasta que el usuario escriba **`FUNCIONA`**.
2. Al terminar cada fase, entregar un **Informe de fase** con esta plantilla exacta:

```
## Informe Fase N — <nombre de la fase>
Qué se hizo: (3 a 6 líneas, en lenguaje simple)
Archivos creados: (lista)
Archivos modificados: (lista)
Cómo verlo:
  1. cd ~/mi_negocio && source venv/bin/activate
  2. python app.py
  3. Abrir en el navegador http://<IP-de-la-Raspberry>:5000
  4. Checklist numerado: qué hacer y qué debería verse (con ejemplos concretos)
Verificaciones automáticas realizadas: (compilación, importación, pruebas)
Limitaciones o pendientes de esta fase: (si los hay)
¿Escribes "FUNCIONA" para pasar a la Fase N+1, o quieres cambios?
```

3. **Si el usuario pide cambios** dentro de la fase: aplicarlos, volver a presentar un informe corto y **seguir esperando** la confirmación. Esos cambios no se acumulan para la fase siguiente.
4. **Si aparece un error**, no adivinar. Explicar: qué significa, por qué ocurrió, qué hacer, el comando o código exacto y cómo comprobar que se solucionó. Nunca responder "revisa la configuración".

### 1.2 Trato con el usuario

- Principiante: no asumir conocimientos de Linux, terminal, Python, Flask, SQLite, HTML/CSS/JS, Git ni servidores.
- Cada instrucción dice: **dónde** hacerlo, **qué** abrir, **qué comando** escribir, **qué debería aparecer** y **cómo comprobar** que funcionó.
- **Una instrucción a la vez** cuando se trabaja con el usuario copiando y pegando. Comandos siempre en bloques de código, y después una frase que explique qué hace.
- Si el agente tiene acceso directo a los archivos, edita él mismo y no hace copiar y pegar; aun así, explica brevemente qué hizo y deja la guía de prueba del informe.
- Cuando el usuario deba crear un archivo: `CREAR: ruta/nombre.py` con el contenido **completo**. Cuando deba reemplazarlo: `REEMPLAZAR COMPLETAMENTE EL CONTENIDO DE: ruta/nombre.py`. Nada de fragmentos que dependan de código que no existe.
- **Interfaz 100 % en español.** Cero palabras en inglés visibles (el usuario pidió cambiar "Dashboard" por "Panel principal"). Excepción: nombres propios como "Excel".
- Tono cercano, positivo y claro. Formato de dinero argentino: `$1.234,50`.

### 1.3 Seguridad de los datos del usuario

- **No** dar comandos que puedan borrar la base de datos, eliminar carpetas, formatear o desinstalar cosas importantes **sin advertir antes** con claridad y sin hacer una copia previa.
- Antes de modificar un archivo existente: copia de respaldo (`cp archivo archivo.antes_<motivo>`) o commit de Git (ver 12.1).
- Antes de cambiar el esquema de `negocio.db`: copia automática de la base (ver 9.6) y migración versionada (ver 5.4).
- Comprobaciones tras cada cambio: `python -m py_compile <archivo>`, `python -c "import app"` y, si hay rutas nuevas, una prueba con el cliente de pruebas de Flask. Comprobar que **no haya contenido duplicado** (`wc -l`, `grep -c`).

### 1.4 Honestidad técnica

- Si algo no se sabe o puede haber cambiado (sobre todo **normativa fiscal**), investigar en fuentes oficiales y avisar la fecha de verificación. No inventar.
- Si una decisión afecta al negocio (impuestos, redondeos, criterios contables), **preguntar al usuario** y recomendarle confirmar con su contador.

---

## 2. El usuario y el entorno

| Dato | Valor |
|---|---|
| Nombre | Luis |
| País | Argentina (pesos argentinos, formato `$1.234,50`) |
| Nivel técnico | Principiante absoluto |
| Equipo servidor | Raspberry Pi 3 (1 GB de RAM aprox.) |
| Sistema operativo | Debian GNU/Linux 13 "trixie" (13.5) |
| Python | 3.13.5 (`/usr/bin/python3`) |
| pip | 25.1.1, instalado con `sudo apt install python3-pip python3-venv` |
| Almacenamiento | Tarjeta de ~15 GB, unos 5,8 GB libres (al 2026-09-29) |
| Usuario del sistema | `luis`, proyecto en `/home/luis/mi_negocio` |
| IP de la Raspberry | `192.168.1.100` (puede cambiar si se reinicia el router; consultar con `hostname -I`) |
| Cómo trabaja | Desde una computadora con **Windows Terminal** conectada por SSH a la Raspberry; shell **zsh** |
| Cómo prueba | Navegador de la computadora en `http://192.168.1.100:5000`, y también el teléfono en el mismo Wi-Fi |
| Servidor actual | Servidor de desarrollo de Flask: `python app.py` (puerto 5000, `debug=True`, `host=0.0.0.0`) |

Para volver a trabajar en una terminal nueva:

```
cd ~/mi_negocio
source venv/bin/activate
```

Debe aparecer `(venv)` al inicio de la línea. El servidor se apaga con **Ctrl + C**. Mientras corre, esa terminal queda ocupada (el usuario ya se confundió con esto una vez).

---

## 3. Visión y alcance funcional

### 3.1 Objetivo general

Sistema para administrar el negocio. Cadena de valor que debe quedar funcionando:

```
PROVEEDORES + COMPRAS → PRODUCTOS → PRECIOS HISTÓRICOS → RECETAS → COSTOS
→ PRODUCTOS FABRICADOS → MÁRGENES → PRECIOS DE VENTA → REPORTES → EXCEL / COPIA DE SEGURIDAD
```

La arquitectura debe permitir agregar después: inventario, ventas, clientes, ganancias, integración con Rappi, alertas y estadísticas. **Pedidos y facturación** (Sección 11) son la primera ampliación pedida.

### 3.2 Módulos y requisitos funcionales

| Módulo | Requisitos |
|---|---|
| **Proveedores** | Crear, editar, ver, buscar, eliminar, historial de compras. Datos: nombre, razón social, CUIT/RUT, teléfono, WhatsApp, email, dirección, persona de contacto, notas, fecha de creación. |
| **Productos** (materias primas) | Nombre, categoría, unidad de compra, unidad de uso, precio actual, proveedor principal, SKU opcional, notas. Unidades: unidad, kg, g, litro, ml, paquete, caja, docena. |
| **Conversión de unidades** | Comprar 1 kg y usar 300 g. 1 kg = 1000 g, 1 litro = 1000 ml. Automática. |
| **Compras** | "Nueva compra": proveedor, fecha, producto, cantidad, unidad, precio total, precio por unidad (calculado), nº de factura/remito, observaciones. Ej.: 25 kg por $30.000 → $1.200/kg. |
| **Historial de precios** | Nunca se pierde un precio anterior. Consultar evolución. Detectar aumentos (ej.: $1.350 → $1.500, aumento $150) y usarlo para recalcular costos de recetas. |
| **Recetas** | Ingredientes con cantidad y unidad, precio actual tomado solo, costo total, **rendimiento** (ej.: 10 vasos) y costo por unidad. |
| **Márgenes** | Tres márgenes **configurables desde la pantalla** (por defecto 30, 50, 70), nunca escritos en el código. Dos métodos: *sumar porcentaje al costo* y *margen real sobre el precio de venta*; la interfaz explica la diferencia. |
| **Productos fabricados** | Lote con receta, cantidad fabricada, costo por unidad, **presentaciones** (x6, x12, x20) con costo y los tres precios de venta. |
| **Costos** | Pantalla muy visual: costo por unidad y tres tarjetas de margen (🟢 margen 1, 🔵 margen 2, 🟣 margen 3). |
| **Reportes** | Compras, proveedores, productos, costos, historial de precios, productos fabricados. Filtros: fecha, proveedor, producto, categoría. |
| **Excel** | Botón "Exportar a Excel" con `openpyxl`: `Mi_Negocio_AAAA-MM-DD.xlsx`. Hojas: Proveedores, Productos, Compras, Detalle Compras, Historial Precios, Recetas, Ingredientes, Productos Fabricados, Costos y Precios. Encabezados, formato, columnas ajustadas, fechas y moneda con formato correcto. |
| **Copias de seguridad** | Configuración → Copias de seguridad → "Crear copia" de la base SQLite, y explicación clara de cómo **restaurar**. |
| **Panel principal** | Tarjetas: proveedores, compras del mes, productos, recetas, productos fabricados, costo total. Gráficos: compras por mes, evolución de precios, productos cuyo costo aumentó, productos más comprados, gastos por categoría. |

### 3.3 Diseño visual (requisito explícito del usuario)

Moderno, limpio, profesional, rápido, responsive. Tarjetas con bordes redondeados y sombras suaves, iconos consistentes, animaciones **sutiles y livianas** (Raspberry Pi 3: sin videos, sin fondos animados, sin dependencias pesadas). Fondo claro, colores fuertes solo en botones, tarjetas, iconos y estados. **Un color por sección** (ver 4.5). Iconos y gráficos funcionan **sin Internet** (archivos locales).

---

## 4. Arquitectura

### 4.1 Decisiones

- Aplicación monolítica **Flask** con **Blueprints** (uno por módulo), plantillas **Jinja2** con una plantilla base y CSS propio. `sqlite3` de la biblioteca estándar, **sin ORM** (simple y liviano).
- Dependencias instaladas en el entorno virtual `venv/`: **Flask** y **openpyxl** (verificar versiones con `pip freeze`; el archivo `requirements.txt` **todavía no existe**, ver 12).
- Frontend: HTML + CSS + JavaScript simple. **Bootstrap Icons** (CSS + fuentes) y **Chart.js 4.4.7** descargados a `static/` (funcionan sin Internet).
- Patrón de cada módulo: ruta (Blueprint) → consulta SQL con parámetros → `render_template`. Formularios con **POST + redirect** y avisos por parámetro `?aviso=clave`.
- Lógica de negocio compartida (conversiones, costos, precios) debe vivir en `services/` (hoy está vacío; ver 12).

### 4.2 Estructura real del proyecto (2026-10-01)

```
mi_negocio/
├── app.py                      # crea la app, registra Blueprints, filtro "moneda"
├── venv/                       # entorno virtual (no se versiona)
├── database/
│   ├── __init__.py
│   ├── db.py                   # obtener_conexion()
│   ├── init_db.py              # crea negocio.db leyendo schema.sql (idempotente)
│   ├── schema.sql              # esquema + datos iniciales  ← FUENTE DE VERDAD
│   └── negocio.db              # base SQLite (≈108 KB al crear)
├── routes/
│   ├── __init__.py
│   ├── dashboard.py            # Panel principal  (url "/")
│   ├── proveedores.py          # /proveedores
│   └── productos.py            # /productos
├── services/__init__.py        # vacío (aquí irá la lógica de negocio)
├── models/__init__.py          # vacío
├── templates/
│   ├── base.html               # menú lateral + botón de modo oscuro + bloques
│   ├── dashboard.html
│   ├── proveedores_lista.html  proveedores_form.html  proveedores_ver.html
│   └── productos_lista.html    productos_form.html    productos_ver.html
├── static/
│   ├── css/estilo.css          # diseño completo + modo oscuro (≈392 líneas)
│   ├── js/chart.umd.js         # Chart.js 4.4.7 local
│   ├── js/tema.js              # alterna modo claro/oscuro (localStorage)
│   └── icons/bootstrap-icons.css + fonts/bootstrap-icons.woff2, .woff
├── exports/                    # vacío (Excel)
└── backups/                    # vacío (copias de la base)
```

Archivos de respaldo que quedaron por el método de trabajo (se pueden limpiar **con permiso del usuario**): `estilo.css.respaldo`, `estilo.css.antes_oscuro`, `estilo.css.antes_boton_arriba`, `base.html.respaldo`, `base.html.antes_panel`, `base.html.antes_oscuro`, `base.html.antes_boton_arriba`, `base.html.antes_proveedores`, `base.html.antes_productos`, `dashboard.html.antes_panel`, `dashboard.html.antes_oscuro`, `dashboard.py.respaldo`, `dashboard.py.parte1`, `proveedores.py.respaldo`, `app.py.antes_proveedores`, `app.py.antes_productos`. Conviene moverlos a `_respaldos/` o reemplazarlos por Git (12.1).

### 4.3 Código de referencia (estado actual)

`database/db.py`

```python
import sqlite3
from pathlib import Path

RUTA_DB = Path(__file__).resolve().parent / "negocio.db"


def obtener_conexion():
    """Abre una conexión a la base de datos. Las filas se leen por nombre de columna."""
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion
```

`app.py`

```python
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
    # host 0.0.0.0 permite entrar desde otros dispositivos de la red Wi-Fi
    app.run(host="0.0.0.0", port=5000, debug=True)
```

Patrón de un módulo (extracto de `routes/proveedores.py`):

```python
bp = Blueprint("proveedores", __name__, url_prefix="/proveedores")

AVISOS = {"creado": "Proveedor creado correctamente.", ...}

@bp.route("/")
def lista():
    aviso = AVISOS.get(request.args.get("aviso", ""))
    con = obtener_conexion()
    try:
        filas = con.execute("SELECT * FROM proveedores ORDER BY nombre").fetchall()
    finally:
        con.close()
    return render_template("proveedores_lista.html", seccion="proveedores",
                           proveedores=filas, aviso=aviso)
```

Reglas del patrón: siempre `try/finally` para cerrar la conexión; **consultas parametrizadas** (`?`), nunca concatenar datos del usuario en el SQL; `redirect(url_for(..., aviso="creado"))` tras cada POST; **no se elimina** un registro que tenga datos relacionados (proveedor con compras; producto con compras o recetas) y se muestra un aviso en rojo.

### 4.4 Plantillas

- Todas extienden `base.html` con `{% extends "base.html" %}` y los bloques `titulo`, `contenido` y (opcional) `scripts`.
- Cada ruta pasa `seccion="..."` (`dashboard`, `proveedores`, `compras`, `productos`, `recetas`, `costos`, `reportes`, `excel`, `config`); `base.html` lo usa para resaltar el menú y para la clase de color `c-<seccion>` del contenido.
- Los enlaces del menú de **Compras, Recetas, Costos, Reportes, Excel y Configuración** apuntan todavía a `#`. Al construir cada módulo hay que cambiar el `href` por `{{ url_for('<bp>.lista') }}` (se hizo con `sed` para Proveedores y Productos).
- Filtro de plantilla `|moneda` definido en `app.py`.
- Los avisos y alertas usan `style` en línea con variables CSS (`var(--c-suave)`, `var(--c)`).

### 4.5 Sistema visual (CSS)

Variables en `:root` (`--fondo`, `--superficie`, `--texto`, `--texto-suave`, `--borde`, `--radio`, `--sombra`, `--c`, `--c-suave`). La clase `c-<seccion>` cambia `--c` y `--c-suave` (color de la sección):

| Sección | Clase | Color |
|---|---|---|
| Panel principal | `c-dashboard` | Índigo `#4f46e5` |
| Proveedores | `c-proveedores` | Azul `#2563eb` |
| Compras | `c-compras` | Verde `#16a34a` |
| Productos | `c-productos` | Naranja `#ea580c` |
| Recetas | `c-recetas` | Violeta `#7c3aed` |
| Costos | `c-costos` | Turquesa `#0d9488` |
| Reportes | `c-reportes` | Celeste `#0284c7` |
| Configuración | `c-config` | Gris azulado `#475569` |
| Alertas/errores | `c-alerta` | Rojo `#dc2626` |

Componentes reutilizables: `.menu`, `.nav-item`, `.contenido`, `.encabezado`, `.grid-stats`, `.stat-card`, `.stat-icono`, `.tarjeta`, `.grid-graficos`, `.grafico-caja`, `.estado-vacio`, `.btn`, `.btn-suave`, `.btn-borde`, `.tabla-caja`, `.tabla`, `.badge`, `.campo`, `.btn-tema`.

**Modo oscuro/claro:** botón en la esquina superior derecha (`.btn-tema`, posición absoluta dentro de `.contenido`). `static/js/tema.js` se carga en `<head>`, aplica el modo guardado en `localStorage['tema']` (valores `oscuro`/`claro`) poniendo `data-tema="oscuro"` en `<html>`. En el panel principal, al cambiar de modo la página se recarga para que Chart.js tome los colores nuevos (`Chart.defaults.color` y `borderColor` leen `--texto-suave` y `--borde`). Cualquier componente nuevo debe usar variables CSS (no colores fijos) para verse bien en ambos modos.

### 4.6 Panel principal (estado)

`routes/dashboard.py` calcula: cantidad de proveedores, compras del mes (`SUM(compras.total)` del mes actual), productos, recetas, productos fabricados y costo total (hoy `SUM(compras.total)`, **provisional**), más tres gráficos: compras por mes (últimos 6), productos más comprados (top 5) y gastos por categoría. Con base vacía muestran "Aún no hay…". **Faltan** los gráficos *evolución de precios* y *productos cuyo costo aumentó* (Fase 8) y definir bien "Costo total" cuando existan recetas (Fase 10).

---

## 5. Modelo de datos (SQLite)

### 5.1 Tablas (13) y relaciones

Fuente de verdad: `database/schema.sql`. Todas las fechas son texto ISO `AAAA-MM-DD` (o `datetime('now','localtime')` para `creado_en`).

| Tabla | Columnas clave | Relaciones |
|---|---|---|
| `unidades` | `nombre`, `abreviatura`, `tipo` (`masa`/`volumen`/`conteo`/`empaque`), `factor_base` | — |
| `categorias` | `nombre` (único) | — |
| `proveedores` | nombre, razon_social, cuit_rut, telefono, whatsapp, email, direccion, persona_contacto, notas | — |
| `productos` | nombre, `categoria_id`, `unidad_compra_id`, `unidad_uso_id`, `precio_actual` (por unidad de compra), `proveedor_principal_id`, sku, notas | → categorias, unidades×2, proveedores |
| `compras` | `proveedor_id`, fecha, numero_documento, observaciones, total | → proveedores |
| `detalle_compras` | `compra_id` (CASCADE), `producto_id`, cantidad, `unidad_id`, precio_total, precio_unitario | → compras, productos, unidades |
| `historial_precios` | `producto_id`, fecha, precio_unitario, `unidad_id`, `detalle_compra_id` (SET NULL) | → productos, unidades, detalle_compras |
| `recetas` | nombre, descripcion, rendimiento_cantidad, rendimiento_unidad (texto), notas | — |
| `receta_ingredientes` | `receta_id` (CASCADE), `producto_id`, cantidad, `unidad_id` | → recetas, productos, unidades |
| `productos_fabricados` | nombre, `receta_id`, cantidad_fabricada, notas | → recetas |
| `presentaciones` | `producto_fabricado_id` (CASCADE), nombre, cantidad_unidades | → productos_fabricados |
| `configuracion` | `clave` (PK), `valor` | — |
| `margenes` | `numero` (1,2,3), nombre, `porcentaje` | — |

Índices: `productos(nombre)`, `compras(fecha)`, `detalle_compras(compra_id)`, `historial_precios(producto_id, fecha)`, `receta_ingredientes(receta_id)`. `PRAGMA foreign_keys = ON` se activa en cada conexión.

### 5.2 Datos iniciales (ya cargados)

- **Unidades:** Gramo `g` (masa, 1), Kilogramo `kg` (masa, 1000), Mililitro `ml` (volumen, 1), Litro `l` (volumen, 1000), Unidad `un` (conteo, 1), Docena `doc` (conteo, 12), Paquete `paq` (empaque, 1), Caja `caja` (empaque, 1).
- **Márgenes:** (1, "Margen 1", 30), (2, "Margen 2", 50), (3, "Margen 3", 70).
- **Configuración:** `nombre_negocio="Mi Negocio"`, `moneda="$"`, `metodo_precio="sobre_costo"`.

### 5.3 Semántica importante

- `productos.precio_actual` = precio por **una unidad de compra** (ej.: $/kg).
- `historial_precios.precio_unitario` = precio por unidad de `unidad_id` en esa fecha. **Nunca se borra** (solo se borra al eliminar el producto, que a su vez solo es posible si no tiene compras ni recetas).
- Paquete y caja **no se convierten automáticamente** (su contenido depende del producto). Hoy el sistema solo permite usarlos con la misma unidad. Mejora prevista: columnas de equivalencia por producto (5.4).

### 5.4 Cambios de esquema: migraciones versionadas

`init_db.py` crea la base desde cero y es idempotente (`IF NOT EXISTS`, `INSERT OR IGNORE`), pero **no modifica tablas existentes**. Para cambios futuros usar migraciones numeradas con `PRAGMA user_version`:

```python
# database/migrar.py
import sqlite3
from pathlib import Path

CARPETA = Path(__file__).resolve().parent / "migraciones"   # 001_xxx.sql, 002_xxx.sql ...


def migrar(ruta_db):
    con = sqlite3.connect(ruta_db)
    try:
        actual = con.execute("PRAGMA user_version").fetchone()[0]
        for archivo in sorted(CARPETA.glob("[0-9][0-9][0-9]_*.sql")):
            version = int(archivo.name[:3])
            if version > actual:
                con.executescript(archivo.read_text(encoding="utf-8"))
                con.execute("PRAGMA user_version = %d" % version)
                con.commit()
    finally:
        con.close()
```

Ejemplo de migración prevista (`001_equivalencia_productos.sql`): `ALTER TABLE productos ADD COLUMN equivalencia_cantidad REAL; ALTER TABLE productos ADD COLUMN equivalencia_unidad_id INTEGER REFERENCES unidades(id);` (permite "1 caja = 12 unidades"). **Hacer copia de la base antes de migrar.**

### 5.5 Dinero y redondeo

Hoy los importes de costos y compras son `REAL`. Para costos está aceptable **si se redondea al mostrar**. Para **comprobantes fiscales y cualquier dato contable nuevo** (Sección 11) usar **enteros en centavos** o `decimal.Decimal`, **nunca `float`**, y guardar los totales tal como se informan a ARCA.

---

## 6. Reglas de negocio, fórmulas y casos de prueba

### 6.1 Conversión de unidades

```python
def convertir(cantidad, desde, hacia):
    """desde y hacia son filas de 'unidades'."""
    if desde["tipo"] != hacia["tipo"]:
        raise ValueError("Unidades incompatibles")
    if desde["tipo"] == "empaque" and desde["id"] != hacia["id"]:
        raise ValueError("Paquete y caja solo se convierten a sí mismos")
    return cantidad * desde["factor_base"] / hacia["factor_base"]
```

Pruebas: `convertir(1, kg, g) == 1000`; `convertir(300, g, kg) == 0.3`; `convertir(1, docena, un) == 12`; `convertir(1, l, ml) == 1000`.

### 6.2 Compra → precio unitario → historial

```python
def precio_unitario(precio_total, cantidad):
    return precio_total / cantidad          # 30000 / 25 = 1200 por kg
```

Al registrar cada línea de compra, en **una sola transacción**: (1) insertar `compras`/`detalle_compras`; (2) convertir el precio a la **unidad de compra del producto** si la línea usa otra unidad: `precio_en_unidad_compra = precio_total / convertir(cantidad, unidad_linea, unidad_compra_producto)`; (3) actualizar `productos.precio_actual`; (4) insertar en `historial_precios`; (5) recalcular `compras.total`. Si algo falla: `rollback`.

Detección de aumento: comparar con el registro anterior más reciente del historial.

```
AZÚCAR   anterior $1.350  →  actual $1.500   aumento $150 (+11,1 %)
```

### 6.3 Costo de receta

```python
costo_linea = convertir(cantidad_ingrediente, unidad_ingrediente, unidad_compra_producto) * producto["precio_actual"]
costo_total = sum(costo_lineas)
costo_por_unidad = costo_total / rendimiento_cantidad
```

Prueba: 300 g de azúcar con precio $1.350/kg → `convertir(300, g, kg) = 0,3` → `0,3 × 1350 = $405`.
Ejemplo del usuario: costo total $2.940 con rendimiento 10 vasos → **$294 por vaso**.

### 6.4 Márgenes (dos métodos que la interfaz debe explicar)

```python
def precio_sobre_costo(costo, pct):          # A) sumar porcentaje al costo
    return costo * (1 + pct / 100)

def precio_margen_real(costo, pct):          # B) margen real sobre el precio de venta
    if pct >= 100:
        raise ValueError("El margen real debe ser menor a 100 %")
    return costo / (1 - pct / 100)
```

Casos de prueba:
- A) costo $100 con +30 % → **$130**. B) costo $100 con margen real 30 % → **$142,86**.
- Costo $294: método A → 30 % = **$382,2**; 50 % = **$441**; 70 % = **$499,8**. Método B con 30 % = **$420**.
- El método activo está en `configuracion.metodo_precio` (`sobre_costo` | `margen_real`). Agregar la clave `redondeo` (por ejemplo `entero`) para mostrar $382 / $441 / $500 como en el ejemplo del usuario.
- Los tres porcentajes se leen **siempre** de la tabla `margenes`; hay una pantalla Configuración → Márgenes para cambiarlos (30/50/70 → 35/55/80 sin tocar código).

### 6.5 Productos fabricados y presentaciones

Ejemplo del usuario: Tequeños, costo del lote **$4.860**, lote de **20 unidades** → **$243 por unidad**. Presentación de 6 unidades → **$1.458**; se muestran los precios con margen 1, 2 y 3 (🟢 🔵 🟣). Cada producto fabricado admite varias presentaciones (6, 12, 20) con costo y precios calculados automáticamente.

---

## 7. Estado por fases

### 7.1 Tabla de fases

| Fase | Nombre | Estado |
|---|---|---|
| 1 | Preparar la Raspberry Pi | ✅ Completa |
| 2 | Crear el proyecto | ✅ Completa |
| 3 | Crear la base de datos | ✅ Completa |
| 4 | Diseño base y panel principal | ✅ Completa (incluye modo oscuro y botón superior derecho) |
| 5 | Proveedores | ✅ Completa y probada por el usuario |
| 6 | Productos | 🟡 Código creado y conectado; **prueba en navegador pendiente de confirmación del usuario** |
| 7 | Compras | ⏳ Pendiente |
| 8 | Historial de precios | ⏳ Pendiente (parte ya existe: ver 7.4) |
| 9 | Recetas | ⏳ Pendiente |
| 10 | Cálculo de costos | ⏳ Pendiente |
| 11 | Márgenes | ⏳ Pendiente |
| 12 | Productos fabricados | ⏳ Pendiente |
| 13 | Exportación a Excel | ⏳ Pendiente |
| 14 | Reportes | ⏳ Pendiente |
| 15 | Copias de seguridad | ⏳ Pendiente |
| 16 | Pruebas y optimización | ⏳ Pendiente |
| 17 | Pedidos (Rappi) | 🗓️ Planificada (Sección 11) |
| 18 | Configuración fiscal | 🗓️ Planificada |
| 19 | Conexión con ARCA en homologación | 🗓️ Planificada |
| 20 | Facturación de pedidos | 🗓️ Planificada |
| 21 | Contabilidad y reportes fiscales | 🗓️ Planificada |
| 22 | Pase a producción | 🗓️ Planificada |

### 7.2 Qué quedó hecho en las fases completas

- **Fase 1:** `cat /etc/os-release` → Debian 13 trixie. Python 3.13.5. `pip` no estaba instalado: se instaló con apt junto con `python3-venv`. Espacio libre ≈ 5,8 GB. IP local 192.168.1.100.
- **Fase 2:** carpetas del proyecto, `venv` creado, `pip install flask openpyxl`, `app.py` de prueba, servidor probado desde la computadora y el teléfono.
- **Fase 3:** `schema.sql` (173 líneas), `init_db.py`, `negocio.db` con 13 tablas, 3 márgenes y 8 unidades. Verificado con el script (lista las tablas y datos iniciales).
- **Fase 4:** iconos y Chart.js locales, `estilo.css`, `base.html`, `dashboard.py` + `dashboard.html`, `db.py`, `app.py`. Palabra "Dashboard" cambiada a **"Panel principal"**. Modo oscuro/claro con botón arriba a la derecha.
- **Fase 5:** lista con buscador (nombre, razón social, CUIT/RUT, contacto), crear, ver ficha con historial de compras, editar, eliminar (bloqueado si hay compras). Verificada por el usuario ("FUNCIONA").

### 7.3 Fase 6 (Productos): qué hay y qué debe probar el usuario

Hecho: `routes/productos.py` (255 líneas: lista con búsqueda y filtro por categoría, nuevo, ver, editar, eliminar), tres plantillas, registro en `app.py` y enlace del menú. Reglas: nombre obligatorio; precio acepta `1200` o `1200,50`; unidad de compra y de uso **compatibles** (kg↔g, l↔ml, un↔doc; paquete/caja solo consigo mismos); la categoría se escribe y se crea sola si no existe; al crear o cambiar el precio se anota en `historial_precios`; no se elimina un producto con compras o recetas.

**Checklist de prueba pendiente** (pedir al usuario que lo ejecute y confirme):

1. Menú **Productos** → lista vacía con "Aún no hay productos".
2. **Nuevo producto**: Azúcar, categoría Insumos, compra en Kilogramo, uso en Gramo, precio 1200 → vuelve a la lista con aviso verde y `$1.200 / kg`.
3. Ficha (ojo): el historial muestra el precio.
4. Editar (lápiz): precio 1350 → el historial muestra **los dos precios**.
5. Combinación inválida (Kilogramo → Mililitro): aviso de que no son compatibles y no guarda.
6. Crear otro producto de prueba y eliminarlo (pregunta de confirmación).
7. Panel principal: la tarjeta Productos muestra la cantidad correcta.

### 7.4 Piezas de fases futuras que ya existen

- Historial de precios: se **escribe** al crear/editar productos y se **muestra** (últimos 20) en la ficha del producto. La Fase 8 agrega la pantalla propia, los gráficos, las alertas de aumento y el vínculo con las compras.

---

## 8. Registro de errores resueltos y lecciones aprendidas

| Situación | Causa | Solución aplicada / regla |
|---|---|---|
| `No module named pip` | Instalación nueva de Debian 13 | `sudo apt update && sudo apt install -y python3-pip python3-venv`. Debian 13 exige entorno virtual (`python3 -m venv venv`). |
| El usuario "no podía escribir" en la terminal | El servidor (`python app.py`) deja la terminal **ocupada** | Apagar con **Ctrl + C**; para otras tareas abrir otra terminal. Decirlo cada vez. |
| `127.0.0.1:5000` no abre | `127.0.0.1` es "este mismo equipo"; el usuario está en otra computadora | Usar la IP de la Raspberry (`http://192.168.1.100:5000`). |
| Bloques largos pegados en Windows Terminal se **cortan** (`heredoc>`) o se **duplican** | Pegado grande de texto; aviso "más de 5 KiB"; el cierre `EOF` no llega | Bloques de **≤ ~60 líneas**; pegar **una sola vez**; verificar con `wc -l`, `grep -c` y marcas `# FIN`; si se duplica: `cp archivo archivo.respaldo` y luego `sed -n '1,/marca/p' archivo.respaldo > archivo` o `head -n N`. Para partes cortadas: Ctrl + C y volver a crear. |
| `zsh: event not found: doctype` | En zsh, `!` dentro de comillas dobles es especial | Usar comillas **simples** en `grep '<!doctype' ...`. |
| El usuario pegó la **respuesta de ejemplo** como si fuera un comando (`command not found`, `cursh>`) | Texto esperado confundido con instrucciones | Presentar "Debe salir:" claramente separado; decir "pega solo el comando, nunca la respuesta de ejemplo". |
| Archivos descargados vacíos (fuentes, `chart.umd.js`) | Se apagó la Raspberry durante la descarga | Reintentar con `curl -fL -o ruta URL` y verificar con `ls -lh`. |
| `productos.py` inexistente al comprobar | El bloque anterior nunca se pegó | Comprobar siempre existencia (`ls`) antes de seguir y recrear el archivo. |
| Se duplicó dos veces el contenido de `estilo.css`, `base.html`, `dashboard.py`, `proveedores.py` | Pegado dos veces o reintento sobre una terminal en `heredoc>` | Método de recuperación anterior. Siempre respaldo antes de reparar. |
| El usuario apagó la Raspberry por error | Desconexión brusca | Los archivos se conservan; rehacer descargas incompletas. Para apagar: `sudo shutdown -h now` y esperar a que se apaguen las luces. |

**Hábitos que funcionaron:** marcas de fin (`# FIN archivo`) y conteos de líneas; respaldos `.antes_<motivo>`; pruebas de sintaxis (`py_compile`) e importación; edición mínima con `sed -i` para enlaces y registros; verificar el **resultado completo** que pega el usuario (a veces falta una de las salidas: pedirla).

---

## 9. Seguridad y buenas prácticas

### 9.1 Estado actual y riesgos conocidos

- La app **no tiene inicio de sesión** ni protección CSRF y corre con `debug=True` y `host=0.0.0.0`. El depurador de Werkzeug **permite ejecutar código** a quien lo alcance en la red: aceptable solo en una red doméstica de confianza y **temporalmente**. **Antes de usar datos reales o de exponerla a más personas hay que cerrar los puntos 9.2 a 9.5.**
- **Nunca** exponer la Raspberry a Internet (sin abrir puertos del router, sin túneles) hasta tener: inicio de sesión, CSRF, HTTPS, servidor de producción y revisión de seguridad. El usuario pidió explícitamente no hacerlo por ahora.

### 9.2 Secretos y configuración

- **Ningún secreto en el código.** Usar variables de entorno desde un archivo `.env` (permisos `600`, incluido en `.gitignore`), cargado por `python-dotenv` o por `EnvironmentFile` de systemd. Explicar al usuario qué es una variable de entorno.
- Mínimo: `SECRET_KEY` (aleatoria, generada con `python -c "import secrets; print(secrets.token_hex(32))"`), `APP_ENTORNO` (`desarrollo`/`produccion`) y, para facturación, rutas a certificado y clave (Sección 11).

```python
import os
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
```

### 9.3 Acceso

- Una sola cuenta administradora al principio, con contraseña guardada como hash (`werkzeug.security.generate_password_hash` / `check_password_hash`), sesión de Flask y limitación de intentos. El usuario crea su contraseña; **nunca** escribirla en el código ni en este documento.
- Proteger con inicio de sesión todas las rutas (decorador `login_requerido` o `before_request`).

### 9.4 Formularios y datos

- **CSRF:** token en todos los formularios POST (Flask-WTF `CSRFProtect` o un token propio). Hoy los POST (incluido eliminar) **no** lo tienen.
- Jinja2 escapa el HTML por defecto (no usar `|safe` con datos del usuario). SQL siempre parametrizado (ya se hace). Validar y limitar el tamaño de todo dato recibido.
- Eliminar siempre con POST (ya se hace) y confirmación.

### 9.5 Servidor de producción local

- Dejar de usar el servidor de desarrollo: usar `waitress` (Python puro, liviano) con `debug=False`, y un servicio **systemd** para arrancar solo al encender la Raspberry.

```
[Unit]
Description=Mi Negocio
After=network.target

[Service]
User=luis
WorkingDirectory=/home/luis/mi_negocio
EnvironmentFile=/home/luis/mi_negocio/.env
ExecStart=/home/luis/mi_negocio/venv/bin/waitress-serve --listen=0.0.0.0:5000 app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

- Limitar el puerto a la red local con `ufw` (permitir solo la subred del Wi-Fi y SSH). SSH con clave en vez de contraseña cuando el usuario esté listo.

### 9.6 Copias de seguridad y datos

- Copiar la base con la **API de copia de SQLite** (segura con el servidor encendido), no con `cp`:

```python
import sqlite3
from datetime import datetime
from pathlib import Path

def crear_copia(ruta_db, carpeta_backups):
    destino = Path(carpeta_backups) / ("negocio_%s.db" % datetime.now().strftime("%Y-%m-%d_%H%M%S"))
    origen = sqlite3.connect(ruta_db)
    copia = sqlite3.connect(destino)
    with copia:
        origen.backup(copia)
    copia.close(); origen.close()
    return destino
```

- **Restaurar:** apagar el servidor → guardar la base actual como `negocio.db.antes_restaurar` → copiar la copia elegida sobre `database/negocio.db` → encender el servidor → comprobar. Redactar estas instrucciones en la pantalla de Copias de seguridad.
- Recomendar al usuario guardar copias **fuera de la Raspberry** (computadora o nube): la tarjeta SD puede fallar. Permisos `600` para `negocio.db`.
- Activar `PRAGMA journal_mode = WAL` y `PRAGMA busy_timeout` cuando haya varios usuarios simultáneos.
- Los datos de clientes (Sección 11) son **datos personales**: guardar solo lo necesario (Ley 25.326 de Protección de Datos Personales) y no registrarlos en logs.

---

## 10. Hoja de ruta: fases pendientes 7 a 16

Cada fase termina con el **Informe de fase** (1.1). Criterios de aceptación = lo que el usuario debe poder ver y probar.

### Fase 7 — Compras
- **Hacer:** módulo `routes/compras.py` + plantillas: lista, **Nueva compra** (proveedor, fecha, número de factura/remito, observaciones, **varias líneas** de producto con cantidad, unidad y precio total; precio unitario calculado en pantalla con JavaScript simple), ver detalle, eliminar con reglas claras. Lógica en `services/compras.py` (6.2) en una transacción. Activar el enlace del menú. Migración para equivalencias de paquete/caja si hace falta (5.4).
- **Aceptación:** Distribuidora Sur, Azúcar, 25 kg, $30.000 → muestra $1.200/kg; `precio_actual` del producto cambia; aparece una fila en `historial_precios`; la compra aparece en la ficha del proveedor y en el Panel principal ("Compras del mes", gráficos). Una segunda compra a $1.350/kg y otra a $1.500/kg guardan los tres precios.

### Fase 8 — Historial de precios
- **Hacer:** pantalla de historial por producto con gráfico de línea (Chart.js) y filtros; **alertas de aumento** (⚠ precio anterior, actual, diferencia y porcentaje); lista de "productos cuyo costo aumentó" en el Panel principal; gráfico "evolución de precios".
- **Aceptación:** con los tres precios de azúcar (1.200 → 1.350 → 1.500) aparece "⚠ AZÚCAR: anterior $1.350, actual $1.500, aumento $150".

### Fase 9 — Recetas
- **Hacer:** CRUD de recetas con ingredientes dinámicos (agregar/quitar filas), rendimiento (cantidad + unidad), costo por ingrediente con la conversión de 6.1/6.3, costo total y por unidad, y recalculo automático al cambiar precios.
- **Aceptación:** receta Chicha (maíz 500 g, azúcar 300 g, leche 1 l, canela 10 g, rinde 10 vasos) calcula costo total y por vaso; al subir el precio del azúcar el costo sube solo.

### Fase 10 — Cálculo de costos
- **Hacer:** pantalla **Costos** muy visual (tarjetas por receta/producto con costo por unidad), definir "Costo total" del Panel principal, resumen de ingredientes que más pesan.
- **Aceptación:** costo por vaso de Chicha visible y coherente con la Fase 9.

### Fase 11 — Márgenes
- **Hacer:** Configuración → Márgenes (editar los tres porcentajes y el método), explicación visual de los dos métodos (6.4), tarjetas 🟢🔵🟣 en Costos con los tres precios, regla de redondeo configurable.
- **Aceptación:** con costo $294 y márgenes 30/50/70: $382 / $441 / $500 (método sobre costo); cambiar a 35/55/80 recalcula sin tocar código; método "margen real" da $420 para el 30 %.

### Fase 12 — Productos fabricados
- **Hacer:** CRUD de productos fabricados (receta, cantidad fabricada), costo por lote y por unidad, **presentaciones** (x6, x12, x20) con costo y los tres precios.
- **Aceptación:** Tequeños: lote $4.860, 20 unidades → $243 c/u; presentación x6 → $1.458 y sus tres precios.

### Fase 13 — Exportar a Excel
- **Hacer:** botón "📊 Exportar a Excel" con `openpyxl`, archivo `exports/Mi_Negocio_AAAA-MM-DD.xlsx` y descarga desde el navegador. Hojas: Proveedores, Productos, Compras, Detalle Compras, Historial Precios, Recetas, Ingredientes, Productos Fabricados, Costos y Precios. Encabezados en negrita y con color, columnas ajustadas, fechas como fechas y dinero con formato de moneda, filtros y primera fila inmovilizada.
- **Aceptación:** el usuario abre el archivo en Excel y ve todas las hojas bien formateadas.

### Fase 14 — Reportes
- **Hacer:** módulo Reportes (compras, proveedores, productos, costos, historial de precios, productos fabricados) con filtros por fecha, proveedor, producto y categoría; exportación del reporte filtrado.
- **Aceptación:** filtrar compras del mes por proveedor devuelve el total esperado.

### Fase 15 — Copias de seguridad
- **Hacer:** Configuración → Copias de seguridad: crear copia (9.6), listar copias con fecha y tamaño, descargar, instrucciones de **restauración** paso a paso y un botón/explicación de restauración segura; límite de copias antiguas (con aviso).
- **Aceptación:** crear una copia, abrirla, restaurarla en una prueba y comprobar que los datos vuelven.

### Fase 16 — Pruebas y optimización
- **Hacer:** `requirements.txt` y `README.md`; pruebas automáticas básicas (`pytest` con el cliente de Flask y una base temporal); cerrar los puntos de seguridad 9.2–9.5 (login, CSRF, `SECRET_KEY`, `waitress`, `systemd`, `debug=False`); revisar consultas lentas (índices), tamaño de páginas y rendimiento en la Pi 3; limpiar respaldos antiguos con permiso.
- **Aceptación:** la app arranca sola al encender la Raspberry, pide contraseña, soporta el uso diario y los tiempos de carga son aceptables.

---

## 11. Facturación de Argentina y pedidos de Rappi (Fases 17 a 22)

> **Importante para el agente:** esta sección resume lo verificado el **2026-10-01** en fuentes secundarias (contables y de software de facturación) y debe **re-verificarse en el sitio oficial de ARCA** antes de programar. Lo marcado ⚠️ es una **decisión fiscal o contable** que el usuario debe confirmar con su **contador**. No dar asesoramiento fiscal como definitivo.

### 11.1 Requerimiento del usuario

- Enlazar los **pedidos de Rappi** con el área de **facturación** para generar la factura cuando entra el pedido.
- Si el cliente **solo aporta su nombre**, facturar como **"Consumidor Final"** **sin pedir más datos**.
- Si el cliente **pide factura tipo C**, emitirla con sus datos.
- Considerar la información **legal, administrativa y contable** de Argentina.

### 11.2 Marco normativo y técnico (verificado, con fecha)

- Organismo: **ARCA** (ex AFIP). Régimen de **factura electrónica**: cada comprobante necesita un **CAE** (Código de Autorización Electrónico de 14 dígitos). Sin CAE no es válido fiscalmente.
- Para software propio hay que usar los **Web Services**: **WSAA** (autenticación con certificado digital X.509 → token y firma) y **WSFEv1** (solicitar CAE para facturas A/B/C). Pasos previos: clave fiscal, **certificado digital** (clave privada + CSR cargado en ARCA), **asociar el certificado al servicio WSFE** (administrador de relaciones), y dar de alta un **punto de venta** del tipo "Factura electrónica – Web Services". Hay **ambiente de homologación** (pruebas) y de **producción**.
- **Factura C:** la emiten contribuyentes **Monotributistas** (y exentos) y **no discrimina IVA**. ⚠️ El pedido del usuario ("factura tipo C") implica que es monotributista: **confirmarlo**. Si fuera Responsable Inscripto, a un consumidor final le corresponde **Factura B**. Diseñar el módulo con el tipo de comprobante **configurable** (A/B/C) e implementar **C primero**.
- Códigos habituales de comprobante: 11 = Factura C, 12 = Nota de Débito C, 13 = Nota de Crédito C (verificar con `FEParamGetTiposCbte`).
- **Identificación del consumidor final:** desde la **RG 5700/2025** solo es obligatorio identificar al comprador (DNI/CUIL/CUIT/CDI) cuando la operación es **igual o superior a $10.000.000**; ya no se exigen nombre ni domicilio. Para menos de ese monto alcanza "Consumidor Final". El umbral **cambia con el tiempo**: guardarlo como **parámetro de configuración** (`umbral_identificacion_centavos`), no fijo en el código. ⚠️ Fuente: sitios contables; verificar vigencia.
- **Condición frente al IVA del receptor (obligatoria):** el campo de condición de IVA del receptor es dato obligatorio. Según un medio especializado, **desde el 1/12/2026 ARCA rechaza automáticamente** las solicitudes de CAE que no lo incluyan. Para consumidor final el código es **5**. Obtener la lista vigente con el método del servicio (`FEParamGetCondicionIvaReceptor`) y **no codificar a mano** los valores.
- **CAEA** (CAE anticipado): según una fuente comercial, desde junio de 2026 queda reservado a contingencias; usar **CAE en tiempo real**. El CAE tiene una vigencia de ~10 días corridos para entregar la factura (verificar).
- **Código QR** obligatorio en el comprobante (URL con datos codificados en base64). Verificar la especificación y el dominio vigentes (ARCA).
- Documentos: factura A/B/C emitida en **PDF** con CUIT, razón social, punto de venta y número, fecha, receptor, detalle, importes, **CAE y vencimiento** y QR.
- ⚠️ Conservación: guardar comprobantes y registros durante el plazo legal (normalmente 10 años; confirmar con el contador). Los comprobantes autorizados **no se editan ni se borran**; los errores se corrigen con **Nota de Crédito**.
- Fuera de alcance, para el contador: Monotributo (categoría, topes anuales), Ingresos Brutos y tributos municipales.

### 11.3 Preguntas abiertas para el contador (⚠️)

1. Condición del usuario: ¿Monotributista (qué categoría) o Responsable Inscripto? ¿Otra?
2. ¿Hay que facturar **cada pedido** individualmente a consumidor final, o se admite otro criterio?
3. **Rappi:** ¿quién emite el comprobante al cliente final y por qué monto? ¿Cómo se registra la **comisión de Rappi** (gasto) y las liquidaciones? ¿Cuál es el tratamiento si Rappi cobra el total al cliente? (No se encontró una respuesta oficial en las fuentes revisadas; revisar el contrato de Rappi Partners.)
4. Qué tope de facturación anual (categoría) debe controlar el sistema.
5. Redondeos y descuentos aplicables en el comprobante.
6. Forma de registrar notas de crédito y devoluciones.

### 11.4 Riesgos técnicos conocidos

- Los servidores de ARCA usan claves DH cortas que el OpenSSL por defecto de **Python 3.10+ rechaza**: puede ser necesario bajar `SECLEVEL` **solo para esos hosts** (consultar la documentación de la biblioteca elegida).
- Bibliotecas posibles (el agente debe **evaluar compatibilidad con Python 3.13 y la Pi 3** antes de elegir): `pyafipws` (histórica y muy usada; revisar mantenimiento), `arcalib` (enlaces generados desde los WSDL oficiales), o un servicio de terceros. Preferir la opción más simple y mantenida; **no** dejar secretos en servicios que el usuario no entienda. Documentar la decisión.
- Caída o lentitud de ARCA: el pedido debe poder quedar "pendiente de facturar" y reintentarse. **No duplicar** facturas: antes de reintentar, consultar el último comprobante autorizado (`FECompUltimoAutorizado`) y el comprobante (`FECompConsultar`).

### 11.5 Modelo de datos propuesto (importes en centavos enteros)

```sql
-- migración 002_pedidos_facturacion.sql  (importes en CENTAVOS, enteros)
CREATE TABLE pedidos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  origen TEXT NOT NULL DEFAULT 'rappi',            -- rappi | local | otro
  codigo_externo TEXT,                             -- nº de pedido de Rappi
  fecha TEXT NOT NULL,                             -- AAAA-MM-DD
  cliente_nombre TEXT,                             -- solo informativo; opcional
  total_centavos INTEGER NOT NULL,
  medio_pago TEXT,
  estado TEXT NOT NULL DEFAULT 'nuevo',            -- nuevo | entregado | cancelado
  creado_en TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  UNIQUE (origen, codigo_externo)
);
CREATE TABLE pedido_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
  descripcion TEXT NOT NULL,
  producto_fabricado_id INTEGER REFERENCES productos_fabricados(id),
  presentacion_id INTEGER REFERENCES presentaciones(id),
  cantidad REAL NOT NULL,
  precio_unitario_centavos INTEGER NOT NULL
);
CREATE TABLE comprobantes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pedido_id INTEGER REFERENCES pedidos(id),
  tipo_cbte INTEGER NOT NULL,                      -- 11 = Factura C, 13 = Nota de Crédito C
  punto_venta INTEGER NOT NULL,
  numero INTEGER,                                  -- lo asigna ARCA al autorizar
  fecha TEXT NOT NULL,
  receptor_tipo_doc INTEGER NOT NULL,              -- 99 = consumidor final sin identificar
  receptor_nro_doc TEXT NOT NULL,                  -- '0' si es 99
  receptor_condicion_iva INTEGER NOT NULL,         -- 5 = Consumidor Final
  receptor_nombre TEXT NOT NULL DEFAULT 'Consumidor Final',
  total_centavos INTEGER NOT NULL,
  cae TEXT, cae_vencimiento TEXT,
  estado TEXT NOT NULL DEFAULT 'borrador',         -- borrador | autorizada | rechazada | error_conexion
  comprobante_origen_id INTEGER REFERENCES comprobantes(id),  -- para notas de crédito
  ambiente TEXT NOT NULL DEFAULT 'homologacion',   -- homologacion | produccion
  observaciones_arca TEXT,
  creado_en TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  UNIQUE (ambiente, tipo_cbte, punto_venta, numero)
);
CREATE TABLE comprobante_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  comprobante_id INTEGER NOT NULL REFERENCES comprobantes(id) ON DELETE CASCADE,
  descripcion TEXT NOT NULL, cantidad REAL NOT NULL, precio_unitario_centavos INTEGER NOT NULL
);
CREATE TABLE comprobantes_log (                    -- trazabilidad SIN datos sensibles
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  comprobante_id INTEGER REFERENCES comprobantes(id),
  fecha_hora TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  evento TEXT NOT NULL, detalle TEXT
);
-- La configuración fiscal vive en 'configuracion' (claves fiscal_*), nunca el certificado ni la clave fiscal.
```

Reglas: un pedido tiene **a lo sumo un comprobante autorizado vigente** (salvo anulación con Nota de Crédito); un comprobante **autorizado es inmutable**.

### 11.6 Regla de negocio "Consumidor Final" vs "Factura C con datos"

```python
def construir_receptor(pedido, pidio_factura_con_datos, datos=None, umbral_centavos=1_000_000_000):
    """Devuelve el receptor del comprobante. 1.000.000.000 centavos = $10.000.000 (parámetro configurable)."""
    if pidio_factura_con_datos:
        # nombre/razón social, tipo y número de documento (DNI 96, CUIL 86, CUIT 80), condición de IVA
        return {"doc_tipo": datos["doc_tipo"], "doc_nro": datos["doc_nro"],
                "condicion_iva": datos["condicion_iva"], "nombre": datos["nombre"]}
    if pedido["total_centavos"] >= umbral_centavos:
        raise ValueError("Por el monto hay que identificar al comprador")
    # Solo el nombre (o nada): Consumidor Final, sin pedir otros datos
    return {"doc_tipo": 99, "doc_nro": "0", "condicion_iva": 5, "nombre": "Consumidor Final"}
```

El nombre que da el cliente de Rappi se guarda en el **pedido** (referencia) pero **no** se exige ni se imprime como dato fiscal cuando es consumidor final sin identificar.

Solicitud de CAE (estructura de referencia, **independiente de la biblioteca**; validar nombres y reglas exactas de Factura C en **homologación**):

```python
solicitud = {
    "CbteTipo": 11,                 # Factura C
    "PtoVta": 1,
    "Concepto": 1,                  # 1 = productos
    "DocTipo": 99, "DocNro": 0,     # consumidor final sin identificar
    "CondicionIVAReceptorId": 5,    # Consumidor Final
    "CbteFch": "20261001",
    "ImpTotal": 12500.00, "ImpTotConc": 0, "ImpNeto": 12500.00,   # Factura C: sin IVA discriminado
    "ImpOpEx": 0, "ImpIVA": 0, "ImpTrib": 0,
    "MonId": "PES", "MonCotiz": 1,
}
```

Esquema del QR (ejemplo; **verificar especificación y dominio vigentes**):

```python
import base64, json
datos = {"ver": 1, "fecha": "2026-10-01", "cuit": 20123456789, "ptoVta": 1, "tipoCmp": 11,
         "nroCmp": 123, "importe": 12500.00, "moneda": "PES", "ctz": 1,
         "tipoDocRec": 99, "nroDocRec": 0, "tipoCodAut": "E", "codAut": 70123456789012}
url_qr = "https://www.afip.gob.ar/fe/qr/?p=" + base64.b64encode(json.dumps(datos).encode()).decode()
```

### 11.7 Fases de la ampliación

**Fase 17 — Pedidos (Rappi).** Módulo "Pedidos": registro manual rápido de pedidos de Rappi (código, fecha, cliente opcional, ítems vinculados a productos fabricados/presentaciones con su precio de venta, total, medio de pago), estados, lista con filtros. El agente debe **investigar** si Rappi ofrece una API o exportación utilizable para restaurantes (no asumirlo); si no, empezar con carga manual e importación por CSV. *Aceptación:* cargar un pedido de ejemplo y verlo en la lista y en el Panel principal.

**Fase 18 — Configuración fiscal.** Pantalla Configuración → Datos fiscales: razón social, CUIT, condición ante el IVA/Monotributo, domicilio comercial, **punto de venta**, ambiente (homologación/producción), tipo de comprobante por defecto, umbral de identificación, rutas del certificado y la clave (**fuera del proyecto**). Guía paso a paso para el usuario: clave fiscal, generar el CSR, subirlo a ARCA, asociar el servicio WSFE y dar de alta el punto de venta. *Aceptación:* los datos se guardan y la pantalla valida que existan los archivos de certificado, sin mostrar su contenido.

**Fase 19 — Conexión con ARCA en homologación.** `services/arca/`: autenticación WSAA (token con caché y renovación), consulta de estado del servicio, consulta de tipos y condiciones de IVA, último comprobante autorizado, solicitud de CAE de **Factura C a consumidor final** en el ambiente de **pruebas**. *Aceptación:* se obtiene un CAE de prueba y se guarda el comprobante con estado `autorizada` en ambiente `homologacion`. Documentar errores comunes (certificado vencido, punto de venta no habilitado, numeración, receptor inválido, caída de ARCA).

**Fase 20 — Facturación de pedidos.** Botón **Facturar** en cada pedido (y opción en Configuración de **facturar automáticamente al marcar el pedido como entregado**). Flujo: solo nombre → Consumidor Final; "El cliente pidió factura C" → formulario con documento, nombre/razón social y condición de IVA. **PDF** del comprobante con CAE y QR, Notas de Crédito para anulaciones, reintentos seguros sin duplicar, bloqueo de edición de comprobantes autorizados. *Aceptación:* un pedido genera una factura de prueba correcta en homologación, con y sin datos del cliente.

**Fase 21 — Contabilidad y reportes fiscales.** Libro de ventas / listado de comprobantes por período para el contador (Excel y PDF), totales por tipo, **control del acumulado de facturación de 12 meses** frente al tope de la categoría (tope configurable, no fijo), conciliación de pedidos facturados vs. no facturados, resumen de comisiones de Rappi (según lo que indique el contador), ingresos vs. costos (usando los costos de Fase 10).

**Fase 22 — Pase a producción.** Checklist: certificado y punto de venta de **producción**, cambio de ambiente, prueba con un comprobante real de monto mínimo acordado con el contador, copia de seguridad previa y posterior, `debug=False`, login y HTTPS activos si hubiera acceso fuera de casa, monitoreo básico (estado de ARCA) y plan de contingencia. *Aceptación:* una factura real emitida y verificada con el QR en el sitio de ARCA.

### 11.8 Seguridad específica de facturación

- Certificado digital y **clave privada**: fuera del directorio del proyecto (por ejemplo `/home/luis/secretos/`, carpeta `700`, archivos `600`), **nunca** en Git, en logs ni en copias de seguridad públicas. La **clave fiscal** del usuario **no se guarda** en la app.
- Registrar en `comprobantes_log` solo eventos y códigos de error; no guardar tokens ni datos personales completos.
- Avisar cuando el certificado esté por vencer. Si la clave privada se filtra, **revocar** el certificado en ARCA.

---

## 12. Deuda técnica y mejoras recomendadas

1. **Git:** el proyecto no usa control de versiones. Proponer al usuario (explicándolo en simple) inicializar Git con `.gitignore` (`venv/`, `.env`, `*.db`, `backups/`, `exports/`, `secretos/`) y **un commit por fase** con etiqueta `fase-N-ok`. Pedir permiso antes.
2. Crear `requirements.txt` (`pip freeze`) y `README.md` (instalación, arranque, restauración).
3. Mover la lógica de negocio de las rutas a `services/` (conversión, costos, precios, compras) con funciones puras y probadas.
4. Migraciones versionadas (5.4).
5. Paquete/caja: equivalencias por producto (5.3).
6. Seguridad pendiente: login, CSRF, `SECRET_KEY`, `debug=False`, `waitress`, `systemd` (Sección 9).
7. Limpiar archivos `.respaldo` / `.antes_*` / `.parte1` y `__pycache__` (con permiso).
8. Mensajes de error amigables (páginas 404 y 500 en español con el diseño de la app).
9. Accesibilidad básica: etiquetas `for`/`id` en formularios, contraste suficiente en ambos modos.

---

## 13. Checklist de arranque para el agente

1. Leer este documento completo.
2. Inspeccionar el proyecto: `find ~/mi_negocio -path ~/mi_negocio/venv -prune -o -type f -not -name '*.pyc' -print` y comparar con 4.2.
3. Comprobar que arranca: `python -c "import app; print('Importación correcta')"`.
4. Pedir al usuario que ejecute el **checklist de la Fase 6 (7.3)** y confirme con `FUNCIONA` o envíe el error.
5. Con `FUNCIONA`: iniciar la **Fase 7** siguiendo el protocolo (1.1). **No** empezar facturación hasta cerrar las fases 7 a 16 salvo que el usuario cambie el orden.
6. En cada fase: respaldo previo, cambios, verificaciones, **Informe de fase**, espera.

Mensaje sugerido del usuario al agente: *"Lee `CONTEXTO_MI_NEGOCIO.md` completo. Soy principiante. Trabaja por fases y, al terminar cada una, muéstrame cómo verla y espera a que yo escriba FUNCIONA. Empieza revisando el proyecto y pidiéndome que confirme la prueba de la Fase 6."*

---

## 14. Glosario (para explicar al usuario)

- **Terminal:** ventana donde se escriben órdenes de texto.
- **Servidor:** programa que atiende las páginas de la app (aquí, `python app.py`).
- **Entorno virtual (venv):** carpeta aislada con las herramientas de Python del proyecto.
- **Base de datos (SQLite):** archivo `negocio.db` con tablas, como un Excel con hojas conectadas.
- **Blueprint:** "módulo" de Flask (proveedores, productos…).
- **Plantilla (Jinja2):** página HTML con partes que se rellenan con datos.
- **CAE:** código de autorización de ARCA para que una factura electrónica sea válida.
- **Homologación:** ambiente de pruebas de ARCA, donde no hay validez fiscal.
- **Punto de venta:** número de 5 dígitos desde el cual se emiten las facturas.
- **Consumidor Final:** comprador sin identificar (documento 99, condición de IVA 5).
- **Nota de Crédito:** comprobante que anula o corrige una factura ya autorizada.

---

*Fuentes consultadas el 2026-10-01 (secundarias; verificar en ARCA antes de programar): guías de facturación electrónica y puntos de venta de ARCA (YoFacturo, Develop Argentina, Invopop), umbral de identificación de consumidor final (RG 5700/2025, vía Contadores en Red y Tributo Simple), obligatoriedad de la condición de IVA del receptor desde el 1/12/2026 (iProfesional), bibliotecas `pyafipws`, `arcalib` y `arca-status`.*