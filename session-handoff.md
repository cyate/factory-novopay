# Handoff de sesión

> Plantilla de entrega compacta. Se sobrescribe en cada handoff; el historial vive en `progress.md` y en git.
> Úsala cuando la sesión fue larga o cuando otra persona o agente continúa el trabajo.

Última actualización: sesión 014 — 2026-10-30, sobre `fbdf206` más el trabajo sin commitear de las sesiones 009 a 014.

## Verificado ahora

- Qué funciona actualmente: 31 de 32 features están en `passing`; `puerta-pre-pr` (32) está en `not_started`, con el cambio OpenSpec `add-puerta-pre-pr` escrito y la verificación en verde. La puerta `./scripts/pre-pr.sh` corre antes de abrir un pull request lo mismo que correrá el revisor, y `.coderabbit.yaml` lleva las reglas con las que el bot revisa este repositorio. El panel tiene una cuarta pestaña, **Pull requests**: los que abrió el usuario y aquellos en los que se le pidió revisión, con estado, checks, tamaño, tiempos (abierto, sin actividad, hasta la primera revisión humana y de ciclo) y alertas accionables, sondeados con `gh` cada 60 s y servidos por el mismo canal SSE; `factory panel --no-pulls` apaga la red y un fixture `autouse` impide que ningún test salga a ella. Antes de eso, las 29 features y, tras archivar `fichar-arquitecto-api` y `fichar-entrega-qa`, no queda ningún cambio activo de OpenSpec. El equipo ideal tiene nueve jugadores y quedan dos vacantes (8 y 11): la mediapunta la ocupa `arquitecto-api` (#10), revisor de APIs, seguridad de la frontera, concurrencia y AWS; el extremo derecho, `entrega-qa` (#7), constructor que prepara el paquete para el QA humano en `entregas/<TICKET>/` y el briefing del plan de desarrollo para Cowork design. `factory panel` sirve la página, `/api/snapshot` y `/api/stream`, y el hook registra en vivo las revisiones del `checker` con su veredicto y sus severidades.
- Qué verificación se ejecutó realmente (comando → resultado):
  - `./scripts/check.sh` → 0, varias veces durante la sesión 014 y la última tras cerrar la tercera vuelta del `checker`.
  - `python -m pytest -q tests/test_reglas_de_oficio.py` → 46 passed.
  - `./scripts/pre-pr.sh main` con el árbol sucio → 1, «PUERTA CERRADA: hay cambios sin commitear».
  - `factory brain import /Users/cyate/obsidianGeneral/novopayment-software` → 11.245 notas, 82 libros, ~13.016.603 tokens.
  - De sesiones anteriores, sin repetir aquí: `./init.sh` → 0, `openspec archive add-panel --yes` y `git push origin main` → `b70d745..fbdf206`.

## Cambiado en esta sesión

- Código o comportamiento añadido: la 014 añadió `scripts/pre-pr.sh` (la puerta previa al pull request) y `.coderabbit.yaml` (las reglas con las que el bot revisa este repositorio), más la consulta obligatoria a la biblioteca en los doce contratos de rol —el `checker` queda fuera a propósito— y el cambio OpenSpec `add-puerta-pre-pr`. Antes, la 012 añadió `src/factory/panel/pulls.py` y la 013 `src/factory/feedback.py`. La 011 fichó a `arquitecto-api` (#10): `.claude/agents/arquitecto-api.md` (revisor de solo lectura, opus, convocatoria por rutas), `tests/test_team_arquitecto_api.py` (15 casos), el cambio OpenSpec `fichar-arquitecto-api` archivado (dos requisitos de `team-match` modificados y uno nuevo, "Fichajes posteriores") y la feature `team-arquitecto-api` en `passing`. Su conocimiento son 21 citas del cerebro principal, sin copiar texto. Tres vueltas de `checker`: 3 `medium` + 5 `minor`, luego 1 `medium` + 1 `minor`, y `pass` al final. La 009 cerró `add-panel` 5.3 y lo archivó; la 010 añadió `add-reglas-de-oficio`: cinco reglas de oficio en los prompts de `maker`, `checker` e `intake`, en el subagente `checker` y en `docs/harness/`, con `tests/test_reglas_de_oficio.py`, que entonces tenía 11 casos y hoy tiene 46, y la feature `reglas-de-oficio` en `passing`.
- Cambios de infraestructura o de harness:
  - specs nuevas en `openspec/specs/`: `observability-panel` (7 requisitos), `review-hooks` (6) y `token-usage` (6). El repo pasa de 15 a 18 capacidades, actualizado en `README.md` y en `progress.md`.
  - `docs/harness/panel.md` ya no apunta a `openspec/changes/add-panel`, sino a las specs y al directorio del archivo.

## Roto o sin verificar

- Defecto conocido: un `minor` abierto a propósito. `./scripts/pre-pr.sh` avisa pero no cierra cuando el pull request se pasa de 10 archivos o 600 líneas, porque los archivos estáticos pueden pasarse y contarlos aparte es una decisión pendiente (`progress.md`, sesión 014). La revisión independiente del `checker` terminó en `pass_with_minor` tras tres vueltas, sin `critical` ni `medium`.
- Ruta sin verificar: los temas claro y oscuro y el ancho de móvil del panel no se volvieron a mirar en esta sesión; son criterio de la tarea 4.5, cerrada en la sesión 008.
- Riesgo para la próxima sesión: este clon no tiene `.factory/runs/`, así que la pestaña Tokens no muestra loops y el `events.jsonl` de la revisión del paso 5.2 se perdió. Se verá en cuanto corra aquí un `factory goal run`. Las cifras de tokens de la sesión 008 se midieron en otro equipo, con otro `$HOME`, y no son reproducibles en este.
- Riesgo cerrado: el puntero de `principal_dir` a un vault de Obsidian por ruta absoluta se revirtió. En ese modo, `factory brain import <otro-vault>` habría borrado el vault apuntado (`importer.py:140-144`); lo encontró `revisor-pr` en la tanda paralela de la sesión 010.

## Mejor próximo paso

- Feature sin terminar de mayor prioridad: `puerta-pre-pr` (32), en `not_started`: el trabajo está hecho y verificado, falta `factory features start puerta-pre-pr` y `factory features verify puerta-pre-pr`. Después, cambios nuevos en este orden propuesto: el equipo dentro de `factory goal run` (fase 2), fichar las dos vacantes que quedan (8 `bibliotecario`, 11 `experiencia-cli`) y refactorizar la deuda de complejidad (`parse_intake` 35, `parse_goal_text` 32, `cmd_brain` 30, `render_loop_state` 30).
- Por qué es la siguiente: la fase 2 es la que convierte el equipo ideal, hoy solo interactivo, en parte del motor de loops; las otras dos son deuda ya medida.
- Qué cuenta como aprobado (comandos): `./scripts/check.sh` en 0, `factory features verify <id>` con la feature en `passing`, y el `checker` sin hallazgos `critical` ni `medium`.
- Qué no debe cambiar durante ese paso: `scripts/check.sh` y la configuración de ruff y pytest, `feature_list.json` a mano (ni `status` ni `evidence`), `prompts/**` y `tests/**` (protegidos en `factory.toml`).

## Comandos

- Arranque: `./init.sh`
- Verificación: `./scripts/check.sh`
- Depuración enfocada: `.venv/bin/factory features list`, `.venv/bin/factory doctor`, `.venv/bin/factory complexity src/factory --max 20`, `.venv/bin/factory panel --port <libre> --open`
