#!/usr/bin/env bash
set -euo pipefail

# scripts/setup_dev.sh
# Automatiza la preparación del entorno de desarrollo para Protonox + Kivy

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$REPO_ROOT"

echo "==> Preparando entorno de desarrollo Protonox (Kivy)"

# 1) Verificar Python
PY=$(command -v python || true)
if [ -z "$PY" ]; then
  echo "Python no encontrado en PATH. Instala Python 3.12 y vuelve a ejecutar." >&2
  exit 1
fi

echo "Using Python: $($PY --version 2>&1)"

# 2) Crear virtualenv si no existe
if [ ! -d .venv ]; then
  echo "Creating venv .venv"
  python -m venv .venv
fi

# 3) Activar
source .venv/bin/activate
python -m pip install --upgrade pip build setuptools wheel

# 4) Instalar en editable
echo "==> Installing protonox package in editable mode"
pip install -e .

# 5) Instalar protonox-kivy fork
if [ -d ./kivy-protonox-version ]; then
  echo "==> Installing protonox-kivy (local)"
  pip install -e ./kivy-protonox-version
else
  echo "Aviso: ./kivy-protonox-version no existe; salta instalación local de Kivy fork"
fi

# 6) Install requirements if present
if [ -f requirements.txt ]; then
  pip install -r requirements.txt || true
fi

# 7) Run quick checks
echo "==> Verifying installation"
python - <<PYCODE
import sys
try:
    import kivy
    print('Kivy:', kivy.__version__, 'at', kivy.__file__)
except Exception as e:
    print('Warning: kivy import failed:', e)
    sys.exit(1)

print('\nRun `python3 run_tests.py` to execute project tests')
PYCODE

echo "Done. Activate with: source .venv/bin/activate"