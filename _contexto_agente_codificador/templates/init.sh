#!/usr/bin/env bash
# init.sh — Inicialización y verificación del entorno del repo activo
#
# Plantilla canónica. Origen: _contexto_agente_codificador/templates/init.sh
# Se genera (copia) en cada repo de producto si no existe todavía.
# template-version: 1
#
# Flujo único, en este orden:
#   1) SCAFFOLD  — crea la estructura mínima ausente. Idempotente: NUNCA
#                  sobrescribe un archivo existente.
#   2) CHECK     — verifica entorno, archivos base, backlog y tests (solo
#                  lectura). Si CHECK falla, la sesión no debe avanzar.
#
# Por eso es seguro ejecutarlo tanto al COMENZAR una sesión como antes de
# declarar una tarea `done`: si todo existe, el scaffold es un no-op.
#
# Salida: bloques [NEW]/[OK]/[WARN]/[FAIL] y exit code (0 = entorno listo).

set -u

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
new()  { printf "${BLUE}[NEW]${NC}   %s\n" "$1"; }
warn() { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }
fail() { printf "${RED}[FAIL]${NC}  %s\n" "$1"; }

EXIT_CODE=0
NEW_COUNT=0
TEMPLATE_VERSION=1

# create_if_absent <ruta>   (contenido por stdin/heredoc)
# Crea el archivo solo si no existe. Si ya existe, descarta el heredoc y sigue.
create_if_absent() {
  local path="$1"
  if [ -e "$path" ]; then
    cat >/dev/null   # consume el heredoc para no contaminar stdin
    return 0
  fi
  mkdir -p "$(dirname "$path")"
  cat > "$path"
  new "creado $path"
  NEW_COUNT=$((NEW_COUNT + 1))
}

echo "── 0. Aviso de versión de plantilla ────────────────────"
CTX="${AGENTS_CONTEXT_DIR:-../_contexto_agente_codificador}"
if [ -f "$CTX/templates/init.sh" ]; then
  CENTRAL_V=$(grep -m1 'template-version:' "$CTX/templates/init.sh" | grep -oE '[0-9]+' | head -1 || true)
  if [ -n "${CENTRAL_V:-}" ] && [ "$CENTRAL_V" -gt "$TEMPLATE_VERSION" ] 2>/dev/null; then
    warn "Plantilla desactualizada: local v$TEMPLATE_VERSION < central v$CENTRAL_V. Regenérala desde $CTX/templates/init.sh"
  else
    ok "Plantilla init.sh al día (v$TEMPLATE_VERSION)"
  fi
else
  ok "Sin contexto global accesible; se omite el aviso de versión"
fi

echo ""
echo "── 1. Scaffold: estructura mínima (AGENTS.md §3.6) ─────"

create_if_absent tests/.gitkeep <<'EOF'
EOF

create_if_absent docs/architecture.md <<'EOF'
# Arquitectura

> Visión general del sistema: componentes, límites y flujos de datos.
> Rellena esta plantilla con la arquitectura real del repo.
EOF

create_if_absent docs/conventions.md <<'EOF'
# Convenciones

> Estilo de código, naming, estructura de carpetas y reglas locales.
EOF

create_if_absent docs/verification.md <<'EOF'
# Verificación

> Cómo se valida el repo. init.sh autodetecta el runner de tests, pero puedes
> fijarlo explícitamente descomentando la línea siguiente:
>
> test-command: <comando de tests del repo>
EOF

create_if_absent progress/Current.md <<'EOF'
# Tarea actual

- **Estado:** sin tarea activa
- **Hecho:**
- **Pendiente:**
- **Última verificación:**
- **Siguiente paso:**
EOF

create_if_absent progress/History.md <<'EOF'
# Histórico

> Bitácora cronológica de hitos cerrados (append).
EOF

create_if_absent progress/Decisions.md <<'EOF'
# Decisiones

> Qué se decidió, por qué y qué alternativas se descartaron (append).
EOF

create_if_absent progress/Blockers.md <<'EOF'
# Bloqueos

