## MODIFIED Requirements

### Requirement: Jugadores revisores iniciales
La plantilla inicial SHALL incluir estos revisores:
- `seguridad` (#1): vulnerabilidades del diff;
- `qa` (#2): plan de pruebas y auditoría de la cobertura, incluidos los tests debilitados, borrados u omitidos;
- `revisor-pr` (#4): una rama o PR completos, propios o ajenos;
- `metricas` (#5): el informe de complejidad;
- `producto` (#6): preguntas y respuestas, criterios y matriz petición→diff.

"Inicial" es la plantilla con la que se integró `add-equipo-ideal`: describe el punto de partida, no un tope. Los fichajes posteriores ocupan dorsales libres y se rigen por el requisito "Fichajes posteriores".

#### Scenario: Plantilla inicial completa
- **WHEN** se ejecuta `factory team list` sobre la plantilla con la que se integró `add-equipo-ideal`
- **THEN** aparecen el técnico, los siete jugadores en sus dorsales y los dorsales 7, 8, 10 y 11 como vacantes

#### Scenario: La plantilla crece con un fichaje
- **WHEN** se añade `.claude/agents/arquitecto-api.md` con `dorsal: 10` y se ejecuta `factory team list`
- **THEN** la mediapunta deja de ser una vacante, el fichaje aparece en su puesto y las vacantes que se informan son las que quedan libres

### Requirement: Jugadores constructores iniciales
La plantilla inicial SHALL incluir dos constructores:
- `ingeniero-software` (#9): implementa siguiendo AGENTS.md, sin editar `status` ni `evidence`, sin debilitar tests y dentro del alcance;
- `documentador` (#3): actualiza solo documentación (`*.md`).

Los dorsales que ningún agente declara SHALL informarse como vacantes, con perfiles sugeridos en `docs/harness/equipo.md`. La lista de vacantes vive en ese documento y en la salida de `factory team list`, no en esta spec.

#### Scenario: El documentador no toca código
- **WHEN** el `documentador` recibe un diff que cambia un subcomando del CLI
- **THEN** actualiza la documentación afectada y no modifica ningún archivo fuera de `*.md`

## ADDED Requirements

### Requirement: Fichajes posteriores
Un fichaje SHALL añadir un único archivo `.claude/agents/<name>.md` con un `dorsal` libre de 1 a 11 y el frontmatter completo (`name`, `description` en una línea con `(#<dorsal>)`, `tools`, `model`, `dorsal`, `tipo` y `convocatoria`). Un revisor MUST declarar `tools` dentro de `Read, Grep, Glob` y responder con el formato común, empezando por `## Jugador: <name> (#<dorsal>)` y con exactamente una línea de veredicto.

El fichaje MUST traer su propio test (`tests/test_team_<name>.py`) y dejar coherentes las cuatro superficies que lo nombran: `README.md`, `docs/harness/equipo.md` (plantilla, formación, vacantes y costes), `.claude/skills/equipo/SKILL.md` (vacantes y coste) y `docs/harness/roles.md` (enumeración por tipo). Un fichaje MUST NOT aceptarse sin `factory team validate` en 0.

#### Scenario: Fichaje con un dorsal ya ocupado
- **WHEN** un agente nuevo declara un `dorsal` que ya usa otro jugador
- **THEN** `factory team validate` falla y el fichaje no se acepta

#### Scenario: El fichaje deja una superficie mintiendo
- **WHEN** se ficha a un jugador y `README.md` sigue contando su dorsal entre las vacantes
- **THEN** es un hallazgo de revisión, y el test del jugador falla al revertir la corrección
