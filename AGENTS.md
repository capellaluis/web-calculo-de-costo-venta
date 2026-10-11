# AGENTS — Mi Negocio (cálculo de costo y venta)

App web local para administrar un negocio de alimentos y bebidas: proveedores,
compras, productos, precios, recetas, costos, márgenes, fabricados, ventas,
reportes, Excel y copias de seguridad. Corre en PC o Raspberry Pi, **sin Internet**
para el uso diario.

## 🔗 Master Agent Configuration

> [!IMPORTANT]
> Este proyecto hereda skills, SDD, seguridad y Engram del **Master AGENTS.md**:
> **📂 `~/repos/skills-engine/skills/AGENTS.md`** — leerlo antes de actuar.
>
> Skill principal para este stack: `python-architect`.

---

## ⚠️ Git Policy — CRÍTICO

### Commits (NUNCA sin pedido explícito)

**REGLA OBLIGATORIA**: No hacer `git commit` NUNCA sin que el usuario lo pida explícitamente.

Flujo correcto:
1. Implementar cambios
2. **SIEMPRE** indicar cómo probar ANTES de pedir commit (comandos, pasos específicos)
3. Esperar confirmación del usuario ("haz commit", "dale commit", "commitea")
4. Solo ENTONCES hacer `git commit`

**NUNCA**:
- Hacer commit automáticamente tras terminar un cambio
- Asumir que "voy a commitear" es permiso
- Saltarse la fase de prueba

- Commits con `conventional-commits-standard` skill
- Sin atribución de IA (global CLAUDE.md lo prohíbe)
- **NUNCA** `git push` sin confirmación explícita

---

## 📌 Stack

- **Python 3.10+** (probado con 3.13) + **Flask 3** + **Jinja2**
- **SQLite** (`database/negocio.db`, acceso con `sqlite3` crudo, sin ORM)
- **waitress** (servidor de uso diario), **openpyxl** (Excel), **python-dotenv**
- Frontend: HTML/CSS propio + Bootstrap Icons + Chart.js, todo **local** en `static/` (sin CDN)
- Tests: **pytest**

## 🗂️ Estructura y capas

| Capa | Ruta | Responsabilidad |
|---|---|---|
| Rutas | `routes/<modulo>.py` | Un `Blueprint` por módulo (`bp`, `url_prefix`). Lee el form, llama al service, renderiza. Sin lógica de negocio. |
| Servicios | `services/<modulo>.py` | Lógica y cálculos. Errores de validación como `Error<Modulo>(ValueError)` con mensaje en español. |
| Datos | `database/db.py` | `obtener_conexion()` → `sqlite3.Row`, `PRAGMA foreign_keys = ON`. |
| Esquema | `database/schema.sql` + `database/migraciones/NNN_nombre.sql` | Migraciones versionadas vía `PRAGMA user_version` (`database/migrar.py`, hace copia previa). |
| Vistas | `templates/<modulo>_{lista,form,ver}.html` | Extienden `base.html`. Parciales con prefijo `_`. |
| App | `app.py` (dev) / `servidor.py` (waitress) | Registro de blueprints + `requerir_login` global. |

Nuevo módulo → blueprint en `routes/`, lógica en `services/`, registrar en `app.py`,
templates `<modulo>_*.html`, tests en `tests/`.

## ✍️ Convenciones

- **Idioma**: código, identificadores, comentarios, mensajes y UI **en español** (el proyecto ya está así; mantener consistencia).
- **Dinero y cantidades**: `Decimal`, nunca `float`. Redondeo `ROUND_HALF_UP` a 2 decimales. Leer input con `services/numeros.py` (`leer_decimal`).
- **Unidades**: conversiones vía `services/unidades.py`.
- Formato moneda en vistas: filtro de `app.py` (`$30.000`, `$1.234,50`).
- **Cambios de esquema**: SIEMPRE nueva migración `NNN_*.sql`; actualizar también `schema.sql` para bases nuevas. Nunca editar migraciones ya aplicadas.
- Todo endpoint requiere login salvo los de `ENDPOINTS_SIN_LOGIN` en `app.py`.

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
pytest
```

- Fixtures en `tests/conftest.py`: `db_temporal` / `con` crean una base temporal desde `schema.sql`; backups aislados.
- **NUNCA** tocar `database/negocio.db` en tests.
- Tests de service: `test_<modulo>.py`. Tests de rutas: `test_rutas_<modulo>.py`.
- Strict TDD: test primero.

## 🛡️ Seguridad

- **NUNCA** leer/mostrar `.env`, `.secret_key`, `negocio.db` ni backups.
- No exponer la app a Internet; `app.py` con `debug` solo en red de confianza.
- SQL siempre parametrizado (`?`), nunca f-strings/concatenación.
- Sin dependencias por CDN: todo asset va a `static/`.

## 🧹 Deuda conocida

Hay archivos de respaldo versionados (`*.respaldo`, `*.antes_*`, `app copy.py`,
`routes/dashboard.py.parte1`). No editarlos ni tomarlos como fuente de verdad;
la fuente es el archivo sin sufijo.