> Impedimentos abiertos o resueltos, con fecha.
EOF

if [ "$NEW_COUNT" -eq 0 ]; then
  ok "Estructura ya presente, nada que crear"
else
  ok "Estructura creada ($NEW_COUNT archivos nuevos)"
fi

echo ""
echo "── 2. Check: archivos base ─────────────────────────────"
for f in AGENTS.md docs/architecture.md docs/conventions.md docs/verification.md \
         progress/Current.md progress/History.md progress/Decisions.md progress/Blockers.md; do
  if [ -f "$f" ]; then
    ok "Existe $f"
  else
    fail "Falta archivo base: $f"
    EXIT_CODE=1
  fi
done

echo ""
echo "── 3. Check: backlog ───────────────────────────────────"
# Canónico: task.md / tasks.md (Markdown). feature_list.json se valida si existe.
if [ -f feature_list.json ] && command -v python3 >/dev/null 2>&1; then
  if python3 - <<'PY'
import json, sys
try:
    data = json.load(open("feature_list.json"))
    valid = {"pending", "in_progress", "done", "blocked"}
    feats = data.get("features", [])
    in_prog = [f for f in feats if f.get("status") == "in_progress"]
    if len(in_prog) > 1:
        print(f"[FAIL]  {len(in_prog)} features en in_progress (máximo 1)"); sys.exit(1)
    for f in feats:
        if f.get("status") not in valid:
            print(f"[FAIL]  Estado inválido en {f.get('id','?')}: {f.get('status')}"); sys.exit(1)
    print(f"[OK]    feature_list.json válido ({len(feats)} features)")
except Exception as e:
    print(f"[FAIL]  feature_list.json inválido: {e}"); sys.exit(1)
PY
  then :; else EXIT_CODE=1; fi
elif [ -f task.md ] || [ -f tasks.md ]; then
  ok "Backlog Markdown presente (task.md/tasks.md)"
else
  warn "Sin backlog (task.md/tasks.md/feature_list.json); repo sin tareas estructuradas"
fi

echo ""
echo "── 4. Check: tests (runner autodetectado) ──────────────"
TEST_CMD=""
# 4a. Comando explícito en docs/verification.md
if [ -f docs/verification.md ]; then
  EXPLICIT=$(grep -m1 -E '^[[:space:]>]*test-command:' docs/verification.md | sed -E 's/^[[:space:]>]*test-command:[[:space:]]*//' || true)
  case "$EXPLICIT" in
    ""|"<comando de tests del repo>") : ;;
    *) TEST_CMD="$EXPLICIT" ;;
  esac
fi
# 4b. Autodetección por tipo de repo
if [ -z "$TEST_CMD" ]; then
  if command -v pytest >/dev/null 2>&1 && ls tests/test_*.py tests/*_test.py >/dev/null 2>&1; then
    TEST_CMD="pytest -q"
  elif [ -d tests ] && command -v python3 >/dev/null 2>&1 && ls tests/*.py >/dev/null 2>&1; then
    TEST_CMD="python3 -m unittest discover -s tests"
  elif [ -f package.json ] && grep -q '"test"' package.json; then
    TEST_CMD="npm test"
  elif command -v go >/dev/null 2>&1 && ls ./*_test.go >/dev/null 2>&1; then
    TEST_CMD="go test ./..."
  fi
fi
if [ -n "$TEST_CMD" ]; then
  echo "    runner: $TEST_CMD"
  if eval "$TEST_CMD"; then
    ok "Todos los tests pasan"
  else
    fail "Hay tests rotos"
    EXIT_CODE=1
  fi
else
  warn "No hay tests detectables todavía"
fi

echo ""
echo "── 5. Resumen ──────────────────────────────────────────"
if [ "$EXIT_CODE" -eq 0 ]; then
  ok "Entorno listo. Puedes empezar a trabajar."
else
  fail "Entorno NO está listo. Resuelve los errores antes de avanzar."
fi
exit $EXIT_CODE
