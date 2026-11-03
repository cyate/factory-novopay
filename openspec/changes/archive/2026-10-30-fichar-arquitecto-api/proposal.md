## Why

La plantilla del equipo ideal nació con siete jugadores y cuatro dorsales libres (7, 8, 10 y 11), y la spec `team-match` fijó esa foto con un MUST: "Los dorsales 7, 8, 10 y 11 MUST quedar vacantes". Era cierto el día que se integró `add-equipo-ideal`, pero deja de serlo en cuanto se ficha a alguien — y fichar es justo lo que el procedimiento de `docs/harness/equipo.md` invita a hacer ("fichar es añadir un archivo y dar de baja es borrarlo").

La necesidad concreta: el equipo no tiene a nadie que mire el **diseño de una frontera** — el contrato de una API, su seguridad, la concurrencia contra servicios externos y bases de datos, y lo que AWS da o quita por configuración. `seguridad` (#1) busca vulnerabilidades explotables en el diff; nadie juzga si el diseño aguanta. El conocimiento para hacerlo ya está en el cerebro principal (82 libros), pero ningún agente lo lleva puesto.

Este cambio ficha a `arquitecto-api` en el dorsal 10 (mediapunta) y, con él, arregla la spec: la plantilla inicial es una foto de partida, no una prohibición permanente.

## What Changes

- **Nuevo jugador `arquitecto-api` (#10)**, revisor de solo lectura con `model: opus`: contrato de la API, seguridad de la frontera, concurrencia e integraciones, y AWS y plataforma. Su conocimiento viene del cerebro principal **citado** (libro · capítulo · páginas), nunca copiado.
- **La spec deja de congelar las vacantes.** El requisito de los constructores ya no exige que 7, 8, 10 y 11 queden vacíos: la lista viva de vacantes pasa a `docs/harness/equipo.md` y a `factory team list`, y el escenario de la plantilla inicial se ata a la integración de `add-equipo-ideal`.
- **Un fichaje tiene requisitos.** Queda escrito qué debe cumplir cualquier fichaje posterior: dorsal libre, frontmatter D8 válido, formato común de revisor, test propio y las cuatro superficies que no pueden quedar mintiendo (`README.md`, `docs/harness/equipo.md`, `.claude/skills/equipo/SKILL.md` y `docs/harness/roles.md`).

No cambia ningún comportamiento ejecutable de `src/factory/`: el motor ya leía la plantilla desde los archivos de `.claude/agents/`.

## Impact

- Specs: `team-match` (dos requisitos modificados, uno añadido).
- Código: ninguno. `factory team validate|list|lineup` ya soportaban 11 dorsales.
- Archivos: `.claude/agents/arquitecto-api.md` (nuevo), `tests/test_team_arquitecto_api.py` (nuevo), `docs/harness/equipo.md`, `docs/harness/roles.md`, `.claude/skills/equipo/SKILL.md`, `README.md`, `tests/test_team_tecnico.py`.
- Coste: una invocación de opus más cuando el técnico lo convoque; la convocatoria por rutas lo deja fuera de los partidos que no tocan su especialidad.
