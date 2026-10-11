# Gestión de Dependencias

**Versiones fijadas** en `requirements.txt` para reproducibilidad y seguridad en local y producción.

## Instalación

### Desarrollo local (localhost / 127.0.0.1)

```bash
pip install -r requirements-dev.txt
pytest
python servidor.py
```

Accesible en `http://localhost:5000` — no hay restricciones de versión.

### Producción (Raspberry Pi / servidor)

```bash
pip install -r requirements.txt
python servidor.py
```

**Las versiones exactas garantizan que el código que pasó tests locales funcionará idénticamente en prod.**

## Actualizar una dependencia

### 1. Agregar nuevo paquete

En `requirements.txt`, agregar línea:
```
paquete==X.Y.Z
```

Luego instalar y verificar:
```bash
pip install -r requirements.txt
pytest
```

### 2. Actualizar versión existente

Detectar cambios de seguridad:
```bash
pip-audit
```

Si hay CVE en un paquete, actualizar:
```
# En requirements.txt, cambiar:
paquete==X.Y.Z  →  paquete==X.Y.(Z+1)
```

Luego:
```bash
pip install -r requirements.txt
pytest
python servidor.py  # Test manual
```

### 3. Actualizar dependencias transitivas

Si cambias Flask (por ejemplo), sus transitividades pueden cambiar.
Obtener todas versiones:
```bash
pip install -r requirements.txt
pip freeze | sort > /tmp/freeze.txt
```

Verificar cambios en `/tmp/freeze.txt` — agregar explícitamente cualquier nueva transitiva en `requirements.txt`.

## Compatibilidad local/producción

- **Python**: 3.10+ (especificado en `setup.sh` / `setup.bat`)
- **Versiones**: idénticas entre local y prod
- **Servidor**: `waitress==3.0.2` en ambos (app factory en `servidor.py`)
- **Base de datos**: SQLite, sin dependencias de BD

**No hay configuración especial por entorno.** La app lee `.env` para `APP_DEBUG`, `APP_HOST`, `APP_PORT`, pero las versiones no cambian.

## Seguridad

Revisar regularmente CVEs en dependencias:
```bash
# ⚠️ Dentro del venv, especificar Python del venv para auditar correctamente
PIPAPI_PYTHON_LOCATION=$(which python) pip-audit

# O usar el módulo directamente
python -m pip_audit

# Esperado: "Found 0 known vulnerabilities in 0 packages"
```

**Nota:** `pip-audit` sin configuración audita pip global, no el venv. Las CVEs en `pip 25.2` (global) NO afectan nuestras dependencias. Mantener pip actualizado (`pip install --upgrade pip`).

Fijar versiones previene:
- Cambios incompatibles en dependencias secundarias
- Desviación entre local y prod
- Upgrades inesperados cuando reinstalando
- CVEs en transitividades desconocidas

## Archivo de bloqueo (futuro)

Cuando crezca, considerar `pip-tools`:
```bash
pip install pip-tools
pip-compile requirements.in  # Genera requirements.txt con hashes
```
