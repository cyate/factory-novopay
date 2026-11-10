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
  - OpenSpec: solo los comandos `/opsx:*`; fuera las skills `openspec-*`. Configuración global de OpenSpec en `delivery: commands` (`openspec config set delivery commands`), así que `openspec update` ya no las vuelve a crear, tampoco en los repos cifra.
  - `factory.toml` solo con lo que difiere de los valores por defecto.
  - Fuera del repo: memorias de cifra a la memoria del proyecto `cifra-spend-corporate-api-go`; `diagramas/`, `pendiente-diario/`, `task/` y el cuestionario a `~/NOVOPAYMENT/cifra-spend/notas-desde-factory-novo/`.
- Fuera de este repositorio (configuración del usuario), jbcontext retirado entero:
  - `~/.claude/settings.json`: fuera los hooks `jbcontext hook pre-tool-use`, `hook user-prompt-submit` y los dos `index --silent` (inicio y fin de sesión). Quedan `rtk hook claude` y `gobricks-check.sh`.
  - `~/.claude/CLAUDE.md`: la búsqueda de código va floorplan → grep; fuera el paso de jbcontext y los marcadores `jbcontext-instructions`.
  - Borrado el agente global `~/.claude/agents/context-explorer.md` (dependía del MCP de jbcontext, que fallaba al conectar).
  - Motivo: el MCP no conectaba, el agente se invocó 0 veces y el hook inyectó su consejo más de 1.000 veces en las sesiones medidas.
- Checker: dos rondas sobre los commits de esta sesión. Ronda 1 `fail` (1 `critical`: se había borrado la comprobación de integridad de `security-audit`, recuperada en `tests/test_security_audit_copia.py`); ronda 2 `pass_with_minor`, minor corregidos en `376575f`.
- Verificación ejecutada: `./scripts/check.sh` → código 0, 431 tests en ~9 s.
- Riesgos / pendientes: siguen sin commitear en `main` el paso "ajustes del bot" de `scripts/pre-pr.sh`, tres notas nuevas de `brain-diario/` y `tests/test_openspec_deltas.py` (trabajo del usuario).
- Mejor próximo paso: usar el harness ligero en trabajo real y medir otra retro.
