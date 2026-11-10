# Roles: maker y checker

Un modelo que escribe código se convence de que está bien mientras lo genera. Cuando se autoevalúa, ve su propio razonamiento, no sus errores (L09, L13). Por eso quien hace el trabajo **nunca** es quien lo aprueba.

> "Alguien en tu equipo no debe creerte."

## Los dos roles

| | Maker | Checker |
|---|---|---|
| Objetivo | que funcione | encontrar problemas |
| Herramientas | leer, editar, ejecutar la verificación | solo lectura (Read, Grep, Glob) |
| Entrada | objetivo, estado, feedback | criterios + diff + resultados de verificación |
| Nunca recibe | — | el razonamiento o la transcripción del maker |
| Salida | cambios + informe (qué hizo, riesgos) | veredicto con hallazgos y evidencia |

La **decisión final** no es de ninguno de los dos. En una sesión interactiva la toma el humano. En un loop la toma el orquestador: verificación determinista en verde **y** checker sin hallazgos `critical` ni `medium`.

## En sesiones interactivas (Claude Code)

El subagente `checker` está en `.claude/agents/checker.md`. Úsalo antes de declarar terminada una feature:

1. Ejecuta `./scripts/check.sh` y guarda el resultado.
2. Invoca el subagente con:
   - los criterios: el `user_visible_behavior` y los comandos de `verification` de la feature;
   - el diff: `git diff` (y `git diff --cached` si hay cambios en el índice);
   - el resultado de la verificación;
   - desde la segunda ronda, el número de ronda, los hallazgos abiertos y el diff incremental (`git diff <sha-de-la-ronda-anterior>`).
3. **No** le pases tu razonamiento ni tu resumen de "por qué está bien".
4. Corrige los hallazgos `critical` y `medium` y repite la revisión. Los `minor` pueden quedar anotados en `progress.md`. Dos rondas como máximo; después, pregunta al usuario (`CLAUDE.md`).

Formato del veredicto:

```
## Veredicto
✅ pass / ❌ fail / ⚠️ pass_with_minor

## Hallazgos
### 1. [critical] Título
- Ubicación: archivo:línea
- Descripción: …
- Evidencia: …
- Sugerencia: …
```

Un hallazgo sin ubicación o sin evidencia no vale: pide que lo concrete.

## Las reglas de oficio

Viven en el prompt del rol al que le tocan; aquí solo se listan, para no tener el texto en dos sitios.

| Regla | Dónde |
|---|---|
| Un hallazgo corregido se cierra con una **prueba de mutación**: un test que falla al revertir el arreglo | [`prompts/checker.md`](../../prompts/checker.md) y [`.claude/agents/checker.md`](../../.claude/agents/checker.md) |
| La revisión cubre **lo que el diff no muestra**: documentación, specs o decisiones que el cambio dejó mintiendo | los mismos dos |
| Antes de afirmar que algo no existe, se comprueba contra **`origin/main`** | [`prompts/maker.md`](../../prompts/maker.md) |
| Un **supuesto es una decisión, nunca un hecho**: lo que se lee en un archivo se lee y se cita | [`prompts/maker.md`](../../prompts/maker.md) |
| **Precedencia** entre los cerebros y la documentación del repositorio | [cerebros.md](cerebros.md) |
| **Antes de proponer se mira cómo lo resolvieron los expertos**, y se cita (`Libro · cap. N · pp. A–B`) | [`prompts/maker.md`](../../prompts/maker.md) y los diez jugadores de [`.claude/agents/`](../../.claude/agents/); el `checker` queda fuera a propósito |
| **Lo que abriría un hilo en el pull request** se decide en la revisión, una vuelta antes | [`prompts/checker.md`](../../prompts/checker.md) y [`.claude/agents/checker.md`](../../.claude/agents/checker.md) |

Vienen de la fábrica `/yate`, donde cada una costó una ronda de revisión antes de escribirse.

## Señales de un checker complaciente

