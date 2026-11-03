#!/usr/bin/env bash
# Puerta local antes de abrir un pull request.
#
# Corre contra el diff lo mismo que correrá el revisor del PR, pero en esta máquina y
# antes de publicar nada. Lo que se arregla aquí no llega a ser un hilo que contestar.
# Termina en 0 solo si el PR se puede abrir; en cualquier otro caso dice qué falta.
#
# Uso: ./scripts/pre-pr.sh [rama-base]    (por defecto, main)
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BASE="${1:-main}"
MAX_ARCHIVOS=10
MAX_LINEAS=600

fallo() {
  echo "" >&2
  echo "PUERTA CERRADA: $1" >&2
  exit 1
}

echo "==> [base] $BASE"
git rev-parse --verify --quiet "$BASE" >/dev/null || fallo "la rama base '$BASE' no existe aquí."

# Tamaño y complejidad se miden sobre "$BASE"...HEAD, o sea sobre lo commiteado. Con el árbol
# sucio o con el rango vacío la puerta se abriría sin haber mirado una sola línea del cambio.
[ -z "$(git status --porcelain)" ] || fallo "hay cambios sin commitear: lo que no está en un commit no llega al PR y esta puerta no lo mediría."
COMMITS=$(git rev-list --count "$BASE"..HEAD)
[ "$COMMITS" -gt 0 ] || fallo "no hay ningún commit por encima de '$BASE': no hay PR que medir."
echo "==> [rango] $COMMITS commit(s) por encima de $BASE"

# 1. La verificación del repositorio. Si está en rojo, no hay nada que revisar.
echo "==> [verificación] ./scripts/check.sh"
./scripts/check.sh || fallo "./scripts/check.sh no termina en 0."

# 2. Tamaño del PR. El corte se decide antes de escribir, así que aquí solo se avisa:
#    los archivos estáticos (specs, documentación, datos de prueba) pueden pasarse.
ARCHIVOS=$(git diff --name-only "$BASE"...HEAD | wc -l | tr -d ' ')
LINEAS=$(git diff --shortstat "$BASE"...HEAD | grep -oE '[0-9]+ (insertion|deletion)' | grep -oE '[0-9]+' | paste -sd+ - | bc)
LINEAS=${LINEAS:-0}
echo "==> [tamaño] ${ARCHIVOS} archivos, ${LINEAS} líneas (límite ${MAX_ARCHIVOS}/${MAX_LINEAS})"
if [ "$ARCHIVOS" -gt "$MAX_ARCHIVOS" ] || [ "$LINEAS" -gt "$MAX_LINEAS" ]; then
  echo "    AVISO: se pasa del límite. Di en el cuerpo del PR cuántas líneas son de archivos" >&2
  echo "    estáticos, o pártelo en PRs apilados (CLAUDE.md)." >&2
fi

# 3. Complejidad ciclomática de lo que cambió. Sin --max el informe sale siempre en 0: el
#    umbral es lo que convierte este paso en una comprobación.
MAX_COMPLEJIDAD="${PRE_PR_MAX_COMPLEJIDAD:-20}"
echo "==> [complejidad] factory complexity --base $BASE --max $MAX_COMPLEJIDAD"
.venv/bin/factory complexity --base "$BASE" --max "$MAX_COMPLEJIDAD" \
  || fallo "hay funciones nuevas o empeoradas por encima de $MAX_COMPLEJIDAD de complejidad ciclomática."

# 4. La revisión de CodeRabbit, en local. --gate major termina en 2 si queda algo
#    de severidad major o superior: eso es exactamente un hilo abierto en el PR.
if ! command -v coderabbit >/dev/null 2>&1; then
  [ "${PRE_PR_STRICT:-0}" = "1" ] && fallo "coderabbit no está instalado y PRE_PR_STRICT=1 no permite saltarlo."
  echo "==> [coderabbit] no instalado; se salta. Sin él esto no es una puerta: instálalo o usa PRE_PR_STRICT=1." >&2
  echo "==> Puerta abierta SIN la revisión de CodeRabbit."
  exit 0
fi
echo "==> [coderabbit] coderabbit review --base $BASE --gate major"
coderabbit review --base "$BASE" --gate major
case $? in
  0) ;;
  2) fallo "CodeRabbit deja hallazgos 'major' o peores. Arréglalos aquí, no en el PR." ;;
  *) fallo "la revisión de CodeRabbit no pudo completarse (sesión, red o cuota)." ;;
esac

echo "==> Puerta abierta: el PR se puede publicar."
