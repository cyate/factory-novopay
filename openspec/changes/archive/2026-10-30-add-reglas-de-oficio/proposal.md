## Why

La fábrica `/yate` (una skill del mismo autor, para servicios Go) lleva meses acumulando reglas que aquí no existen, y cada una se pagó con una ronda de revisión perdida. Cinco de ellas no dependen del lenguaje ni del framework: son reglas de oficio sobre cómo se cierra un hallazgo, qué mira una revisión, cuándo se afirma que algo no existe, qué cuenta como hecho y qué fuente manda cuando dos se contradicen.

Este harness ya tiene los roles (maker, checker, intake, equipo) y los cerebros, pero sus prompts no piden ninguna de las cinco cosas. Dos ejemplos de esta misma semana: el `checker` aceptó un arreglo sin ninguna prueba que fallara si alguien lo revertía, y nadie vio que archivar `add-panel` dejaba a `docs/harness/panel.md` apuntando a un directorio que ya no existe — un defecto que ningún revisor de diff puede ver, porque el archivo que miente no está en el diff.

## What Changes

- **Mutación que cierra el hallazgo.** El veredicto del checker deja de aceptar un arreglo sin la prueba que lo defiende: romper el arreglo a propósito debe hacer fallar un test. Un arreglo sin eso es una opinión con commit.
- **Checklist de lo que el diff no muestra.** El checker y la lista de cierre de sesión preguntan por lo que el diff deja mintiendo: documentación, specs o decisiones escritas que el cambio volvió falsas, y caminos que quedaron inalcanzables.
- **Leer contra `origin/main`.** Antes de afirmar que algo no está construido, se comprueba donde vive la verdad y no en el checkout, que puede estar decenas de commits atrás o en otra rama.
- **Un supuesto es una decisión, nunca un hecho.** Lo que se puede leer en un archivo se lee y se cita. Solo es supuesto lo que nadie ha decidido todavía.
- **Precedencia de fuentes.** Queda escrito qué manda cuando los cerebros y `docs/harness/` no coinciden, y qué hacer con la discrepancia en vez de elegir en silencio.

No cambia ningún comportamiento ejecutable: es texto en los prompts de los roles, en el subagente `checker` y en la documentación del harness, más los requisitos que lo fijan.

## Capabilities

### New Capabilities

Ninguna. Las cinco reglas modifican contratos de roles que ya existen.

### Modified Capabilities

- `maker-checker-loop`: el veredicto del checker exige la prueba de mutación de cada hallazgo corregido y una revisión de lo que el diff no muestra; el maker debe comprobar contra `origin/main` antes de afirmar que algo no existe.
- `request-intake`: la decisión del intake separa lo contado de lo supuesto, y solo puede llamar supuesto a lo que nadie ha decidido.
- `brain-retrieval`: queda fijada la precedencia entre los cerebros y la documentación del harness, y qué hacer cuando se contradicen.
- `agent-harness`: la lista de cierre de sesión incluye la comprobación de lo que el cambio dejó mintiendo.

## Impact

- `prompts/checker.md`, `prompts/maker.md` y `prompts/intake.md`: los tres roles del motor de loops.
- `.claude/agents/checker.md`: el mismo árbitro en sesión interactiva, que hoy no comparte texto con `prompts/checker.md`.
- `docs/harness/revision.md`, `docs/harness/roles.md`, `docs/harness/cerebros.md` y `docs/harness/clean-state-checklist.md`.
- Sin cambios en el código de `src/factory/`, en `scripts/check.sh` ni en la configuración de ruff o pytest. Sí cambian las copias empaquetadas `src/factory/templates/prompts/{maker,checker,intake}.md`, que `tests/test_templates.py` obliga a mantener idénticas a las de `prompts/` y que `engine.load_prompt` usa como respaldo. Los tests existentes que comprueban la forma del veredicto no se tocan: el esquema JSON no cambia.
- Riesgo de alcance: `team-match` define revisores propios (`qa`, `revisor-pr`, `seguridad`) que también emiten hallazgos. Este cambio **no** los toca; la regla llega a ellos por el árbitro `checker`, que el reglamento ya declara obligatorio.
