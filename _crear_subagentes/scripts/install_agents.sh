#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd "$SCRIPT_DIR/.." && pwd)
CONTEXT_ROOT=$(CDPATH= cd "$PROJECT_ROOT/../_contexto_agente_codificador" && pwd)
COMMON_DIR="$CONTEXT_ROOT/agents/common"

if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  echo "ERROR: Python no esta disponible. Instala python3 y vuelve a ejecutar." >&2
  exit 1
fi

echo "Python: $($PYTHON --version 2>&1)"
OUTPUT_ROOT="$PROJECT_ROOT/output/generated_agents"

echo "Preparando salida en $OUTPUT_ROOT ..."
rm -rf "$OUTPUT_ROOT"
mkdir -p "$OUTPUT_ROOT"

echo "Generando agentes desde $COMMON_DIR ..."

"$PYTHON" "$PROJECT_ROOT/scripts/generate_agents.py" \
  --common-dir "$COMMON_DIR" \
  --output-root "$OUTPUT_ROOT"

echo
echo "Agentes generados en:"
echo "$OUTPUT_ROOT"
echo
echo "Archivos que se instalaran:"
find "$OUTPUT_ROOT" -type f | sort
echo

printf "Instalar estos agentes en ~/.claude, ~/.codex y ~/.devin? [y/N] "
read answer

case "$answer" in
  y|Y|yes|YES)
    echo "Instalando agentes en $HOME ..."
    mkdir -p "$HOME/.claude" "$HOME/.codex" "$HOME/.devin"
    cp -R "$OUTPUT_ROOT/.claude/." "$HOME/.claude/"
    cp -R "$OUTPUT_ROOT/.codex/." "$HOME/.codex/"
    cp -R "$OUTPUT_ROOT/.devin/." "$HOME/.devin/"
    echo "OK: agentes instalados."
    ;;
  *)
    echo "Instalacion cancelada. No se han modificado las carpetas de $HOME."
    echo "Puedes revisar los archivos generados en $OUTPUT_ROOT."
    exit 0
    ;;
esac

echo "OK: flujo completado."
