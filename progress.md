# Registro de progreso

## Estado verificado actual

- Raíz del repositorio: `factory-novo/`, la que contiene `AGENTS.md`.
- Arranque: `.venv/bin/factory doctor` (`./init.sh` solo si falta `.venv` o el doctor falla).
- Verificación estándar: `./scripts/check.sh` (antes de cerrar y antes de un PR).
- OpenSpec: specs principales en `openspec/specs/`. Cambios archivados y activos: ver `openspec/changes/`.
- Feature activa / siguiente: ver `.venv/bin/factory features list`.
- Commits: ver `git log`. HEAD de la última sesión verificada: `dd4222f`.
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
- Riesgos / pendientes: `scripts/pre-pr.sh` (paso "recorrido") sigue exigiendo `entregas/` en el diff, y `README.md` dice que `entregas/` «se versionan» (lo fija `tests/test_team_entrega_qa.py`); `src/factory/templates/{AGENTS,CLAUDE}.md` siguen con las reglas viejas.
- Mejor próximo paso: PR 2: guardrails (pre-commit, pre-push, pytest-xdist); PR 3: borrar panel, autonomía, strands y roster.
