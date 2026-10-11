# MI NEGOCIO

Aplicación web para administrar un negocio de alimentos y bebidas: **proveedores,
compras, productos, precios, recetas, costos, márgenes, productos fabricados,
ventas, reportes, Excel y copias de seguridad**.

Está hecha con **Python + Flask + SQLite**. Corre en tu computadora o en una
**Raspberry Pi**, sin hosting y **sin Internet** para el uso diario (Internet solo
hace falta la primera vez para instalar, y si usás la recuperación por correo).

---

## Índice

1. [Requisitos](#1-requisitos)
2. [Instalación rápida](#2-instalación-rápida)
3. [Cómo iniciar la aplicación](#3-cómo-iniciar-la-aplicación)
4. [Primer uso: crear tu usuario](#4-primer-uso-crear-tu-usuario)
5. [Qué incluye](#5-qué-incluye)
6. [Copias de seguridad](#6-copias-de-seguridad)
7. [Excel y Reportes](#7-excel-y-reportes)
8. [El archivo .env](#8-el-archivo-env)
9. [La base de datos y mover a otra máquina](#9-la-base-de-datos-y-mover-a-otra-máquina)
10. [Usar desde el teléfono o la tablet](#10-usar-desde-el-teléfono-o-la-tablet)
11. [Actualizar una instalación existente](#11-actualizar-una-instalación-existente)
12. [Git y Visual Studio Code](#12-git-y-visual-studio-code)
13. [Estructura del proyecto](#13-estructura-del-proyecto)
14. [Problemas frecuentes](#14-problemas-frecuentes)
15. [Seguridad: lo que NO se debe hacer](#15-seguridad-lo-que-no-se-debe-hacer)

---

## 1. Requisitos

- **Python 3.10 o superior** (se probó con 3.13).
- **Git** (solo para clonar/actualizar el proyecto).
- Internet la primera vez (para instalar las librerías).

Cómo conseguir Python:

- **Windows**: <https://www.python.org/downloads/> → en el instalador marcá
  **"Add python.exe to PATH"**. (No uses el Python de la Microsoft Store.)
- **Debian / Ubuntu / Raspberry Pi OS**:
  ```bash
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip git
  ```
- **macOS**: <https://www.python.org/downloads/> o `brew install python`.

Comprobar la instalación: `py --version` (Windows) o `python3 --version` (Linux/Mac).
Debe mostrar algo como `Python 3.13.5`.

---

## 2. Instalación rápida

Los instaladores hacen todo solos: crean el entorno virtual (`venv`), instalan
las librerías, preparan el `.env`, descargan íconos/gráficos y crean la base de
datos. Se pueden ejecutar varias veces: **no borran tus datos**.

```bash
git clone <dirección-del-repositorio>
cd mi_negocio
```

- **Windows**: doble clic en **`setup.bat`** (o `setup.bat` desde CMD).
- **Linux / Mac / Raspberry Pi**: `bash setup.sh`.

Al terminar debe decir **LISTO**. En una Raspberry Pi 3 puede tardar unos minutos.

### Inicializar el `.env` con tu propia clave

El instalador crea el `.env` con una `SECRET_KEY` aleatoria. Si preferís crearlo
vos (o el instalador falló), hacelo **antes** de iniciar la aplicación. Si el `.env`
ya existe, el instalador **no lo toca**.

1. Copiá la plantilla:

   ```bash
   cp .env.example .env              # Linux / Mac / Raspberry Pi
   copy .env.example .env            # Windows (CMD)
   ```

2. Generá una clave aleatoria de 64 caracteres:

   **Linux / Mac / Raspberry Pi**

   ```bash
   openssl rand -hex 32
   ```

   **Windows (PowerShell)** — equivalente sin instalar nada:

   ```powershell
   $b = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); -join ($b | ForEach-Object { $_.ToString('x2') })
   ```

   O, en cualquier sistema con Python:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Abrí `.env` y reemplazá `CAMBIAR_POR_UNA_CLAVE_ALEATORIA` por la clave generada:

   ```
   SECRET_KEY=3f9a1c...e07b
   ```

4. En Linux / Raspberry Pi, dejá el archivo legible solo por tu usuario:
   `chmod 600 .env`.

> ⚠️ Cada instalación debe tener **su propia clave**. No la compartas, no la copies
> en el código y no subas el `.env` a Git.

### Instalación manual (si un script falla)

Todos los comandos se escriben dentro de la carpeta del proyecto.

**Windows (CMD o PowerShell)**

```bat
py -3 -m venv venv
venv\Scripts\activate.bat          :: CMD
venv\Scripts\Activate.ps1          :: PowerShell
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\preparar_entorno.py
python scripts\descargar_recursos.py
python database\init_db.py
```

Si PowerShell dice que *la ejecución de scripts está deshabilitada*, usá CMD o
ejecutá una sola vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

**Linux / Mac / Raspberry Pi**

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/preparar_entorno.py
python scripts/descargar_recursos.py
python database/init_db.py
```

Al activar el entorno, al inicio de la línea aparece `(venv)`. Cada vez que abras
una terminal nueva tenés que volver a entrar a la carpeta y **activar el venv**;
los demás pasos no se repiten.

---

## 3. Cómo iniciar la aplicación

### Uso diario (recomendado) — servidor de producción `waitress`

```bash
# Windows:                 iniciar.bat   (o)   venv\Scripts\python.exe servidor.py
# Linux / Mac / Raspberry: bash iniciar.sh (o)   venv/bin/python servidor.py
```

`servidor.py` usa **waitress** (servidor estable) y **no muestra errores detallados
ni recarga solo**: es el modo recomendado para todos los días. Toma la dirección y
el puerto del `.env` (`APP_HOST` / `APP_PORT`).

Si todavía no ejecutaste el instalador (falta el `venv` o la base),
`iniciar.bat` / `iniciar.sh` lo ejecutan por vos.

### Para programar (servidor de desarrollo)

```bash
python app.py
```

Recarga solo cuando cambiás el código y muestra errores detallados. **No** lo uses
para el uso diario ni en una red que no sea de confianza (ver
[Seguridad](#15-seguridad-lo-que-no-se-debe-hacer)).

Al arrancar (con cualquiera de los dos), la aplicación aplica las **migraciones
pendientes** de la base y hace una copia de seguridad antes.

Luego abrí el navegador en **<http://127.0.0.1:5000>**.

Para **apagar**: volvé a la ventana de la terminal y presioná **Ctrl + C**.
Mientras está encendida, esa ventana queda ocupada (es normal); no la cierres si
querés seguir usando la aplicación.

---

## 4. Primer uso: crear tu usuario

La primera vez que abrís la aplicación te pide **crear tu usuario administrador**:
usuario, **correo** y contraseña. Después, todo pide **iniciar sesión**.

- Para **recuperar** el usuario y/o la contraseña: en el login, *"¿Olvidaste el
  usuario o la clave?"* → te llega un **código por correo** → lo escribís y ponés
  una clave nueva.
- Para que salga el correo, configurá **Configuración → Correo** con tu **Gmail**
  y una **contraseña de aplicación** (en Gmail: activá la verificación en dos pasos
  y creá una "Contraseña de aplicaciones"). Sin internet, la recuperación por correo
  no funciona.

> **TODO**: La función de correo actual usa SMTP directo a Gmail. Para producción o mayor confiabilidad,
> considerar migrar a **SendGrid** o un servicio similar:
> - **Reemplazar en**: `services/correo.py` — cambiar `smtplib.SMTP()` por la API HTTP de SendGrid
> - **Instalar**: `pip install sendgrid` (agregar a `requirements.txt`)
> - **Configurar**: guardar la clave de API de SendGrid en `.env` (`SENDGRID_API_KEY`) en lugar de la contraseña SMTP
> - **Beneficios**: webhooks de entrega, mejor manejo de errores, no exponer credenciales SMTP en la red local

---

## 5. Qué incluye

- **Panel principal**: tarjetas y gráficos (compras, ventas del mes, ganancia,
  aumentos de precios, etc.).
- **Proveedores** y **Compras** (con edición).
- **Productos** (materias primas) e **Historial de precios**.
- **Recetas** y **Costos** (con gastos fijos y márgenes de ganancia por producto).
- **Productos fabricados** con **presentaciones** y precios de **tienda** y
  **delivery**.
- **Ventas / pedidos** (canal tienda/delivery, estado, forma de pago, ganancia).
- **Reportes** con filtros y exportación.
- **Excel**: exporta todo a un archivo `.xlsx`.
- **Copias de seguridad**, **Nombre y logo** del negocio y **Login**.

---

## 6. Copias de seguridad

En **Configuración → Copias de seguridad** podés:

- **Crear** una copia de toda la base.
- **Descargar** cada copia.
- **Restaurar** una copia (guarda antes una copia de la actual).
- **Eliminar** copias.

Además, la aplicación crea **copias automáticas** después de cada cambio y
conserva las **últimas 30**.

> ⚠️ Una copia en la misma máquina **no te salva si falla el disco**. Descargá una
> copia de vez en cuando y guardala **fuera** (pendrive, correo, nube).

La carpeta de copias es `backups/`.

### A mano (con la aplicación apagada)

Hacer una copia:

```bash
copy database\negocio.db backups\negocio_copia.db     # Windows
cp database/negocio.db backups/negocio_copia.db       # Linux/Mac
```

Restaurar una copia:

1. Renombrá la base actual: `negocio.db` → `negocio.db.antes_restaurar`.
2. Copiá la copia elegida a `database/negocio.db`.
3. Iniciá la aplicación y comprobá que estén tus datos.

---

## 7. Excel y Reportes

- **Excel** (menú): botón **Exportar a Excel** → descarga
  `Mi_Negocio_AAAA-MM-DD.xlsx` con hojas de proveedores, productos, compras,
  recetas, fabricados, costos y precios, ventas, etc.
- **Reportes** (menú): elegís un reporte, filtrás (fechas, proveedor, categoría,
  canal, estado, cliente) y lo **exportás**.

Los archivos generados se guardan en `exports/`.

---

## 8. El archivo .env

Es un archivo de texto con la configuración local. El instalador lo crea copiando
`.env.example` y generando una clave secreta nueva. Se puede abrir con el Bloc de
notas o con VS Code. **Nunca se sube a Git.**

| Clave | Para qué sirve |
|---|---|
| `SECRET_KEY` | Clave secreta de la aplicación (se genera sola). Si la cambiás, se cierran las sesiones abiertas. |
| `APP_HOST` | `127.0.0.1` = solo esta máquina. `0.0.0.0` = también desde otros equipos del Wi-Fi (Raspberry). |
| `APP_PORT` | Puerto (por defecto 5000). |

Para generar o cambiar la `SECRET_KEY` a mano, ver
[Inicializar el `.env` con tu propia clave](#inicializar-el-env-con-tu-propia-clave).

Si no hay `SECRET_KEY` en el `.env`, la app crea un archivo local **`.secret_key`**
(tampoco se sube a Git).

### Otros detalles

- Los cambios en `.env` se aplican al **reiniciar** la aplicación.
- `APP_HOST` y `APP_PORT` solo los usa `servidor.py` (uso diario). `python app.py`
  siempre escucha en `0.0.0.0:5000` con el modo de depuración activado.
- Con `servidor.py` las plantillas quedan en memoria: si editás una plantilla o el
  diseño, reiniciá la aplicación y recargá el navegador con **Ctrl + F5**.

---

## 9. La base de datos y mover a otra máquina

- Toda la información vive en **un solo archivo**: `database/negocio.db`.
- Se crea sola con el instalador (o a mano con `python database/init_db.py`) a
  partir del plano `database/schema.sql`. Ejecutar `init_db.py` de nuevo **no borra
  ni duplica** datos.
- Trae cargados: **8 unidades** (g, kg, ml, l, unidad, docena, paquete, caja), los
  **3 márgenes** (30, 50 y 70 %) y los gastos fijos Gas, Agua y Luz. Se cambian desde
  **Configuración**, sin tocar código.
- Los cambios de estructura se aplican solos al iniciar (migraciones en
  `database/migraciones/`), con copia de seguridad previa.
- **No se sube a Git** (son tus datos). Al clonar el proyecto en otra PC, arranca **vacía**.
- Para **llevar tus datos**: con la aplicación apagada, copiá `database/negocio.db`
  (o una copia de `backups/`) a la carpeta `database/` de la otra máquina, o
  restaurá una copia desde la pantalla de Copias de seguridad.

### Empezar de cero

> ⚠️ **Esto borra TODOS los datos.** Hacé primero una copia (ver
> [Copias de seguridad](#6-copias-de-seguridad)).

Con la aplicación apagada, borrá `database/negocio.db` y ejecutá de nuevo
`setup.bat` / `setup.sh`. Se crea una base nueva y vacía.

---

## 10. Usar desde el teléfono o la tablet

1. En `.env`: `APP_HOST=0.0.0.0` y reiniciá la aplicación.
2. Averiguá la IP del equipo que corre la app: `ipconfig` (Windows, "Dirección IPv4")
   o `hostname -I` (Linux/Pi).
3. En el teléfono (mismo Wi-Fi): `http://ESA-IP:5000` (ej.: `http://192.168.1.100:5000`).

En Windows la primera vez el Firewall pide permiso: permití solo en redes privadas.

La IP puede cambiar si se reinicia el router.

---

## 11. Actualizar una instalación existente

Por ejemplo, en la Raspberry Pi que ya está funcionando:

```bash
cd ~/mi_negocio
git pull
source venv/bin/activate
pip install -r requirements.txt      # por si hay librerías nuevas
bash iniciar.sh
```

Al iniciar se aplican solas las migraciones pendientes (con copia previa).
Si la máquina no tenía `.env`, crealo con `python scripts/preparar_entorno.py` y,
en la Raspberry, dejá `APP_HOST=0.0.0.0` para poder entrar desde el teléfono.

---

## 12. Git y Visual Studio Code

**Qué se sube a Git**: el código, las plantillas, el CSS, `schema.sql`, las
migraciones, `requirements*.txt`, `.env.example`, los scripts y este README.

**Qué NO se sube** (ya está en `.gitignore`): `venv/`, `.env`, `.secret_key`, la base
de datos (`*.db`), `backups/`, `exports/` y `static/uploads/`.

Si el repositorio ya tenía subido `negocio.db` o `.env`, quitalos del seguimiento
(no se borran de tu disco):

```bash
git rm --cached database/negocio.db
git rm --cached .env
git commit -m "chore: stop tracking data and secrets"
```

Si alguna vez subiste un `.env` con una clave real, **cambiala**.

Flujo en una PC nueva: `git clone` → `setup.bat` (o `bash setup.sh`) → iniciar.

Los `.sh` se guardan con saltos de línea de Linux y los `.bat` con los de Windows
gracias a `.gitattributes`. **No lo borres.**

### Visual Studio Code

1. *Archivo → Abrir carpeta…* y elegí la carpeta del proyecto.
2. Instalá la extensión **Python** de Microsoft.
3. `Ctrl + Shift + P` → *Python: Select Interpreter* → elegí el de la carpeta `venv`
   (`venv\Scripts\python.exe` en Windows).
4. Abrí la terminal de VS Code (`Ctrl + ñ`) y ejecutá `python app.py`.

---

## 13. Estructura del proyecto

```
mi_negocio/
  app.py                 Servidor de desarrollo (recarga sola)
  servidor.py            Servidor de uso diario (waitress)
  requirements.txt       Librerías necesarias
  requirements-dev.txt   Librerías para pruebas (pytest)
  .env / .env.example    Configuración local (el .env NO se sube a Git)
  setup.bat / setup.sh   Instaladores
  iniciar.bat / .sh      Inician la app (waitress)
  database/
    schema.sql           Plano de la base + datos iniciales
    db.py                Conexión a la base
    migrar.py            Migraciones versionadas (con copia previa)
    migraciones/         Cambios de esquema (001, 002, ...)
    init_db.py           Crea negocio.db
    negocio.db           Tus datos (NO se sube a Git)
  routes/                Pantallas por módulo
  services/              Lógica de negocio (cálculos)
  models/                Reservado para el futuro
  templates/             Páginas HTML
  static/                CSS, JS, íconos y logos subidos
  scripts/               Herramientas de instalación
  tests/                 Pruebas automáticas (pytest)
  exports/               Excel generado
  backups/               Copias de seguridad
```

---

## 14. Problemas frecuentes

- **"Python no se encontró" / se abre la Microsoft Store (Windows)**: instalá Python
  desde python.org marcando "Add python.exe to PATH". Si sigue: *Configuración →
  Aplicaciones → Configuración avanzada → Alias de ejecución de aplicaciones* y
  desactivá los alias de `python.exe` y `python3.exe`.
- **"No module named flask"** (o `dotenv`, `openpyxl`, `waitress`): no activaste el
  venv o faltan las librerías → usá `iniciar.bat` / `iniciar.sh`, o activá el venv y
  `pip install -r requirements.txt`.
- **"ensurepip is not available" / falla `python3 -m venv`** (Debian, Raspberry):
  `sudo apt install -y python3-venv python3-pip`, borrá la carpeta `venv` si quedó a
  medias y repetí el instalador.
- **"externally-managed-environment"** al usar pip: estás usando el Python del
  sistema; activá primero el entorno virtual.
- **PowerShell: "la ejecución de scripts está deshabilitada"**: usá CMD, o ejecutá una
  vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- **`/bin/bash^M: bad interpreter`** (el `.sh` tiene saltos de línea de Windows):
  `sed -i 's/\r$//' setup.sh iniciar.sh`.
- **"Address already in use"**: el puerto 5000 está ocupado → cambiá `APP_PORT` en
  `.env` (ej.: 5001). En macOS el 5000 a veces lo usa el sistema.
- **`sqlite3.OperationalError: no such table`**: la base no se creó →
  `python database/init_db.py`.
- **No se ve un cambio de plantilla/diseño**: reiniciá la app y recargá con **Ctrl + F5**.
- **Desde el teléfono no abre**: mismo Wi-Fi, `APP_HOST=0.0.0.0`, app reiniciada,
  dirección con `http://` y `:5000`, y Firewall de Windows.
- **Se ve sin íconos/gráficos**: `python scripts/descargar_recursos.py` (con Internet)
  y recargá con **Ctrl + F5**. Si falla durante la instalación, el instalador sigue;
  volvé a ejecutarlo y solo descarga lo que falta.
- **Pruebas**: en el venv, `pip install -r requirements-dev.txt` y luego `pytest`.

---

## 15. Seguridad: lo que NO se debe hacer

- No subir a Git el `.env`, `.secret_key`, la base de datos ni certificados.
- No escribir contraseñas dentro del código.
- **No exponer la app a Internet** (no abrir puertos del router, sin túneles).
- No usar el servidor de desarrollo (`python app.py`) en una red que no sea de
  confianza: escucha en toda la red con el depurador activo, y el depurador permite
  ejecutar código a quien lo vea. Para uso diario usá `servidor.py` (waitress).
- Hacer copias de seguridad de `database/negocio.db` y guardar al menos una **fuera**
  de la máquina.
