@echo off
rem =====================================================
rem MI NEGOCIO - Instalacion automatica para Windows
rem Uso: doble clic en este archivo (o ejecutarlo desde CMD).
rem Es seguro ejecutarlo varias veces: no borra datos.
rem =====================================================
setlocal
cd /d "%~dp0"

echo === MI NEGOCIO: instalacion ===

rem 1) Buscar Python 3.10 o superior
set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if not defined PY goto sin_python

%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if errorlevel 1 goto sin_python

echo [1/6] Python encontrado:
%PY% --version

rem 2) Entorno virtual (carpeta venv)
if exist venv\Scripts\python.exe (
  echo [2/6] El entorno virtual ya existe.
) else (
  echo [2/6] Creando el entorno virtual - venv ...
  %PY% -m venv venv
  if errorlevel 1 goto error
)
set "VPY=venv\Scripts\python.exe"

rem 3) Dependencias
echo [3/6] Instalando dependencias - pip ...
%VPY% -m pip install --upgrade pip
if errorlevel 1 goto error
%VPY% -m pip install -r requirements.txt
if errorlevel 1 goto error

rem 4) .env y carpetas
echo [4/6] Preparando el archivo .env y las carpetas...
%VPY% scripts\preparar_entorno.py
if errorlevel 1 goto error

rem 5) Iconos y graficos (solo si faltan)
echo [5/6] Descargando iconos y graficos - solo si faltan ...
%VPY% scripts\descargar_recursos.py
if errorlevel 1 echo AVISO: faltan algunos recursos. Se continua con la instalacion.

rem 6) Base de datos SQLite (no borra datos si ya existe)
echo [6/6] Creando la base de datos SQLite...
%VPY% database\init_db.py
if errorlevel 1 goto error

echo.
echo LISTO. Para iniciar la aplicacion haz doble clic en iniciar.bat
echo y abre en el navegador: http://127.0.0.1:5000
if not "%~1"=="auto" pause
exit /b 0

:sin_python
echo.
echo ERROR: no se encontro Python 3.10 o superior.
echo Descargalo desde https://www.python.org/downloads/ y durante la instalacion
echo marca la casilla "Add python.exe to PATH". Luego ejecuta este archivo otra vez.
if not "%~1"=="auto" pause
exit /b 1

:error
echo.
echo ERROR: algo fallo en el paso anterior. Lee el mensaje que aparece arriba.
if not "%~1"=="auto" pause
exit /b 1