- Devuelve `pass` sin haber leído los archivos tocados por el diff.
- No pregunta si se debilitaron, borraron u omitieron tests.
- Repite el resumen del maker en lugar de contrastarlo con el código.

Si pasa esto, vuelve a invocarlo recordándole su checklist. En los loops se usa por defecto un modelo distinto para cada rol.

## Límites del checker

- No ejecuta comandos. La verificación determinista la ejecuta quien orquesta: tú o `factory`.
- No modifica archivos. Si `git status` cambia tras invocarlo, descarta el veredicto.
- No sustituye a la revisión humana de la rama antes de integrarla.

## Permisos por rol en los loops

En `factory goal run` cada rol se invoca con `claude -p` en una **sesión nueva**, con listas explícitas de herramientas (`--allowedTools` / `--disallowedTools`). Nunca se usa `bypassPermissions` ni `--dangerously-skip-permissions`.

| | Maker | Checker |
|---|---|---|
| `permission_mode` | `acceptEdits` | `dontAsk` (deniega lo no permitido) |
| Permitido | Read, Edit, Write, Glob, Grep, `git status`, `git diff`, `python -m pytest`, `python -m ruff`, y los comandos `run` de `acceptance` del objetivo | Read, Glob, Grep |
| Denegado | `git commit/push/reset/checkout/rebase/merge`, `gh`, editar `feature_list.json` | Edit, Write, NotebookEdit, Bash y lo mismo que el maker |
| Modelo por defecto | `sonnet` | `opus` |

Defensas que no dependen de los permisos del CLI:

- El maker trabaja en un **worktree fuera del repo** y en su propia rama. El directorio principal no se toca.
- Tras cada ronda, el orquestador revierte los cambios en rutas fuera de `scope.allow` o dentro de `scope.deny`.
- Tras cada ronda, también revierte cualquier modificación, borrado o renombrado de archivos protegidos existentes (tests, scripts de verificación, `factory.toml`, `prompts/`, `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/hooks/`, `.claude/settings.json`). Ver [loops.md](loops.md#rutas-protegidas).
- Antes y después del checker se compara el estado del árbol. Si cambió, el veredicto se descarta y la ronda falla.
  - Limitación: la huella usa `git status` y `git diff`, así que **no detecta escrituras en archivos ignorados por git**. Por eso el checker también tiene `Edit` y `Write` denegados.
- Las denegaciones de publicación de ambos roles y la restricción de solo lectura del checker son **obligatorias**: ni `factory.toml` ni `goal.md` pueden quitarlas.
- Las listas de Bash permitidas funcionan por prefijo y **no son un sandbox**. Para ejecuciones desatendidas largas, usa un contenedor o una VM (ver [loops.md](loops.md)).

Se configuran en `[roles.<rol>]` de `factory.toml`, y se pueden ajustar por objetivo con `roles:` en `goal.md`.

## Agentes interactivos

En las sesiones interactivas hay tres agentes en `.claude/agents/`. La regla de este documento no cambia: quien construye nunca aprueba.

| Agente | Herramientas | Cuándo | ¿Decide? |
|---|---|---|---|
| `ingeniero-software` | leer, editar y Bash | implementa código y tests | nunca aprueba su propio trabajo |
| `checker` | solo lectura (Read, Grep, Glob) | antes de dar por terminada una feature; ejes spec y estándares | sí: con un `critical` o un `medium` abierto, la feature no está terminada |
| `seguridad` | solo lectura (Read, Grep, Glob) | cuando el diff toca autenticación, secretos, entradas externas o permisos | sus hallazgos `critical`/`medium` devuelven el trabajo a construcción |

La verificación determinista (`./scripts/check.sh` y, si hace falta, `factory complexity`) la ejecuta la sesión principal, nunca un revisor.

---
Adaptado de walkinglabs/learn-harness-engineering (MIT), lecciones 09, 11 y 13 (prompts maker/checker).
