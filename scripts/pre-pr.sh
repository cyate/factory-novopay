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
MAX_LINEAS=500

fallo() {
  echo "" >&2
  echo "PUERTA CERRADA: $1" >&2
  exit 1
}

# Documentación: todo lo que se lee sin ejecutarse. No cuenta para el límite porque
# añadir un escenario, un ejemplo de Postman o una página de spec no alarga la revisión
# del comportamiento, que es lo que el límite protege.
es_documentacion() {
  case "$1" in
    *.md | *.txt | *.http) return 0 ;;
    openspec/* | docs/* | notes/* | entregas/* | testdata/* | diagramas/*) return 0 ;;
    *postman*) return 0 ;;
    *.openapi.yaml | *.openapi.yml | *openapi*.yaml | *openapi*.yml) return 0 ;;
    *) return 1 ;;
  esac
}

echo "==> [base] $BASE"
git rev-parse --verify --quiet "$BASE" >/dev/null || fallo "la rama base '$BASE' no existe aquí."

# Tamaño y complejidad se miden sobre "$BASE"...HEAD, o sea sobre lo commiteado. Con el árbol
# sucio o con el rango vacío la puerta se abriría sin haber mirado una sola línea del cambio.
[ -z "$(git status --porcelain -- . ':(exclude)entregas')" ] || fallo "hay cambios sin commitear: lo que no está en un commit no llega al PR y esta puerta no lo mediría."
COMMITS=$(git rev-list --count "$BASE"..HEAD)
[ "$COMMITS" -gt 0 ] || fallo "no hay ningún commit por encima de '$BASE': no hay PR que medir."
echo "==> [rango] $COMMITS commit(s) por encima de $BASE"

# 1. La verificación del repositorio. Si está en rojo, no hay nada que revisar.
echo "==> [verificación] ./scripts/check.sh"
./scripts/check.sh || fallo "./scripts/check.sh no termina en 0."

# 2. Tamaño del PR, medido sobre lo que una persona tiene que leer para revisarlo.
#    El límite cuenta código y tests. La documentación —specs, contrato, Postman, el
#    paquete de QA, los datos de prueba— no cuenta: crece sin que la revisión se alargue.
#    Y aquí se cierra la puerta, porque avisar no evitó ningún PR de sesenta archivos.
ARCHIVOS=0
LINEAS=0
DOC_ARCHIVOS=0
DOC_LINEAS=0
BORRADOS=0
# Un archivo borrado entero cuenta como archivo pero suma 0 líneas: no hay nada que leer en él,
# solo comprobar que sobra. Las ediciones cuentan siempre por sus líneas.
ELIMINADOS="$(git diff --no-renames --diff-filter=D --name-only "$BASE"...HEAD)"
while IFS=$'\t' read -r mas menos ruta; do
  [ -n "${ruta:-}" ] || continue
  # Un binario llega como "-" en las dos columnas; cuenta como archivo y cero líneas.
  [ "$mas" = "-" ] && mas=0
  [ "$menos" = "-" ] && menos=0
  if ! es_documentacion "$ruta" && [[ $'\n'"$ELIMINADOS"$'\n' == *$'\n'"$ruta"$'\n'* ]]; then
    BORRADOS=$((BORRADOS + 1))
    mas=0
    menos=0
  fi
  if es_documentacion "$ruta"; then
    DOC_ARCHIVOS=$((DOC_ARCHIVOS + 1))
    DOC_LINEAS=$((DOC_LINEAS + mas + menos))
  else
    ARCHIVOS=$((ARCHIVOS + 1))
    LINEAS=$((LINEAS + mas + menos))
  fi
done < <(git diff --no-renames --numstat "$BASE"...HEAD)
echo "==> [tamaño] código y tests: ${ARCHIVOS} archivos, ${LINEAS} líneas (límite ${MAX_ARCHIVOS}/${MAX_LINEAS}); borrados enteros: ${BORRADOS} (cuentan como archivo, 0 líneas)"
echo "    documentación (sin límite): ${DOC_ARCHIVOS} archivos, ${DOC_LINEAS} líneas"
if [ "$ARCHIVOS" -gt "$MAX_ARCHIVOS" ] || [ "$LINEAS" -gt "$MAX_LINEAS" ]; then
  echo "" >&2
  echo "    Lo que se pasa es código y tests, que es lo que alguien tiene que leer entero." >&2
  echo "    Pártelo en PRs apilados, cada uno desplegable por sí solo (CLAUDE.md)." >&2
  fallo "el PR se pasa del límite de ${MAX_ARCHIVOS} archivos o ${MAX_LINEAS} líneas de código y tests."
fi

# 3. Complejidad ciclomática de lo que cambió. Sin --max el informe sale siempre en 0: el
#    umbral es lo que convierte este paso en una comprobación.
MAX_COMPLEJIDAD="${PRE_PR_MAX_COMPLEJIDAD:-20}"
echo "==> [complejidad] factory complexity --base $BASE --max $MAX_COMPLEJIDAD"
.venv/bin/factory complexity --base "$BASE" --max "$MAX_COMPLEJIDAD" \
  || fallo "hay funciones nuevas o empeoradas por encima de $MAX_COMPLEJIDAD de complejidad ciclomática."

# 4. La revisión de CodeRabbit, en local. --gate major termina en 2 si queda algo
#    de severidad major o superior: eso es exactamente un hilo abierto en el PR.
# Sin CodeRabbit, o si la revisión no llega a completarse, la puerta avisa y sigue;
# PRE_PR_STRICT=1 mantiene ambos casos como fallo.
if ! command -v coderabbit >/dev/null 2>&1; then
  [ "${PRE_PR_STRICT:-0}" = "1" ] && fallo "coderabbit no está instalado y PRE_PR_STRICT=1 no permite saltarlo."
  echo "==> [coderabbit] AVISO: no instalado; se salta. Instálalo o usa PRE_PR_STRICT=1." >&2
  SIN_CODERABBIT=1
else
  echo "==> [coderabbit] coderabbit review --base $BASE --gate major"
  coderabbit review --base "$BASE" --gate major
  case $? in
    0) ;;
    2) fallo "CodeRabbit deja hallazgos 'major' o peores. Arréglalos aquí, no en el PR." ;;
    *)
      [ "${PRE_PR_STRICT:-0}" = "1" ] && fallo "la revisión de CodeRabbit no pudo completarse (sesión, red o cuota)."
      echo "==> [coderabbit] AVISO: la revisión no pudo completarse (sesión, red o cuota)." >&2
      SIN_CODERABBIT=1
      ;;
  esac
fi

[ "${SIN_CODERABBIT:-0}" = "1" ] && echo "==> Puerta abierta SIN la revisión de CodeRabbit." >&2
echo "==> Puerta abierta: el PR se puede publicar."
