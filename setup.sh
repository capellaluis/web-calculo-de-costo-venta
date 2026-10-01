#!/usr/bin/env bash
# =====================================================
# MI NEGOCIO - Instalacion automatica
# Sirve para Linux, macOS y Raspberry Pi.
# Uso (desde la carpeta del proyecto):   bash setup.sh
# Es seguro ejecutarlo varias veces: no borra datos.
# =====================================================
set -euo pipefail
cd "$(dirname "$0")"

echo "=== MI NEGOCIO: instalacion ==="

# 1) Buscar Python 3.10 o superior
PY=""
for candidato in python3 python; do
  if command -v "$candidato" >/dev/null 2>&1; then
    if "$candidato" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      PY="$candidato"
      break
    fi
  fi
done
if [ -z "$PY" ]; then
  echo "ERROR: no se encontro Python 3.10 o superior."
  echo "En Debian, Ubuntu o Raspberry Pi OS ejecuta:"
  echo "  sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
  exit 1
fi
echo "[1/6] Python encontrado: $("$PY" --version)"

# 2) Entorno virtual (carpeta venv)
if [ -x venv/bin/python ]; then
  echo "[2/6] El entorno virtual ya existe."
else
  echo "[2/6] Creando el entorno virtual (venv)..."
  if ! "$PY" -m venv venv; then
    echo "ERROR: no se pudo crear el entorno virtual."
    echo "En Debian, Ubuntu o Raspberry Pi OS ejecuta:  sudo apt install -y python3-venv"
    echo "Luego borra la carpeta venv (si quedo a medias) y vuelve a ejecutar este archivo."
    exit 1
  fi
fi
VPY="venv/bin/python"

# 3) Dependencias
echo "[3/6] Instalando dependencias (pip)..."
"$VPY" -m pip install --upgrade pip
"$VPY" -m pip install -r requirements.txt

# 4) .env y carpetas
echo "[4/6] Preparando el archivo .env y las carpetas..."
"$VPY" scripts/preparar_entorno.py

# 5) Iconos y graficos (solo si faltan)
echo "[5/6] Descargando iconos y graficos (solo si faltan)..."
"$VPY" scripts/descargar_recursos.py || echo "AVISO: faltan algunos recursos. Se continua con la instalacion."

# 6) Base de datos SQLite (no borra datos si ya existe)
echo "[6/6] Creando la base de datos SQLite..."
"$VPY" database/init_db.py

echo
echo "LISTO. Para iniciar la aplicacion ejecuta:   bash iniciar.sh"
echo "Y abre en el navegador:   http://127.0.0.1:5000"
