@echo off
rem MI NEGOCIO - Inicia la aplicacion en Windows.
rem Uso: doble clic en este archivo. Para apagarla: Ctrl + C
setlocal
cd /d "%~dp0"

if not exist venv\Scripts\python.exe goto instalar
if not exist database\negocio.db goto instalar
goto iniciar

:instalar
echo Primero hay que instalar el proyecto. Ejecutando setup.bat...
call setup.bat auto
if errorlevel 1 (
  pause
  exit /b 1
)

:iniciar
echo Iniciando MI NEGOCIO... para apagar: Ctrl + C
venv\Scripts\python.exe servidor.py
pause
