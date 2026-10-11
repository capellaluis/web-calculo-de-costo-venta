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

## 🧰 Skills del proyecto (versionadas)

Las skills de uso diario viven en **`.skills/`** (fuente de verdad, versionada).
`.claude/skills` es un symlink a `../.skills`, así Claude Code las descubre solo al clonar.
Otros agentes: leer `.skills/<skill>/SKILL.md` antes de actuar cuando aplique el trigger.

| Dominio | Skill | Cuándo |
|---|---|---|
| **Negocio** | [`negocio-costos`](.skills/negocio-costos/SKILL.md) | Costos, precios, márgenes, unidades, compras, recetas, fabricados, ventas. **Obligatoria** antes de tocar cálculos. |
| Python | [`python-architect`](.skills/python-architect/SKILL.md) | Nuevos módulos/services, tipado, estructura. |
| Commits | [`conventional-commits-standard`](.skills/conventional-commits-standard/SKILL.md) | Todo mensaje de commit (solo con pedido explícito). |
| Commits | [`work-unit-commits`](.skills/work-unit-commits/SKILL.md) | Dividir cambios en commits revisables (test + código + docs). |
| PRs | [`branch-pr`](.skills/branch-pr/SKILL.md) / [`chained-pr`](.skills/chained-pr/SKILL.md) | Abrir PR a `master`; dividir PRs > 400 líneas. |
| Review | [`judgment-day`](.skills/judgment-day/SKILL.md) | Review adversarial doble antes de mergear cambios críticos. |
| Diseño UI | [`frontend-design`](.skills/frontend-design/SKILL.md) | Templates Jinja, CSS, UX de pantallas. |
| Diseño UI | [`theme-factory`](.skills/theme-factory/SKILL.md) | Paletas y temas (claro/oscuro). |
| Testing web | [`webapp-testing`](.skills/webapp-testing/SKILL.md) | Pruebas E2E de la web con Playwright. |
| Docs | [`cognitive-doc-design`](.skills/cognitive-doc-design/SKILL.md) | `docs/`, README, `ANALISIS_*.md`. |

No versionadas (vienen con Claude Code o con la config global): `/security-review`, `/code-review`,
`/simplify`, `xlsx` y `pdf` (licencia propietaria de Anthropic, no copiar al repo), `sdd-*`.

**Actualizar una skill**: editar en `.skills/` y commitear. Las copiadas desde
`~/repos/skills-engine` no se sincronizan solas; re-copiar si cambia el origen.

**Windows**: el symlink requiere `git config core.symlinks true` (y modo desarrollador)
antes de clonar; si no, `.claude/skills` queda como archivo de texto y hay que recrearlo.

---

## ⚠️ Git Policy — CRÍTICO

### Commits (NUNCA sin pedido explícito)

**REGLA OBLIGATORIA**: No hacer `git commit` NUNCA sin que el usuario lo pida explícitamente.

**Flujo correcto (OBLIGATORIO)**:
1. ✅ Implementar cambios
2. ✅ **SIEMPRE indicar cómo probar** ANTES de pedir commit (comandos exactos, pasos claros, URLs si es web)
3. ⏸️ Esperar confirmación explícita del usuario:
   - "haz commit" / "dale commit" / "commitea" / "crea el commit"
4. ✅ Solo ENTONCES ejecutar `git commit`

**NUNCA**:
- Hacer commit automáticamente tras terminar un cambio
- Asumir que "voy a commitear" es permiso
- Saltarse la fase de prueba/verificación
- Skippear la indicación de "cómo probar"

**Commits**:
- Usar skill `conventional-commits-standard` antes de escribir mensaje
- Sin atribución de IA (global CLAUDE.md lo prohíbe)
- **NUNCA** `git push` sin confirmación explícita

**Documentación**:
- Actualizar `docs/` y `AGENTS.md` cuando cambios afecten convenciones
- Marcar puntos del análisis (`ANALISIS_*.md`) como "✅ RESUELTO" con commit asociado

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
- **Acciones destructivas** (borrar, restaurar, quitar): usar la macro `form_confirmar` de
  `templates/_confirmacion.html` (modal de `static/js/ui.js`). Nunca `confirm()` del navegador.
  Desde JS: `UI.confirmar({titulo, texto, aceptar, peligro}).then(ok => ...)`.
- **Avisos tras una acción**: redirigir con `?aviso=<clave>` y resolver con
  `services/avisos.leer_aviso(AVISOS, request.args.get("aviso"))`. Texto suelto = éxito;
  otro tipo con `crear_aviso(texto, tipo="info|exito|advertencia|error", segundos=None)`.
  `base.html` los muestra como notificación flotante (`templates/_avisos.html`); no pintarlos
  a mano en cada plantilla. Tiempo: `APP_AVISO_SEGUNDOS` (5 por defecto, 0 = fijo).
  Desde JS: `UI.notificar(texto, {tipo, titulo, segundos})`. Los errores de validación de
  formularios (`error`) siguen inline junto al formulario.
- **Colores**: usar tokens de `estilo.css` (`--peligro`, `--c`, `--superficie`…) y definir su
  variante en `:root[data-tema="oscuro"]`; nunca colores fijos que rompan el modo oscuro.

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
