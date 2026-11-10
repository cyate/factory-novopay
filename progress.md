# Registro de progreso

## Estado verificado actual

- Raíz del repositorio: `factory-novo/`, la que contiene `AGENTS.md`.
- Arranque: `.venv/bin/factory doctor` (`./init.sh` solo si falta `.venv` o el doctor falla).
- Verificación estándar: `./scripts/check.sh` (antes de cerrar y antes de un PR).
- OpenSpec: specs principales en `openspec/specs/`. Cambios archivados y activos: ver `openspec/changes/`.
- Feature activa / siguiente: ver `.venv/bin/factory features list`.
- Commits: ver `git log`. HEAD de la última sesión verificada: ver la sesión 025.
- Bloqueos actuales: el push de `main` es una decisión humana pendiente.
- Historial de sesiones 001 a 024: `docs/historial/progress-sesiones.md`.

## Registro de sesiones

### Sesión 025 — 2026-11-10 (equipo, OpenSpec y limpieza)

- Objetivo: decisiones 9, 10, 7, 8 y 12 de la retro.
- Completado:
  - Cambio pequeño (menos de 3 archivos, sin capacidad nueva): `check.sh` en verde y commit, sin `feature_list.json`, OpenSpec ni `checker` (`AGENTS.md`, `CLAUDE.md`).
  - Fuera la regla de delegar a partir de 3 archivos (también de la memoria).
  - De 11 agentes a 3: `ingeniero-software`, `checker` (ejes spec y estándares) y `seguridad`. `product-owner` y `entrega-qa` pasan a `~/.claude/agents/`. Fuera `/equipo`, `docs/harness/equipo.md`, los `test_team_*` y las features `team-*`; `tests/test_agentes.py` comprueba el frontmatter.
  - OpenSpec: solo los comandos `/opsx:*`; fuera las skills `openspec-*` (la configuración global de OpenSpec sigue en `delivery: both`).
  - `factory.toml` solo con lo que difiere de los valores por defecto.
  - Fuera del repo: memorias de cifra a la memoria del proyecto `cifra-spend-corporate-api-go`; `diagramas/`, `pendiente-diario/`, `task/` y el cuestionario a `~/NOVOPAYMENT/cifra-spend/notas-desde-factory-novo/`.
- Verificación ejecutada: `./scripts/check.sh` → código 0, 427 tests en ~10 s.
- Riesgos / pendientes: siguen sin commitear en `main` el paso "ajustes del bot" de `scripts/pre-pr.sh`, tres notas nuevas de `brain-diario/` y `tests/test_openspec_deltas.py` (trabajo del usuario).
- Mejor próximo paso: usar el harness ligero en trabajo real y medir otra retro.
