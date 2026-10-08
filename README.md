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
11. [Estructura del proyecto](#11-estructura-del-proyecto)
12. [Problemas frecuentes](#12-problemas-frecuentes)
13. [Seguridad: lo que NO se debe hacer](#13-seguridad-lo-que-no-se-debe-hacer)

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

Comprobar la instalación: `py --version` (Windows) o `python3 --version` (Linux/Mac).

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

Al terminar debe decir **LISTO**.

### Instalación manual (si un script falla)

```bash
python -m venv venv
# Windows:  venv\Scripts\activate.bat      Linux/Mac:  source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/preparar_entorno.py
python scripts/descargar_recursos.py
python database/init_db.py
```

---

## 3. Cómo iniciar la aplicación

### Uso diario (recomendado) — servidor de producción `waitress`

```bash
# Windows:                 iniciar.bat   (o)   venv\Scripts\python.exe servidor.py
# Linux / Mac / Raspberry: bash iniciar.sh (o)   venv/bin/python servidor.py
```

`servidor.py` usa **waitress** (servidor estable) y **no muestra errores detallados
ni recarga solo**: es el modo recomendado para todos los días.

### Para programar (servidor de desarrollo)

```bash
python app.py
```

Recarga solo cuando cambiás el código y muestra errores detallados. **No** lo uses
para el uso diario ni en una red que no sea de confianza.

Luego abrí el navegador en **<http://127.0.0.1:5000>**.

Para **apagar**: volvé a la ventana de la terminal y presioná **Ctrl + C**.
Mientras está encendida, esa ventana queda ocupada (es normal).

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

Es un archivo de texto con la configuración local (lo crea el instalador). **Nunca
se sube a Git.**

| Clave | Para qué sirve |
|---|---|
| `SECRET_KEY` | Clave secreta de la aplicación (se genera sola). |
| `APP_HOST` | `127.0.0.1` = solo esta máquina. `0.0.0.0` = también desde otros equipos del Wi-Fi (Raspberry). |
| `APP_PORT` | Puerto (por defecto 5000). |
| `APP_DEBUG` | `1` = recarga sola al editar (programar). `0` = normal (uso diario). |

Si no hay `SECRET_KEY`, se crea un archivo local **`.secret_key`** (tampoco se sube a Git).

---

## 9. La base de datos y mover a otra máquina

- Toda la información vive en **un solo archivo**: `database/negocio.db`.
- **No se sube a Git** (son tus datos). Al clonar el proyecto en otra PC, arranca **vacía**.
- Para **llevar tus datos**: con la aplicación apagada, copiá `database/negocio.db`
  a la carpeta `database/` de la otra máquina (o restaura una copia desde la pantalla
  de Copias de seguridad).

---

## 10. Usar desde el teléfono o la tablet

1. En `.env`: `APP_HOST=0.0.0.0` y reiniciá la aplicación.
2. Averiguá la IP del equipo que corre la app: `ipconfig` (Windows) o `hostname -I` (Linux/Pi).
3. En el teléfono (mismo Wi-Fi): `http://ESA-IP:5000` (ej.: `http://192.168.1.100:5000`).

En Windows la primera vez el Firewall pide permiso: permití solo en redes privadas.

---

## 11. Estructura del proyecto

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
    migrar.py            Migraciones versionadas (con copia previa)
    migraciones/         Cambios de esquema (001, 002, ...)
    init_db.py           Crea negocio.db
    negocio.db           Tus datos (NO se sube a Git)
  routes/                Pantallas por módulo
  services/              Lógica de negocio (cálculos)
  templates/             Páginas HTML
  static/                CSS, JS, íconos y logos subidos
  tests/                 Pruebas automáticas (pytest)
  exports/               Excel generado
  backups/               Copias de seguridad
```

---

## 12. Problemas frecuentes

- **"No module named flask"**: no activaste el venv o faltan las librerías →
  `pip install -r requirements.txt`.
- **"externally-managed-environment"** al usar pip: estás usando el Python del
  sistema; activá primero el entorno virtual.
- **"Address already in use"**: el puerto 5000 está ocupado → cambiá `APP_PORT` en `.env`.
- **No se ve un cambio de plantilla/diseño**: reiniciá la app y recargá con **Ctrl + F5**.
- **Desde el teléfono no abre**: mismo Wi-Fi, `APP_HOST=0.0.0.0`, app reiniciada, y Firewall.
- **Se ve sin íconos/gráficos**: `python scripts/descargar_recursos.py` (con Internet).
- **Pruebas**: en el venv, `pip install -r requirements-dev.txt` y luego `pytest`.

---

## 13. Seguridad: lo que NO se debe hacer

- No subir a Git el `.env`, `.secret_key`, la base de datos ni certificados.
- No escribir contraseñas dentro del código.
- **No exponer la app a Internet** (no abrir puertos del router, sin túneles).
- No usar el servidor de desarrollo (`app.py`) con `debug=True` en una red que no
  sea de confianza; para uso diario usá `servidor.py` (waitress).
- Hacer copias de seguridad de `database/negocio.db` y guardar al menos una **fuera**
  de la máquina.
