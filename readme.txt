=====================================================================
  MI NEGOCIO
  Sistema para administrar proveedores, compras, productos, recetas,
  costos, márgenes y reportes de un negocio de alimentos y bebidas.
=====================================================================

Aplicación web hecha con Python + Flask + SQLite. Funciona en tu propia
computadora o en una Raspberry Pi, sin hosting y sin Internet (Internet
solo se necesita la primera vez, para instalar).

ÍNDICE
  1. Requisitos
  2. Instalación rápida (recomendada)
  3. Cómo iniciar la aplicación
  4. Instalación manual, paso a paso
  5. El archivo .env (configuración)
  6. La base de datos SQLite
  7. Usar la aplicación desde el teléfono o la tablet
  8. Si ya tienes el proyecto funcionando en la Raspberry Pi
  9. Trabajar con Git y con Visual Studio Code
 10. Estructura del proyecto
 11. Problemas frecuentes y soluciones
 12. Seguridad: lo que NO se debe hacer


---------------------------------------------------------------------
1. REQUISITOS
---------------------------------------------------------------------
  - Python 3.10 o superior (se probó con 3.13).
  - Git (solo para clonar el proyecto).
  - Internet la primera vez (para descargar las librerías).

Cómo conseguir Python:
  * Windows: descárgalo de https://www.python.org/downloads/
    IMPORTANTE: en el instalador marca la casilla "Add python.exe to PATH".
    (No uses el Python de la Microsoft Store.)
  * Debian / Ubuntu / Raspberry Pi OS:
      sudo apt update
      sudo apt install -y python3 python3-venv python3-pip git
  * macOS: https://www.python.org/downloads/ o "brew install python".

Para comprobar que quedó bien instalado:
  Windows:   py --version
  Linux/Mac: python3 --version
Debe mostrar algo como "Python 3.13.5".


---------------------------------------------------------------------
2. INSTALACIÓN RÁPIDA (RECOMENDADA)
---------------------------------------------------------------------
Los scripts hacen todo solos: crean el entorno virtual, instalan las
librerías, crean el archivo .env, descargan los iconos y los gráficos
y crean la base de datos SQLite. Son seguros: se pueden ejecutar varias
veces y NO borran tus datos.

  1) Clona el proyecto (reemplaza la dirección por la de tu repositorio):

       git clone https://github.com/TU_USUARIO/mi_negocio.git
       cd mi_negocio

  2) Ejecuta el instalador:

     WINDOWS:     haz doble clic en  setup.bat
                  (o, desde la ventana CMD:   setup.bat)

     LINUX / MAC / RASPBERRY PI:
                  bash setup.sh

  3) Espera a que termine. Al final debe decir "LISTO".
     En una Raspberry Pi 3 puede tardar unos minutos.


---------------------------------------------------------------------
3. CÓMO INICIAR LA APLICACIÓN
---------------------------------------------------------------------
     WINDOWS:                 doble clic en  iniciar.bat
     LINUX / MAC / RASPBERRY: bash iniciar.sh

Luego abre el navegador y entra a:

     http://127.0.0.1:5000

Para APAGAR la aplicación: vuelve a la ventana negra (la terminal) y
presiona  Ctrl + C.  Mientras esté encendida, esa ventana queda "ocupada";
es normal. No la cierres si quieres seguir usando la aplicación.

Si todavía no ejecutaste el instalador, iniciar.bat / iniciar.sh lo
ejecutan por ti.


---------------------------------------------------------------------
4. INSTALACIÓN MANUAL, PASO A PASO
---------------------------------------------------------------------
Úsala si prefieres hacerlo a mano o si un script falla. Todos los
comandos se escriben dentro de la carpeta del proyecto (mi_negocio).

