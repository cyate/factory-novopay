# Registro de progreso

## Estado verificado actual

- Raíz del repositorio: `factory-novo/`, la que contiene `AGENTS.md`.
- Arranque: `.venv/bin/factory doctor` (`./init.sh` solo si falta `.venv` o el doctor falla).
- Verificación estándar: `./scripts/check.sh` (antes de cerrar y antes de un PR).
- OpenSpec: specs principales en `openspec/specs/`. Cambios archivados y activos: ver `openspec/changes/`.
- Feature activa / siguiente: ver `.venv/bin/factory features list`.
- Commits: ver `git log`. HEAD de la última sesión verificada: ver la sesión 024.
- Bloqueos actuales: el push de `main` es una decisión humana pendiente.
- Historial de sesiones 001 a 022: `docs/historial/progress-sesiones.md`.

## Registro de sesiones

### Sesión 023 — 2026-11-10 (retro: simplificar las reglas)

- Objetivo: una retro midió que ~48 % del tiempo de sesión se iba en ceremonia del harness. Solo documentación.
- Completado:
  - `checker.md`: regla de re-revisión (desde la segunda ronda solo lo abierto y el diff nuevo) y número mágico sin nombre baja a `minor`.
  - `revisor-pr.md`: límite de tamaño a 500 líneas, igual que `CLAUDE.md` y `scripts/pre-pr.sh`.
  - `docs/harness/cifra.md` nuevo: reglas de los servicios Go de cifra, sacadas de `CLAUDE.md`.
  - `CLAUDE.md` corto; `AGENTS.md` con inicio de sesión ligero y permisos de push/PR aclarados; `sesiones.md` apunta a `AGENTS.md`.
  - `progress.md` recortado: sesiones 001 a 022 movidas a `docs/historial/progress-sesiones.md`.
  - Ronda 1 del `checker` (7 `medium`): re-revisión que no rebaja los `critical` de regla dura; el checker recibe ronda, hallazgos abiertos y diff incremental (`checker.md`, `CLAUDE.md`, `roles.md`); push/PR alineados en `tecnico.md` y la skill `recomendaciones`; vuelve «PRs apilados, cada uno desplegable»; `entregas/` va directo a QA (`AGENTS.md`, `recomendaciones.md`); alcance de `cifra.md` unificado a «repo cifra».
  - Ronda 2: `fail` solo formal (prueba de mutación exigida a prosa). Decisión del usuario: la prueba de mutación aplica al código, no a la prosa; del 1 al 6 se cierran, y el 7 y los `minor` A–E se corrigen sin tercera ronda.
- Verificación ejecutada: `PYTHONPATH=src ./scripts/check.sh` en el worktree → código 0, «Verificación completa: OK» (`PYTHONPATH` para que los tests usen el `src` del worktree y no el editable del árbol principal).
- Bloque 2 (guardrails):
  - `scripts/pre-pr.sh`: sin CodeRabbit, o si la revisión no se completa, avisa y sigue (`PRE_PR_STRICT=1` lo mantiene como fallo; salida 2 sigue cerrando); se borra el paso "recorrido" y `PRE_PR_SIN_RECORRIDO`.
  - `pyproject.toml`: `pythonpath = ["src"]` (ya no hace falta `PYTHONPATH`), `pytest-xdist` y `-n auto`; suite de 108 s a ~21 s en `check.sh`; `pythonpath` solo arregla los imports de pytest: `doctor`, `complexity` y los tests con subprocesos en un worktree siguen usando el `.venv` editable compartido, así que un worktree que cambia `src/` necesita su propio `.venv`.
  - Hooks versionados `scripts/hooks/{pre-commit,pre-push}` y `init.sh` fija `core.hooksPath`.
  - `tests/test_reglas_de_oficio.py` sin los tests que fijaban frases de Markdown; la prueba de mutación aplica a código y tests, no a documentación (prompts del checker y spec `maker-checker-loop`).
  - `entregas/` va directo a QA (README, `test_team_entrega_qa.py`, `cifra.md`, `recomendaciones.md`); plantillas `AGENTS.md`/`CLAUDE.md` alineadas.
  - Ronda 1 del `checker`: `tests/test_pre_pr.py` ejecuta `pre-pr.sh` real (salidas 0/2/1 de CodeRabbit, CLI ausente, `PRE_PR_STRICT`); la puerta ignora `entregas/` sin trackear; `commit_daily` usa `--no-verify` (con test de hook que falla); checklists y README ya no dicen «los agentes no hacen push».
  - Verificación: `./scripts/check.sh` sin `PYTHONPATH` → código 0, 880 tests en 18 s (antes 108 s en un solo proceso).
