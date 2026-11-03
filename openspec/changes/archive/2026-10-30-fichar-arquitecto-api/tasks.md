# Tasks

> El fichaje sigue el procedimiento de `docs/harness/equipo.md` ("Cómo fichar"). No se toca `src/factory/`, ni `scripts/check.sh`, ni la configuración de ruff o pytest.

## 1. El jugador

- [x] 1.1 Buscar en el cerebro principal (en inglés) el conocimiento de las cuatro áreas y quedarse con las citas, no con el texto.
- [x] 1.2 Escribir `.claude/agents/arquitecto-api.md` con el frontmatter D8 (dorsal 10, `tipo: revisor`, `tools: Read, Grep, Glob`, `model: opus`, convocatoria por rutas) y el formato común de revisor.
- [x] 1.3 `factory team validate` en 0 y `factory team list` con el fichaje en la mediapunta.
- [x] 1.4 Prueba real barata con haiku (`--max-budget-usd 0.05`), comprobando que `git status --porcelain` no cambia.

## 2. Documentación

- [x] 2.1 `docs/harness/equipo.md`: fila de la plantilla, formación, lista de vacantes y costes.
- [x] 2.2 `.claude/skills/equipo/SKILL.md`: regla de ampliación, línea de vacantes y sección "Coste".
- [x] 2.3 `README.md`: fila del dorsal 10 y línea de vacantes.
- [x] 2.4 `docs/harness/roles.md`: enumeración de los jugadores revisores.

## 3. Tests

- [x] 3.1 `tests/test_team_arquitecto_api.py`: frontmatter, solo lectura, las cuatro áreas, biblioteca citada, gravedad, formato y coherencia con `equipo.md`.
- [x] 3.2 Anclar las superficies que podrían quedar mintiendo: `README.md`, `SKILL.md` (vacantes y coste) y `roles.md`.
- [x] 3.3 Comprobar con `factory.globs.matches` que los globs de OpenAPI casan a cualquier profundidad.
- [x] 3.4 `tests/test_team_tecnico.py`: `arquitecto-api` en `JUGADORES` y fuera de `VACANTES`.

## 4. Spec

- [x] 4.1 Delta de `team-match`: acotar la plantilla inicial, soltar el MUST de las vacantes y añadir el requisito de los fichajes posteriores.
- [x] 4.2 `openspec validate fichar-arquitecto-api --strict` y `./scripts/check.sh` en 0.
