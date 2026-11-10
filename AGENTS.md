# AGENTS.md

factory-novo es una "fábrica" para agentes de codificación. Tiene dos capas:

- un **harness**: instrucciones, estado, verificación, alcance y ciclo de vida;
- un **motor de loops** en Python (`factory`) que orquesta Claude Code en modo headless con roles maker/checker separados.

Requiere Python ≥ 3.12. El paquete vive en `src/factory/` y los tests en `tests/`.

El objetivo de una sesión no es producir más código, sino dejar el repositorio en un estado que la siguiente sesión pueda continuar sin adivinar.

## Comandos

- Arranque (entorno + verificación de referencia; solo si falta `.venv` o el doctor falla): `./init.sh`
- Verificación completa (lint, formato, tests y auditoría del harness): `./scripts/check.sh`
- Puerta previa a un pull request (árbol limpio, commits sobre la base, verificación, tamaño, complejidad y CodeRabbit en local): `./scripts/pre-pr.sh [base]`
- Auditoría del harness: `.venv/bin/factory doctor`
- Features: `.venv/bin/factory features list | start <id> | verify <id>`
- Equipo ideal (plantilla y convocatoria sugerida): `.venv/bin/factory team list | validate | lineup`
- Complejidad ciclomática por función: `.venv/bin/factory complexity [rutas] [--base REF] [--max N]`
- Recomendaciones de los revisores de un PR: `.venv/bin/factory feedback <pr> [--revisor <login>]`

## Inicio de sesión

1. Lee de `progress.md` solo "Estado verificado actual" y la última entrada de sesión (el resto vive en `docs/historial/`).
2. Ejecuta `.venv/bin/factory features list` y elige la feature `in_progress` o, si no hay, la de mayor prioridad sin terminar.
3. Ejecuta `.venv/bin/factory doctor`. Corre `./init.sh` solo si falta `.venv` o el doctor falla; si la referencia está rota, arréglala antes de empezar trabajo nuevo.

El directorio de trabajo y los commits recientes ya vienen en el contexto de la sesión. `./scripts/check.sh` completo corre antes de cerrar y antes de un PR, no al empezar.

## Restricciones duras

- **WIP=1**: solo una feature en `in_progress`. Actívala con `factory features start <id>`.
- **Nunca edites a mano `status` ni `evidence`** de `feature_list.json`. Solo `factory features verify <id>` promueve a `passing`, y solo si la verificación pasa.
- **No debilites, borres ni omitas tests** para que algo pase. Si un test es incorrecto, documéntalo en `progress.md` y pide revisión.
- **Push y PRs solo cuando el usuario los pide en la sesión.** El merge es una decisión humana: nunca sin una petición explícita.
- **No cambies las reglas de verificación** (`scripts/check.sh` y la configuración de ruff/pytest) sin una petición explícita.
- **No uses modos que omiten permisos** (`bypassPermissions`, `--dangerously-skip-permissions`).
- **Consulta a los expertos antes de proponer.** Un enfoque, un arreglo o un hallazgo que no sea evidente desde el código se contrasta contra la biblioteca técnica (`factory brain search "<consulta en inglés>"`) y se **cita** (`Libro · cap. N · pp. A–B`), sin copiar su texto. Si no hay nada aplicable, se dice. Mandan `AGENTS.md`, `docs/harness/` y `openspec/specs/` sobre cualquier nota que los contradiga; la contradicción se anota (`docs/harness/cerebros.md`).
- **Respeta el alcance** de la feature activa. Un arreglo de soporte solo se permite si bloquea, y debe quedar anotado.

## Definición de terminado

Una feature está terminada solo si se cumple todo lo siguiente:

- el comportamiento está implementado y cubierto por tests;
- `./scripts/check.sh` termina en 0;
- `factory features verify <id>` la promovió a `passing` con evidencia;
- la revisión independiente (subagente `checker`) no deja hallazgos `critical` ni `medium` abiertos;
- si el trabajo va a un pull request, `./scripts/pre-pr.sh` termina en 0 **antes** de abrirlo;
- `progress.md` registra lo hecho, la verificación ejecutada y el siguiente paso.

## Cierre de sesión

Sigue la [lista de clean state](docs/harness/clean-state-checklist.md):

1. `./scripts/check.sh` en verde. Si no lo está, documenta el fallo como riesgo en `progress.md`.
2. Actualiza `progress.md`, y también `session-handoff.md` si la sesión fue larga.
3. Comprueba que el estado de las features refleja la realidad.
4. No dejes nada a medio hacer sin documentar.

## Documentos temáticos

Léelos solo cuando la tarea lo requiera:

- [Cifra](docs/harness/cifra.md): servicios Go de cifra: feature-flags, recorrido contra el servicio, apertura y límite de PRs.
- [Verificación](docs/harness/verificacion.md): qué ejecuta `check.sh`, cómo leer un fallo y las capas de verificación.
- [Features](docs/harness/features.md): formato de `feature_list.json`, máquina de estados y evidencia.
- [Sesiones](docs/harness/sesiones.md): inicio, cierre, handoff y clean state.
- [Roles](docs/harness/roles.md): separación maker/checker, cuándo pedir revisión independiente y permisos por rol.
- [Loops](docs/harness/loops.md): `goal.md`, `factory goal run`, anti-patrones y seguridad.
- [Observabilidad](docs/harness/observabilidad.md): estado de cada ejecución, bandeja y costes silenciosos.
- [Intake](docs/harness/intake.md): triaje de peticiones, borradores y `factory goal promote`.
- [Recomendaciones](docs/harness/recomendaciones.md): `factory feedback` y la skill `recomendaciones`, para atender los hilos de los revisores de un pull request.
- [Cerebros](docs/harness/cerebros.md): cerebro principal (libros, fuera de git) y diario; `factory brain …`.
- [Equipo](docs/harness/equipo.md): el equipo ideal de sub-agentes (técnico, jugadores y árbitro); `/equipo` y `factory team …`.
- [Cambios OpenSpec](openspec/changes/): requisitos y tareas del cambio en curso.

## Estructura

- `src/factory/`: paquete y CLI `factory`.
- `tests/`: pytest; `conftest.py` tiene utilidades para crear repos git temporales.
- `init.sh` y `scripts/check.sh`: rutas estándar de arranque y verificación.
- `scripts/pre-pr.sh` y `.coderabbit.yaml`: la puerta previa a un pull request y las reglas con las que el bot revisa.
- `feature_list.json`, `progress.md` y `session-handoff.md`: estado del harness.
- `entregas/<TICKET>/`: paquetes de entrega al QA humano (briefing, escenarios y README), escritos por `entrega-qa`. Se entregan directo a QA y no van en el PR; como salen del equipo, nunca llevan secretos ni datos reales.
- `openspec/`: specs y cambios. No edites specs fuera del flujo de OpenSpec.

---
Adaptado del curso [walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) (licencia MIT).