--- WINDOWS (ventana CMD o PowerShell) ---

  a) Crear el entorno virtual (una carpeta llamada "venv"):
       py -3 -m venv venv

  b) Activarlo:
       CMD:          venv\Scripts\activate.bat
       PowerShell:   venv\Scripts\Activate.ps1
     Al inicio de la línea debe aparecer (venv).
     (Si PowerShell dice que la ejecución de scripts está deshabilitada,
      usa CMD o ejecuta una sola vez:
        Set-ExecutionPolicy -Scope CurrentUser RemoteSigned )

  c) Instalar las librerías:
       python -m pip install --upgrade pip
       pip install -r requirements.txt

  d) Crear el archivo .env y las carpetas:
       python scripts\preparar_entorno.py

  e) Descargar iconos y gráficos (solo si faltan):
       python scripts\descargar_recursos.py

  f) Crear la base de datos:
       python database\init_db.py

  g) Iniciar la aplicación:
       python app.py

--- LINUX / MAC / RASPBERRY PI ---

  a) python3 -m venv venv
  b) source venv/bin/activate
  c) python -m pip install --upgrade pip
     pip install -r requirements.txt
  d) python scripts/preparar_entorno.py
  e) python scripts/descargar_recursos.py
  f) python database/init_db.py
  g) python app.py

Cada vez que abras una terminal nueva para trabajar en el proyecto
tendrás que volver a entrar a la carpeta y activar el entorno virtual
(pasos b). No hace falta repetir los demás pasos.


---------------------------------------------------------------------
5. EL ARCHIVO .env (CONFIGURACIÓN)
---------------------------------------------------------------------
El instalador crea un archivo llamado ".env" copiando ".env.example" y
generando una clave secreta nueva. Es un archivo de texto: puedes
abrirlo con el Bloc de notas o con Visual Studio Code.

  SECRET_KEY   Clave secreta de la aplicación. Se genera sola.
               Si la regeneras, se cierran las sesiones abiertas.
  APP_HOST     127.0.0.1 = solo se abre en esta computadora (recomendado
                           en Windows).
               0.0.0.0   = también se abre desde otros equipos de tu Wi-Fi
                           (úsalo en la Raspberry Pi).
  APP_PORT     Puerto. Por defecto 5000.
  APP_DEBUG    1 = recarga sola al cambiar el código (para programar).
               0 = modo normal (uso diario).

IMPORTANTE:
  - El archivo .env NUNCA se sube a Git (ya está en .gitignore).
  - Los cambios en .env se aplican al reiniciar la aplicación.
  - Con APP_DEBUG=0 las plantillas HTML se guardan en memoria: si editas
    una plantilla o el diseño, reinicia la aplicación (Ctrl + C y volver
    a iniciarla) y recarga el navegador con Ctrl + F5.
  - No uses APP_DEBUG=1 junto con APP_HOST=0.0.0.0 salvo en una red de
    total confianza: el depurador permite ejecutar código a quien lo vea.


---------------------------------------------------------------------
6. LA BASE DE DATOS SQLITE
---------------------------------------------------------------------
  - Es un solo archivo:  database/negocio.db
  - Se crea sola al ejecutar el instalador (o a mano con
    "python database/init_db.py"), a partir del plano  database/schema.sql
  - Trae cargados: 8 unidades (g, kg, ml, l, unidad, docena, paquete, caja)
    y tus 3 márgenes (30, 50 y 70), que luego se cambian desde la pantalla
    de Configuración, sin tocar código.
  - Ejecutar init_db.py de nuevo NO borra ni duplica datos.
  - La base de datos NO se sube a Git (son tus datos, no código). Cuando
    clones el proyecto en otra PC arrancará VACÍA. Para llevar tus datos:
    copia el archivo negocio.db (o una copia de seguridad de la carpeta
    backups/) a la carpeta database/ de la otra PC, con la aplicación apagada.

HACER UNA COPIA DE SEGURIDAD A MANO (con la aplicación apagada):
     Windows:   copy database\negocio.db backups\negocio_copia.db
     Linux/Mac: cp database/negocio.db backups/negocio_copia.db

RESTAURAR UNA COPIA (con la aplicación apagada):
     1) Guarda la base actual:  renombra negocio.db a negocio.db.antes_restaurar
     2) Copia la copia elegida a database/negocio.db
     3) Inicia la aplicación y comprueba que estén tus datos.

