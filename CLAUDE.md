@AGENTS.md

## Notas para Claude Code

- **Revisión independiente.** Antes de declarar terminada una feature, invoca el subagente `checker` (`.claude/agents/checker.md`), pasándole solo el diff, los criterios de la feature y el resultado de `./scripts/check.sh` que ejecutas tú. Desde la segunda ronda, añade el número de ronda, los hallazgos abiertos y el diff incremental.
  - Corrige los hallazgos `critical` y `medium`. **Dos rondas como máximo**: si la segunda aún deja `critical` o `medium`, para y pregunta al usuario en lugar de abrir una tercera.
- **Trabajo largo o desatendido.** Usa el motor de loops de `factory` en lugar de encadenar prompts a mano (`docs/harness/loops.md`).
- **Agentes.** `ingeniero-software` construye, `checker` revisa (ejes spec y estándares) y `seguridad` se pide cuando el diff toca autenticación, secretos, entradas externas o permisos.
- **Cambio pequeño:** ver «Definición de terminado» en `AGENTS.md` (sin `feature_list.json`, OpenSpec ni `checker`).
- **Tamaño de un PR.** 10 archivos y 500 líneas de código y tests como máximo; la documentación no cuenta, y un archivo borrado entero cuenta como archivo pero suma 0 líneas. Lo mide `./scripts/pre-pr.sh` y el corte se decide **antes** de escribir. Si no cabe, PRs apilados, cada uno desplegable por sí solo.
- **Antes de abrir un PR.** `./scripts/pre-pr.sh [base]` termina en 0 antes de abrirlo: verificación, tamaño, complejidad y CodeRabbit en local.
  - **Dos vueltas como máximo.** Si tras la segunda siguen abriéndose hilos, para: el problema es el corte del PR o una regla que falta en `.coderabbit.yaml`, no el hilo. Arréglalo ahí y deja la nota con `factory brain learn`.
- **Servicios Go de cifra** (rutas nuevas, feature-flags, abrir PRs, `entregas/`): antes del primer `Edit` o del primer PR en un repo cifra, lee `docs/harness/cifra.md`.
- **Cierre de sesión.** Sigue la lista de `AGENTS.md`; no termines con `./scripts/check.sh` en rojo sin documentarlo en `progress.md`.
- **OpenSpec.** Los comandos `/opsx:*` gestionan las specs y los cambios de `openspec/`. Solo comandos: si `openspec update` vuelve a crear `.claude/skills/openspec-*`, bórralas (la configuración global tiene `delivery: both`).
