#!/usr/bin/env sh
set -eu

PROJECT_ROOT=$(CDPATH= cd "$(dirname "$0")" && pwd)
cd "$PROJECT_ROOT"

if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  echo "ERROR: Python no esta disponible." >&2
  exit 1
fi

echo "Proyecto: _template_repo"
echo "Python: $($PYTHON --version 2>&1)"
echo "Ejecutando tests..."

PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -m unittest discover -s tests -p "test_*.py" -v

echo "OK: verificacion completada."