EMPEZAR DE CERO (¡CUIDADO: BORRA TODOS LOS DATOS!):
     Primero haz una copia (arriba). Después borra database/negocio.db y
     ejecuta de nuevo setup.bat / setup.sh. Se crea una base nueva y vacía.


---------------------------------------------------------------------
7. USAR LA APLICACIÓN DESDE EL TELÉFONO O LA TABLET
---------------------------------------------------------------------
  1) En el archivo .env cambia:   APP_HOST=0.0.0.0
  2) Reinicia la aplicación.
  3) Averigua la IP de la computadora que corre la aplicación:
       Windows:    ipconfig        (busca "Dirección IPv4", ej. 192.168.1.50)
       Linux/Pi:   hostname -I
  4) En el teléfono (conectado al MISMO Wi-Fi) abre:
       http://ESA-IP:5000        por ejemplo   http://192.168.1.50:5000
  5) En Windows, la primera vez aparece un aviso del Firewall: elige
     "Permitir acceso" solo en redes privadas.

La IP puede cambiar si se reinicia el router.
NO abras puertos del router ni expongas la aplicación a Internet: por
ahora no tiene inicio de sesión.


---------------------------------------------------------------------
8. SI YA TIENES EL PROYECTO FUNCIONANDO EN LA RASPBERRY PI
---------------------------------------------------------------------
Esta versión de app.py lee la configuración del archivo .env. Si la
copias a tu Raspberry Pi, hazlo así para que siga igual que antes:

  1) Entra a la carpeta y activa el entorno:
       cd ~/mi_negocio
       source venv/bin/activate
  2) Instala la librería nueva que falta (python-dotenv):
       pip install -r requirements.txt
  3) Crea el .env:
       python scripts/preparar_entorno.py
  4) Abre .env y deja:   APP_HOST=0.0.0.0
     (Si no lo haces, la aplicación solo se verá en la propia Raspberry y
      no desde el teléfono.)
  5) Inicia:   python app.py

Para uso diario en la Raspberry (arranque automático y servidor más
estable) se usará "waitress" (ya está en requirements.txt):
     venv/bin/waitress-serve --listen=0.0.0.0:5000 app:app
La configuración del servicio automático se explica en el documento
CONTEXTO_MI_NEGOCIO.md (sección de seguridad).


---------------------------------------------------------------------
9. TRABAJAR CON GIT Y CON VISUAL STUDIO CODE
---------------------------------------------------------------------
QUÉ SE SUBE A GIT: el código, las plantillas, el CSS, schema.sql,
requirements.txt, .env.example, los scripts y este README.
QUÉ NO SE SUBE (ya está en .gitignore): venv/, .env, la base de datos
(*.db), backups/, exports/ y los archivos .respaldo / .antes_*.

Si el repositorio ya tenía subido negocio.db o .env, quítalos del
seguimiento (no se borran de tu disco):
     git rm --cached database/negocio.db
     git rm --cached .env
     git commit -m "Dejar de versionar datos y secretos"
Si alguna vez subiste un .env con una clave real, cámbiala.

Flujo en una PC nueva:
     git clone <dirección>   ->   setup.bat (o bash setup.sh)   ->   iniciar

Visual Studio Code:
  1) Archivo > Abrir carpeta... y elige la carpeta mi_negocio.
  2) Instala la extensión "Python" de Microsoft.
  3) Ctrl + Shift + P > "Python: Select Interpreter" y elige el que está
     dentro de la carpeta venv (venv\Scripts\python.exe en Windows).
  4) Abre la terminal de VS Code (Ctrl + ñ) y ejecuta:  python app.py
  5) Para programar con recarga automática, pon APP_DEBUG=1 en .env
     (con APP_HOST=127.0.0.1).

Los archivos .sh se guardan con saltos de línea de Linux y los .bat con
saltos de Windows gracias al archivo .gitattributes. No lo borres.


