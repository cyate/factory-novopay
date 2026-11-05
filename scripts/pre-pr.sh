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
[ -z "$(git status --porcelain)" ] || fallo "hay cambios sin commitear: lo que no está en un commit no llega al PR y esta puerta no lo mediría."
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
while IFS=$'\t' read -r mas menos ruta; do
  [ -n "${ruta:-}" ] || continue
  # Un binario llega como "-" en las dos columnas; cuenta como archivo y cero líneas.
  [ "$mas" = "-" ] && mas=0
  [ "$menos" = "-" ] && menos=0
  if es_documentacion "$ruta"; then
    DOC_ARCHIVOS=$((DOC_ARCHIVOS + 1))
    DOC_LINEAS=$((DOC_LINEAS + mas + menos))
  else
    ARCHIVOS=$((ARCHIVOS + 1))
    LINEAS=$((LINEAS + mas + menos))
  fi
done < <(git diff --numstat "$BASE"...HEAD)
echo "==> [tamaño] código y tests: ${ARCHIVOS} archivos, ${LINEAS} líneas (límite ${MAX_ARCHIVOS}/${MAX_LINEAS})"
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

# 6. El recorrido contra el servicio arrancado. Un test en proceso prueba el enrutado y la
#    forma de la respuesta; no prueba que el binario arranque, lea su configuración y
#    conteste. Dos defectos de la pila de usuarios —un 500 en la primera página y un campo
#    que no se podía vaciar— pasaron por suites verdes y solo cayeron al levantar el
#    servicio. Aquí se comprueba lo único comprobable desde fuera: que el PR que construye
#    una ruta trae también su recorrido, que es lo que `AGENTS.md` pide en `entregas/`.
RUTAS=$(git diff --name-only "$BASE"...HEAD | grep -cE '(handlers?/|routes?\.go|module\.go)$' || true)
RECORRIDO=$(git diff --name-only "$BASE"...HEAD | grep -cE '^entregas/' || true)
if [ "${RUTAS:-0}" -gt 0 ] && [ "${RECORRIDO:-0}" -eq 0 ]; then
  echo "" >&2
  echo "    Este PR toca ${RUTAS} archivo(s) de rutas y no trae nada en entregas/." >&2
  echo "    Levanta el servicio, ejercítalo y guarda la petición y la respuesta de cada" >&2
  echo "    escenario; esa evidencia es la que convierte la rebanada en terminada." >&2
  echo "    Si de verdad no aplica, PRE_PR_SIN_RECORRIDO=1 lo salta y deja dicho por qué." >&2
  [ "${PRE_PR_SIN_RECORRIDO:-0}" = "1" ] || fallo "hay rutas construidas sin recorrido contra el servicio arrancado."
  echo "==> [recorrido] saltado por PRE_PR_SIN_RECORRIDO=1" >&2
elif [ "${RUTAS:-0}" -gt 0 ]; then
  echo "==> [recorrido] ${RUTAS} archivo(s) de rutas, con evidencia en entregas/"
else
  echo "==> [recorrido] el PR no construye rutas; no hay recorrido que exigir"
fi

echo "==> Puerta abierta: el PR se puede publicar."