- Riesgo: se retiraron por decisión del usuario los tests de frases en `.md` (fijaban redacción, no comportamiento); `reglas-de-oficio` sigue `passing` con esa cobertura reducida. `puerta-pre-pr` está `not_started` y su `verification` solo corre `tests/test_reglas_de_oficio.py`: falta añadir `tests/test_pre_pr.py` antes de promoverla (no cabe en este PR: sería el archivo 11 de código).
- Riesgos / pendientes: ninguno más.
- Mejor próximo paso: PRs de borrado (panel, autonomía, strands, roster; ≤10 archivos/500 líneas cada uno) y decisiones 9–10 (circuito ligero para cambios pequeños, regla de delegar a partir de 3 archivos).

### Sesión 024 — 2026-11-10 (borrado de lo que no se usa)

- Objetivo: borrar los subsistemas sin uso real que midió la retro (panel, capa de autonomía, código del equipo, capturas e inyección del cerebro) en PRs de ≤10 archivos y ≤500 líneas. Regla nueva: un archivo borrado entero cuenta como archivo y 0 líneas.
- Commits (rama `chore/borrar-ceremonia`, sobre `bc89acf`):
  - `d0b87df` pre-pr: borrado entero = 1 archivo, 0 líneas, y se imprime aparte (`tests/test_pre_pr.py`, `CLAUDE.md`).
  - `4edf66b` panel: servidor, snapshot, página y `factory panel`.
  - `59c0abb` panel: tokens, pull requests, revisiones y tareas.
  - `62f13dd` panel: hooks, `factory hook`, `panel-hook.sh` y `.claude/settings.json` (solo tenía esos hooks).
  - `6b10c59` `factory status`.
  - `ef21f74` `factory tick`.
  - `3c380b6` `factory land`, `schedule`, `goal promote`, `goal rework`.
  - `4f0ea55` `factory intake`, peticiones (`requests.py`) y borradores; `slugify` pasa a `brain/text.py`.
  - `5cfee37` `factory inbox` (el módulo `inbox.py` se queda: el motor lo escribe).
  - `5c7486c` config `[tick]`/`[alerts]`, rol `intake`, su prompt y su esquema.
  - `fd25e69` `factory team` y `src/factory/team/` (el chequeo `team-roster` de doctor se va con él).
  - `07b3672` capturas e inyección (`brain pending|accept|reject`); el motor ya no inyecta conocimiento ni propone capturas.
  - Este commit: clave `[brain] inject_max_tokens` y esta entrada.
- Specs borradas (subsistema entero): `team-roster`, `team-match`, `observability-panel`, `review-hooks`, `token-usage`, `request-intake`, `scheduled-loop`, `run-landing`. Docs borrados: `panel.md`, `vigilancia.md`, `intake.md`, `revision.md`; `observabilidad.md`, `loops.md`, `equipo.md`, `cerebros.md` y el README recortados.
- Código de src+tests: 22 130 → 12 699 líneas. Suite: 880 tests en ~16,9 s → 519 tests en ~7,6 s.
- Verificación: `./scripts/check.sh` → 0 y `./scripts/pre-pr.sh <commit anterior>` → «Puerta abierta» en cada commit (CodeRabbit no corrió: sin sesión en este entorno).
- Se conserva a propósito: `inbox.py` y `engine.py` (congelados; el motor escribe la bandeja y mantiene el soporte de retrabajo `parent`/`answer`, que ya no tiene comando), el parseo de `knowledge` en `goal.md` (se acepta e ignora), `mode: monitor` (se rechaza con mensaje), `.claude/agents/*.md` y la skill `/equipo` (la skill aún nombra `factory team list|lineup`, que ya no existen), `feature_list.json` (sus entradas de panel/intake/team citan tests borrados; no se editan a mano) y `src/factory/templates/AGENTS.md`.
- Mejor próximo paso: decisiones 9–10; el trabajo de strands sin commitear en `main` se descarta (respaldo en `respaldo/wip-2026-11-10`).