---------------------------------------------------------------------
10. ESTRUCTURA DEL PROYECTO
---------------------------------------------------------------------
mi_negocio/
  app.py                  Arranca la aplicación (lee .env)
  requirements.txt        Librerías de Python necesarias
  .env.example            Modelo de configuración (se copia a .env)
  .env                    Tu configuración local (NO se sube a Git)
  setup.bat / setup.sh    Instaladores automáticos (Windows / Linux-Mac-Pi)
  iniciar.bat / .sh       Inician la aplicación
  README.txt              Este archivo
  database/
    schema.sql            Plano de la base de datos y datos iniciales
    init_db.py            Crea negocio.db a partir del plano
    db.py                 Conexión a la base de datos
    negocio.db            Tus datos (se crea sola; NO se sube a Git)
  routes/                 Pantallas de cada módulo (dashboard, proveedores,
                          productos, y las que se agreguen)
  services/               Lógica de negocio (cálculos)
  models/                 Reservado para el futuro
  templates/              Páginas HTML
  static/                 Diseño (css), scripts (js) e iconos
  scripts/                Herramientas de instalación
  exports/                Archivos de Excel generados
  backups/                Copias de seguridad de la base de datos


---------------------------------------------------------------------
11. PROBLEMAS FRECUENTES Y SOLUCIONES
---------------------------------------------------------------------
"Python no se encontró" / se abre la Microsoft Store (Windows)
   Instala Python desde python.org marcando "Add python.exe to PATH".
   Si sigue pasando: Configuración > Aplicaciones > Configuración
   avanzada > Alias de ejecución de aplicaciones, y desactiva los
   alias de "python.exe" y "python3.exe".

"No module named flask" (o dotenv, openpyxl)
   No está activado el entorno virtual, o no se instalaron las librerías.
   Usa iniciar.bat / iniciar.sh, o activa el venv (sección 4) y ejecuta
   "pip install -r requirements.txt".

"ensurepip is not available" / falla "python3 -m venv" (Debian, Raspberry)
   sudo apt install -y python3-venv python3-pip
   Borra la carpeta venv si quedó a medias y repite el instalador.

"externally-managed-environment" al usar pip
   Estás usando el Python del sistema. Activa primero el entorno virtual.

PowerShell: "la ejecución de scripts está deshabilitada"
   Usa CMD, o ejecuta una vez:
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

bash: "/bin/bash^M: bad interpreter" (el .sh tiene saltos de línea de Windows)
   Ejecuta:  sed -i 's/\r$//' setup.sh iniciar.sh
   (con el .gitattributes incluido no debería pasar al clonar.)

"Address already in use" / el puerto 5000 está ocupado
   Cambia APP_PORT en .env (por ejemplo 5001) y vuelve a iniciar. En
   macOS el puerto 5000 a veces lo usa el sistema: usa 5001.

"sqlite3.OperationalError: no such table"
   La base no se creó o está vacía. Ejecuta:  python database/init_db.py

Se ve sin iconos o sin gráficos
   Faltan archivos de static/. Con Internet ejecuta:
   python scripts/descargar_recursos.py
   Luego recarga el navegador con Ctrl + F5.

Cambié el diseño o una plantilla y no se ve el cambio
   Reinicia la aplicación y recarga con Ctrl + F5 (ver sección 5).

Desde el teléfono no abre
   Revisa: mismo Wi-Fi, APP_HOST=0.0.0.0 en .env, aplicación reiniciada,
   dirección con http:// y :5000, y el Firewall de Windows.

Falla la descarga de iconos/gráficos durante la instalación
   El instalador continúa. Revisa tu Internet y vuelve a ejecutarlo: solo
   descarga lo que falta.


---------------------------------------------------------------------
12. SEGURIDAD: LO QUE NO SE DEBE HACER
---------------------------------------------------------------------
  - No subir a Git el archivo .env, la base de datos ni certificados.
  - No escribir contraseñas ni claves dentro del código.
  - No exponer la aplicación a Internet (no abrir puertos del router)
    hasta que tenga inicio de sesión, protección de formularios y HTTPS.
  - No usar APP_DEBUG=1 en una red que no sea de confianza.
  - Hacer copias de seguridad de database/negocio.db y guardar al menos
    una FUERA de la computadora (otro disco o la nube).

=====================================================================
