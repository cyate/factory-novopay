# Tasks

> Fichaje según "Cómo fichar" de `docs/harness/equipo.md`, pasos 1 a 6. No se toca `src/factory/`, ni `scripts/check.sh`, ni la configuración de ruff o pytest.

## 1. El jugador

- [x] 1.1 `.claude/agents/entrega-qa.md` con el frontmatter D8 (dorsal 7, `tipo: constructor`, sin `Agent` ni `Bash`, `model: sonnet`, convocatoria `entregas/**`).
- [x] 1.2 Definir el paquete: briefing, escenarios y README, con el plan de Cowork aparte.
- [x] 1.3 Reglas duras: solo escribe en `entregas/<TICKET>/`, nada de secretos, nada sin anclar en `archivo:línea`.
- [x] 1.4 `factory team validate` en 0 y `factory team list` con el fichaje en el extremo derecho.
- [x] 1.5 Prueba real barata con haiku (paso 3 de "Cómo fichar"), ejecutada después de archivar: con `--permission-mode dontAsk` los tres `Write` quedaron en `permission_denials` y no escribió nada — ese modo solo sirve para revisores. Repetida con `--permission-mode acceptEdits` (`--max-budget-usd 0.10`, 0,0163 USD): escribió los tres archivos de `entregas/DEMO-001/` y nada fuera. El procedimiento de `docs/harness/equipo.md` se corrigió para distinguir los dos tipos.

## 2. Las cuatro superficies

- [x] 2.1 `docs/harness/equipo.md`: fila, formación, vacantes (ahora 8 y 11), perfiles sugeridos y costes.
- [x] 2.2 `.claude/skills/equipo/SKILL.md`: regla de ampliación, línea de vacantes y sección "Coste".
- [x] 2.3 `README.md`: fila del dorsal 7 y línea de vacantes.
- [x] 2.4 `docs/harness/roles.md`: enumeración de constructores y el terreno de cada uno.

## 3. Tests

- [x] 3.1 `tests/test_team_entrega_qa.py`: frontmatter, herramientas de constructor, el paquete, el briefing, los escenarios, las reglas de secretos y anclaje, el formato y las cuatro superficies.
- [x] 3.2 `tests/test_team_tecnico.py`: `entrega-qa` en `JUGADORES` y fuera de `VACANTES`.
- [x] 3.3 Dejar los anclajes de vacantes de `tests/test_team_arquitecto_api.py` a prueba de fichajes (que el 10 no vuelva a aparecer como vacante, en vez de fijar la lista entera).

## 4. Spec

- [x] 4.1 Delta de `team-match` con el requisito "Paquete de entrega al QA humano".
- [x] 4.2 `openspec validate fichar-entrega-qa --strict` y `./scripts/check.sh` en 0.
