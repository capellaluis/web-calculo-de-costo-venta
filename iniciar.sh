#!/usr/bin/env bash
# MI NEGOCIO - Inicia la aplicacion.   Uso:  bash iniciar.sh
# Para apagarla: Ctrl + C
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x venv/bin/python ] || [ ! -f database/negocio.db ]; then
  echo "Primero hay que instalar el proyecto. Ejecutando setup.sh..."
  bash setup.sh
fi

echo "Iniciando MI NEGOCIO... (para apagar: Ctrl + C)"
exec venv/bin/python app.py
