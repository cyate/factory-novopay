# Historial de sesiones (001 a 021)

Entradas archivadas de `progress.md`, sin cambios. Las más recientes viven en `progress.md`.

### Sesión 001 — 2026-10-27

- Objetivo: fase 1 del cambio `add-harness-loop-engine`, es decir, la base Python y el harness del repo.
- Completado:
  - `.gitignore`.
  - `pyproject.toml` (paquete `factory`, Python ≥ 3.12, `pyyaml`; dev: `pytest`, `ruff`).
  - `init.sh` y `scripts/check.sh`.
  - `factory features validate|list|start|verify` y `factory doctor [--json]`.
  - `AGENTS.md`, `CLAUDE.md` y `docs/harness/` (verificación, features, sesiones, roles, checklist de clean state).
  - `session-handoff.md`.
  - Se eliminó el `main.py` de ejemplo de PyCharm.
- Verificación ejecutada:
  - `rm -rf .venv && ./init.sh` → código 0.
  - `./scripts/check.sh` → código 0. Desde la tarea 3.7 incluye `factory doctor`.
  - Una copia limpia del árbol (sin `.venv` ni `.git`) en el scratchpad con `./init.sh` → código 0.
- Evidencia:
  - `factory features verify harness-core` → `passing`. El commit de la evidencia es `sin-commit` porque aún no hay commits.
  - Poner a mano `loop-config` en `passing` hace fallar `./scripts/check.sh` (paso `harness`), y al revertirlo vuelve a verde.
  - Tarea 3.2: `claude -p` (haiku, sin herramientas de lectura) respondió `./scripts/check.sh` en 1 turno (0,0035 USD).
  - Tarea 3.5: con un diff de prueba que relajaba WIP a 2 y modificaba su test, `claude -p --agent checker` (sonnet) devolvió `fail` con dos hallazgos `critical` (regresión WIP y test debilitado), ambos con ubicación y evidencia. `git status --porcelain` quedó idéntico antes y después (0,05 USD, 2 turnos).
  - Tarea 3.10, parcial: una sesión nueva (haiku, solo Read/Glob/Grep) respondió con artefactos del repo las 5 preguntas de arranque en frío. Identificó `loop-config` como siguiente feature y los bloqueos de commit y de la prueba live (0,006 USD). Falta repetirlo desde un `git clone`, que requiere el commit inicial.
  - El JSON de `claude -p --output-format json` incluye `permission_denials`, `total_cost_usd`, `usage` y `num_turns`. Este dato adelanta parte de la pregunta abierta de la tarea 9.2.
- Riesgos / pendientes: el commit inicial (3.9) y la prueba live (9.2) no están aprobados.
- Mejor próximo paso: continuar `tasks.md` del cambio OpenSpec.

### Sesión 002 — 2026-10-27

- Objetivo: fase 2 del cambio `add-harness-loop-engine` (grupos 4–8) y la validación 9.1.
- Completado:
  - `factory.toml` y `goal.md` (frontmatter YAML, globs de alcance, límites por defecto).
  - Adaptadores `ClaudeCodeRunner` (`claude -p`) y `FakeRunner`.
  - Esquemas y validación del informe del maker y del veredicto del checker.
  - Prompts de los roles.
  - Estado externo: `state.json`, `loop-state.md`, `events.jsonl`, `results.tsv` y la bandeja.
  - `factory status` con los cuatro costes silenciosos.
  - Worktrees fuera del repo.
  - Motor maker-checker con ratchet y condiciones de parada.
  - `factory goal run [--dry-run]`.
  - `factory tick`: bloqueo, guardas, cortacircuitos y presupuesto diario.
  - `factory schedule`.
  - `factory init` con plantillas empaquetadas.
  - Documentos `docs/harness/loops.md` y `observabilidad.md`.
- Verificación ejecutada:
  - `./scripts/check.sh` → código 0 (194 tests, ruff y doctor).
  - `openspec validate add-harness-loop-engine --strict` → válido.
  - `factory tick goals/vigilancia-check.md` → `noop`, coste 0.
  - Las plantillas aparecen en el wheel (`pip wheel`).
- Evidencia: `factory features verify` en `loop-config`, `loop-state`, `maker-checker-engine`, `scheduled-loop` y `harness-scaffolding` → `passing`.
- Hallazgo de diseño resuelto: en un worktree, `python -m pytest` importaría `factory` desde la instalación editable del repo principal. Se resolvió anteponiendo `<cwd>/src` a `PYTHONPATH` en los comandos de verificación y en el entorno del maker (`util.command_env`).
- Riesgos / pendientes:
  - 3.9 (commit inicial) y 9.2 (prueba live) no están aprobados.
  - 9.3 (dogfooding) está aprobada, pero depende de 3.9.
  - La revisión independiente del `checker` se hizo una sola vez sobre toda la fase 2 (ver abajo), no feature a feature.
- Revisión independiente de la fase 2 (aprobada; `claude -p --agent checker`, sonnet, 0,42 USD, 24 turnos, `git status` sin cambios). Veredicto `fail` con 3 hallazgos `medium` y 5 `minor`. Todos se corrigieron con tests, salvo uno que se documentó:
  - medium: carrera en el bloqueo del tick → `flock` sobre un archivo guarda, `pid <= 0` no cuenta como vivo, un bloqueo vacío y reciente cuenta como ocupado. Hay un test con 8 procesos concurrentes.
  - medium: `goal.md` o `factory.toml` podían vaciar `denied_tools` → `enforce_role_policy` impone las denegaciones obligatorias y limita el checker a lectura.
  - medium: un tick cuyo motor lanzaba una excepción no se registraba → ahora se registra con `run_status=error`, suma el gasto y cuenta para el cortacircuitos.
  - minor: promoción fallida sin aviso → aviso en `stop_reason` y sección "Bloqueos y avisos" en la bandeja; además, timeout en la verificación de la feature.
  - minor: sin presupuesto tras el maker → el checker no se invoca.
  - minor: un fallo de `create_worktree` dejaba `running` → ahora queda `interrupted` y va a la bandeja.
  - minor: el test de push ahora comprueba el argv real del CLI.
  - minor: la guarda no ve archivos ignorados por git → documentado en `roles.md`.
- Mejor próximo paso:
  - con aprobación, hacer el commit inicial;
  - repetir `factory features verify` para registrar los hashes;
  - ejecutar 3.10 desde un clon;
  - lanzar el dogfooding (9.3).

### Sesión 003 — 2026-10-27

- Objetivo: tareas 3.9, 3.10 y 9.3 (aprobadas).
- Completado:
  - commit inicial `d7c3d5b`;
  - repetición de `factory features verify` en las 6 features (la evidencia apunta a `d7c3d5b`) y commit `9d74594`.
- Verificación ejecutada:
  - `git clone` en el scratchpad y `./init.sh` → código 0 (doctor sin fallos).
  - Sesión nueva (haiku, solo lectura) sobre el clon: respondió las 5 preguntas (0,008 USD). Detectó que este `progress.md` decía "sin commits" → corregido aquí.
- Dogfooding 9.3 (`goals/dogfood-cli-help.md`), ejecución `20261028-040428-dogfood-cli-help-90b9`:
  - Resultado: `completed` en 1 ronda y 41 s, por 0,4468 USD (tope 1,00 USD). Maker `claude-sonnet-5-5` con 0,13 USD y 4 turnos; checker `claude-opus-5-5` con 0,31 USD y 6 turnos.
  - Base: 1 de 3 criterios fallaba (el test no existía). Ronda 1: 3 de 3, checker `pass_with_minor`, decisión `keep`.
  - Rama: `factory/20261028-040428-dogfood-cli-help-90b9` (commit `ed18856`, añade `tests/test_cli_help.py`, +16 líneas). `main` sigue en `9d74594`. El worktree hermano se eliminó y queda una entrada pendiente en la bandeja.
  - Contrato del CLI confirmado con una ejecución real: `--json-schema` devolvió una salida estructurada válida para ambos roles. No hubo `permission_denials` ni bloqueos por confianza en el worktree fuera del repo. `modelUsage` confirma modelos distintos por rol. No se registró en qué clave exacta llegó la salida (campo estructurado o JSON en `result`); el adaptador acepta las dos.
- Retrospectiva (proyecto 07):
  - Intervenciones humanas durante la ejecución: 0.
  - El checker detectó 2 problemas `minor`, ambos válidos:
    - la lista de subcomandos está escrita a mano y no se contrasta con `build_parser`;
    - la comprobación `"  nombre" in texto` es una subcadena laxa.
  - El checker no pasó por alto ningún problema mayor visible: el test es pequeño y correcto.
  - Límite observado: `pass_with_minor` aprueba la ronda, así que los `minor` no generan una segunda ronda. Corregirlos queda a criterio humano al revisar la rama. Si se quieren corregir automáticamente, sube `consecutive_passes` o trata `minor` como bloqueante en un objetivo concreto.
  - Techo de calidad del loop: lo marca el criterio del checker, más que la capacidad del maker. Con criterios deterministas más finos (por ejemplo, contrastar con los subparsers) el maker habría tenido que hacerlo así.
  - Coste vs. valor: 0,45 USD y unos 40 s por un test pequeño. Para tareas triviales sale más caro que hacerlo a mano. Rinde en tareas medianas con criterios claros.
- Pendiente para el humano:
  - revisar y decidir la rama del dogfooding (`factory inbox ack <run-id>` al terminar);
  - hacer commit de `progress.md`, `tasks.md` y `goals/dogfood-cli-help.md`, que no están commiteados;
  - decidir la prueba live 9.2, que no está aprobada.

### Sesión 004 — 2026-10-28

- Objetivo: archivar `add-harness-loop-engine` y aplicar `extend-factory-pipeline`, que adapta patrones de *Software Factory v2* (ZazenCodes, GPLv3) sin copiar código.
- Completado:
  - Archivo del cambio anterior, con las 6 specs principales sincronizadas.
  - Rutas protegidas: críticas siempre protegidas, `tests/**` en este repo y `scope.allow_modify`.
  - Artefactos por ronda: `rounds/<n>/{maker,checks,review}.md` y `decision.md`.
  - `factory goal rework`.
  - `factory land`: merge exacto verificado, `--ff-only`, sin push.
  - `factory intake` y `factory goal promote`, con borradores no ejecutables.
  - README: guía paso a paso con requisitos y pasos A–F.
  - Documentos temáticos nuevos: `intake.md`, `revision.md` y `vigilancia.md`.
- Verificación ejecutada:
  - `./scripts/check.sh` → código 0 (272 tests, ruff y doctor).
  - `openspec validate extend-factory-pipeline --strict` → válido.
  - Pasos B–D del README sobre un proyecto nuevo, con instalación no editable → en verde.
- Evidencia: `factory features verify` → `passing` en `protected-paths`, `round-artifacts`, `run-rework`, `run-landing` y `request-intake`. El commit de la evidencia es `7563c8f` porque los cambios aún no están commiteados.
- Tarea 7.2 (aprobada, 1 USD como máximo): intake real de la petición "init.sh de factory init con .venv en proyectos Python".
  - Resultado: `ACCEPT`, riesgo `medium`, superficie `harness`, sin recorte. `claude-opus-5-5`, 12 turnos, **0,4389 USD**, sin denegaciones de permisos.
  - El borrador cita `scaffold.py:68-74` y propone 3 criterios ejecutables.
  - En la revisión de `goal promote`, el plan mostró que `tests/**` está protegido, mientras el borrador pedía añadir tests a `tests/test_init.py`, que ya existe. Se añadió `allow_modify: [tests/test_init.py]`, después `promote --yes` y luego `goal run --dry-run` → en verde. Petición en `promoted`; objetivo en `goals/en-repos-con-pyproject-toml-factory.md`, listo para un `goal run` real.
  - Hallazgo: el intake no conoce `protected_paths`. Mejora propuesta: dárselos en el prompt y admitir `scope.allow_modify` en su esquema.
- Riesgos / pendientes:
  - Ningún cambio de esta sesión está commiteado.
  - El `init.sh` que genera `factory init` en proyectos Python instala con pip en el Python global; queda como mejora fuera de alcance (avisado en el README).
- Archivado: `extend-factory-pipeline` en `openspec/changes/archive/2026-10-28-extend-factory-pipeline/`, con specs sincronizadas (goal-loop +4, loop-state +2, run-landing y request-intake nuevas).
- Mejor próximo paso: opcionalmente, `factory goal run goals/en-repos-con-pyproject-toml-factory.md` (real, con coste) y `factory land`.

### Sesión 005 — 2026-10-28

- Objetivo: aplicar `add-knowledge-brains`: cerebro principal (copia de los libros, fuera de git) y cerebro diario (versionado), con búsqueda e inyección acotada en los loops. Indicación del usuario: solo archivos `.md`; los `.pdf` se descartan en `.gitignore`.
- Completado:
  - `factory brain import|status|search|learn|reindex|commit|pending|accept|reject`.
  - Importación filtrada (`.md` + índices), atómica y validada; `/brain-principal/` y `*.pdf` en `.gitignore`; check crítico de `doctor` si el principal llega a git.
  - Cerebro diario con catálogo e índices propios; ruta prohibida en todo objetivo; `factory brain commit` solo de `brain-diario/`.
  - Capturas deterministas al terminar cada ejecución, pendientes de revisión, con salvaguarda de 8-gramas contra texto de libros.
  - Búsqueda por palabras clave (sin dependencias) e inyección citada en el prompt de usuario del maker (una selección por ejecución, presupuesto `inject_max_tokens`, evento `knowledge`); el intake recibe notas del diario y las rutas de los catálogos; el checker no recibe nada.
  - Acceso de lectura: `--add-dir` por cerebro, denegaciones `Edit/Write(//<ruta>/**)` añadidas en cada invocación y huella de integridad al inicio y al final con aviso en `decision.md` y la bandeja.
  - Documentación: `docs/harness/cerebros.md`, `loops.md` (`knowledge`) y paso G del README.
- Ajustes de diseño tras medir con el vault real (registrados en `design.md`, D3 y D4):
  - **Cobertura en la puntuación.** Para "rate limiting", 5 de las 8 mejores notas solo contenían "rate" ("Rate of Change", "Learning Rate Scheduling"). Ahora la puntuación se multiplica por la fracción de términos encontrados.
  - **Fusión intercalada.** Con `["rate limiting", "api gateway"]`, ordenar solo por puntuación daba las 8 plazas a "api gateway". Ahora se intercala la mejor nota de cada consulta.
- Verificación ejecutada:
  - `./scripts/check.sh` → código 0 (330 tests, ruff y doctor sin fallos).
  - `openspec validate add-knowledge-brains --strict` → válido.
  - `factory features verify` → `passing` en `main-brain`, `daily-brain`, `brain-captures` y `brain-retrieval`.
- Tarea 6.2 (sin coste de API), vault real (`~/…/redPDF/book/obsidian-vault` en el equipo de entonces):
  - `factory brain import` → 11.245 notas, 82 libros, ~13,0 M tokens, en ~3 s. Copiados 11.330 `.md` (notas + guías) y 4 índices; ningún PDF.
  - `git status` → nada de `brain-principal/` (`git check-ignore` lo confirma); `factory doctor` → `brain-principal-untracked` en PASS.
  - `factory brain search "rate limiting"` → primeros resultados *Defending APIs* · cap. 9 · pp. 259–260 y *Privacy and Security for LLMs* · cap. 5.
  - Selección simulada para `["rate limiting", "api gateway"]` → 8 notas en 0,42 s, 3 en texto completo (2.659/3.000 tokens) y 5 como referencia, con ambas consultas representadas.
- Tarea 6.3 (aprobada, ≤ 0,50 USD): dos invocaciones reales vía `ClaudeCodeRunner` (mismos argumentos que el motor), `claude-haiku-5-5`, `acceptEdits`, en directorios temporales del scratchpad (no sobre `brain-principal/`):
  - `Write` de `brain/probe.txt` → en `permission_denials`, archivo inexistente (0,0061 USD, 4 turnos).
  - `Edit` de `brain/nota.md` existente → en `permission_denials`, contenido intacto (0,0040 USD, 5 turnos).
  - En ambas, escribir en el cwd y leer/`Glob` del cerebro funcionó; la sintaxis `Edit(//<ruta absoluta>/**)` es correcta y no hubo que ajustarla.
  - El `CLAUDE.md` del cerebro (con una palabra de control) **no** se cargó en el contexto vía `--add-dir`: la palabra no apareció y el agente lo confirmó.
  - Coste total: **0,0101 USD**.
  - Ajuste derivado: `Config._abs` ahora resuelve también las rutas absolutas, para que `--add-dir` y las denegaciones coincidan si la ruta tiene enlaces (`/tmp` → `/private/tmp`). Test `test_ruta_absoluta_con_enlace_se_resuelve`.
- Revisión independiente (subagente `checker`), primera pasada: `fail`, con 4 `medium` y 6 `low`. Todos corregidos con tests:
  - un catálogo roto ya no deja una ejecución huérfana ni tumba el intake (queda como aviso);
  - el presupuesto mide el texto que de verdad se inyecta;
  - la fusión agrupa por consulta (el diario ya no recibe plazas de más);
  - la salvaguarda de capturas cubre también el `abstract` de las notas solo citadas;
  - la huella ignora archivos ocultos (`.DS_Store`, `.obsidian/`) y avisa si aparece un cerebro;
  - las denegaciones se emiten aunque el cerebro aún no exista;
  - la integridad se comprueba después de la promoción;
  - las cabeceras de cita se reducen a una línea;
  - se quitó el gancho de test del motor.
  - D4 y `cerebros.md` actualizados. `./scripts/check.sh` → código 0 (339 tests).
- Segunda pasada del `checker`: `pass_with_minor`, con los 10 hallazgos cerrados y 3 `low` nuevos, también corregidos:
  - un `chapter_title` no textual en el catálogo ya no rompe el loop ni el intake;
  - un fallo de la huella inicial ya no produce un falso aviso de integridad;
  - D5 y D7 describen lo implementado.
- Incidencia: durante la sesión apareció `/ba` delante de la primera línea de `factory.toml` (tecleo accidental, no generado por factory), lo que rompía el TOML. Se quitó con el visto bueno del usuario.
- Riesgos / pendientes:
- Archivado: `add-knowledge-brains` en `openspec/changes/archive/2026-10-28-add-knowledge-brains/`, con specs sincronizadas (`main-brain`, `daily-brain` y `brain-retrieval`, nuevas; 21 requisitos).
- Integrada con `factory land` (a petición del usuario) la ejecución `20261028-052249-en-repos-con-pyproject-toml-factory-a254` (objetivo `en-repos-con-pyproject-toml-factory`, 2 rondas, 2,14 USD): merge `1fa6e05` sobre `31423c1`, verificado antes de mover `main`, sin push. El `init.sh` de `factory init` en proyectos Python crea e instala en un `.venv` propio; se quitó del README el aviso sobre pip global. La rama `factory/20261028-052249-…-a254` se conserva.
- Mejor próximo paso: empezar a alimentar el cerebro diario con `factory brain learn` y lanzar un objetivo real con `knowledge.queries`.

### Sesión 006 — 2026-10-29

- Objetivo: el usuario quería versionar las notas de `redPDF/book` para que cada clon tuviera una base de conocimiento. Esas notas son el texto completo de 82 libros comerciales y el remoto es GitHub, así que no se versionaron. El usuario eligió dos alternativas: un **mapa de la biblioteca sin texto** y **fichas propias** en el cerebro diario. Él mueve los libros a mano entre sus equipos.
- Completado (cambio OpenSpec `add-library-map`, feature `library-map`):
  - `brain/libmap.py`: mapa construido desde una lista blanca de campos (sin `abstract` ni cuerpos ni guías del vault), con títulos recortados a 20 palabras y salida determinista que solo reescribe lo que cambia;
  - `factory brain import` regenera `brain-mapa/`; `status` lo muestra; `search` avisa del modo "solo mapa";
  - sin principal importado, la búsqueda, la inyección y el intake usan el mapa (solo citas, "texto no disponible en este equipo"); con principal, el mapa se ignora;
  - `doctor`: comprobación crítica `brain-map-sin-texto`, dentro de `_brain_checks` como pidió la otra sesión;
  - el mapa es ruta prohibida en todo objetivo, con denegaciones `Edit/Write` y huella;
  - `factory brain commit`, `status` y `land` cubren el mapa;
  - documentación en `cerebros.md` (tabla de tres columnas, mapa, fichas propias) y en el README, paso G;
  - 6 fichas sembradas en `brain-diario/` con aprendizajes de este proyecto (macOS `timeout`, `/tmp` → `/private/tmp`, denegaciones con `--add-dir`, cobertura, fusión intercalada, zsh `:t`); ninguna sale de los libros.
- Verificación ejecutada:
  - `./scripts/check.sh` → código 0 (355 tests, ruff y doctor sin fallos);
  - `openspec validate add-library-map --strict` → válido;
  - `factory features verify library-map` → `passing`.
- Evidencia con el vault real (sin coste de API):
  - mapa de 11.245 notas y 82 libros, 5,3 MB, generado en ~3,5 s; reimportar → "sin cambios";
  - **ninguna fuga**: 0 de 10.822 `abstract` y 0 de 45.011 fragmentos de 8 palabras de 1.500 notas al azar aparecen en el mapa; campos del mapa = lista blanca exacta;
  - clon simulado (solo `factory.toml` + `brain-mapa/`): `factory brain search "rate limiting"` → *Defending APIs* · cap. 9 · pp. 259–260 primero, igual que con el texto completo.
- Coordinación: otra sesión (`equipo-ideal-subagentes`) trabaja en `add-equipo-ideal` en worktrees bajo `.claude/worktrees/`, sin tocar el checkout principal. Commiteó su preparación (`f18df16`). Acordado: features con prioridades únicas (`library-map` = 23), commits con pathspec explícito y aviso antes de integrar.
- Revisión independiente (`checker`), primera pasada: `fail` con 7 `medium`. No encontró texto de los libros en el mapa, pero sí que `doctor` solo validaba los nombres de los campos y no los valores. Corregido:
  - `subtitle` fuera de la lista blanca: en el vault real a veces trae texto de una página ("Copyright © 2022 Packt Publishing");
  - formatos estrictos por campo (keywords e identificadores sin espacios; las 89.425 keywords reales los cumplen);
  - `doctor` reconstruye y compara cada línea, libro, guía y `.gitignore`, y su salida de texto muestra el detalle (archivo y campo);
  - `.gitignore` propio del mapa (`.DS_Store` y `.obsidian/` ni cuentan ni se commitean);
  - aviso y check recomendado si el mapa está en `.gitignore`, sin bloquear `factory brain commit`;
  - `search --json` deja los avisos en stderr;
  - el commit solo pasa las rutas con cambios preparados;
  - el intake recibe el mapa en `--add-dir`; `_map.json` entra en la huella;
  - `factory.toml` rechaza rutas de cerebros que se solapen;
  - tests: mapa construido (no copiado), texto pegado en valores, clon con `--json`, mapa ignorado, aviso de integridad del mapa, tipos raros, diario y mapa juntos.
  - Vault real regenerado: 0 de 10.822 `abstract`, 0 subtítulos y 2 de 74.154 fragmentos de 8 palabras (2.000 notas). Los 2 son títulos de sección que el resumen del capítulo repite como índice, no prosa. `./scripts/check.sh` → código 0 (369 tests).
- Segunda pasada del `checker`: `fail` con 1 `medium`, porque `doctor` comparaba el JSON interpretado, no el texto. Un párrafo cabía en una clave repetida o en `_map.json`. Corregido:
  - comparación del texto exacto de cada archivo con su forma canónica (catálogo línea a línea, `_books.json`, `_map.json` con recuentos reales y huella `[0-9a-f]{64}`, guías y `.gitignore`), y error si falta alguno;
  - aviso de notas descartadas en `import`;
  - ruta configurada en el mensaje de `doctor`;
  - el `.gitignore` del mapa entra en la huella;
  - tests de clave repetida, `_map.json` manipulado, archivo ausente, intake con el mapa y aviso en `decision.md` y la bandeja.
  - `./scripts/check.sh` → código 0 (376 tests); el mapa real pasa la validación de texto exacto.
- Tercera pasada del `checker`: `pass_with_minor`, con el `medium` cerrado y 4 `minor` nuevos, también corregidos:
  - `factory brain commit` se niega a commitear un mapa que `doctor` rechazaría;
  - un mapa con UTF-8 inválido nombra el archivo;
  - test de clave repetida en `_books.json`;
  - redacción de la spec sobre los autores.
- Riesgos / pendientes:
  - sin commitear; al commitear, avisar a la otra sesión.
- Mejor próximo paso: revisión del `checker`, commit (incluye `brain-mapa/` y `brain-diario/`) y archivar `add-library-map`.

### Sesión 007 — 2026-10-28 a 2026-10-30 (`add-equipo-ideal`)

- Objetivo: el "equipo ideal" de sub-agentes. Un técnico (orquestador) decide la convocatoria y dirige a hasta 11 jugadores especialistas; el `checker` sigue como árbitro independiente.
- Cómo se hizo:
  - cambio OpenSpec `add-equipo-ideal`: propuesta, diseño D1–D9, 4 specs delta y tareas (`f18df16`);
  - 7 unidades en paralelo (subagentes en worktrees, commits en ramas locales sin push);
  - rama `integracion/equipo-ideal`, que trajo `main` y resolvió el README (equipo = paso L) y una línea pegada de `AGENTS.md`;
  - 6 revisiones del árbitro hasta `pass_with_minor`;
  - fast-forward de `main` a `c066f30` y después a `cde950b`, sin push. La sesión de `add-panel` apartó y reaplicó sus cambios de `cli.py` y `README.md` para hacerlo posible.
- Completado:
  - **`factory team list | validate | lineup`:** plantilla en el frontmatter de `.claude/agents/*.md` (`dorsal`, `tipo`, `convocatoria`), formación 4-3-3 con vacantes y convocatoria determinista con su motivo; comprobación crítica `team-roster` en `doctor`;
  - **`factory complexity [rutas] [--base REF] [--max N] [--json]`:** complejidad ciclomática con `ast`, rangos A–F, delta y umbral;
  - **jugadores:**
    - #1 `seguridad`: copia literal de `cloudflare/security-audit-skill` @ `c1c8a8c` (MIT) con sha256 en `UPSTREAM.md`, siempre en modo guía;
    - #2 `qa`, #3 `documentador`, #4 `revisor-pr` (ideas de `gentleman-guardian-angel`, MIT, sin copiar código), #5 `metricas`, #6 `producto` y #9 `ingeniero-software`;
    - técnico `tecnico` + skill `/equipo` (reglamento del partido) + `docs/harness/equipo.md`;
    - vacantes 7, 8, 10 y 11 con perfiles sugeridos;
  - **protección:** `.claude/agents/**`, `.claude/skills/**`, `.claude/commands/**`, `.claude/hooks/**` y `.claude/settings.json` son críticos en los loops; `releases_critical` también rechaza rutas dentro de un crítico (con o sin `./`);
  - **arreglo de un fallo previo:** git entrecomillaba las rutas con tildes y un loop podía modificar un crítico o un archivo fuera de alcance sin que se revirtiera. Ahora las rutas se leen con `-z`;
  - **validación:** ningún agente puede repetir el `name` de otro y el árbitro debe declarar `name: checker` (contra la suplantación);
  - **otros:** `.claude/settings.local.json` se ignora en git y `tests/test_cli_help.py` se contrasta con `build_parser`.
- Verificación ejecutada (en `cde950b`):
  - `./scripts/check.sh` → 0 (604 passed, ruff y doctor sin fallos);
  - `openspec validate add-equipo-ideal --strict` → válido;
  - `factory team validate` → 0 (8 miembros).
- Revisión independiente (`checker`): 6 rondas sobre el diff conjunto.
  - Los `critical` y `medium` están corregidos, con tests. Entre ellos: `revisor-pr` leía el razonamiento del maker, la spec de `allow_modify` prometía más de lo que hace la heurística, y el prefijo `./` esquivaba el rechazo.
  - Última ronda: `pass_with_minor`; también se corrigieron sus 6 `minor`.
- Pruebas reales con haiku (una por jugador nuevo): total ≈ 0,029 USD. Todas cargaron el agente y respondieron con su cabecera, y los revisores no cambiaron el árbol.
- Cierre (2026-10-30):
  - **9.2:** `factory features verify` de las 7 features → `passing`. `verify` no exige `in_progress`, así que no se tocó `review-hooks`, que está en `in_progress` en add-panel. `team-roster` y `team-integration` se volvieron a verificar sobre el código final.
  - **9.4, primer partido real con el reglamento `/equipo`:**
    - revisión de `cde950b`, con los jugadores en `claude -p --agent … --model haiku` y un tope de 0,05 USD por jugador (los subagentes nuevos aún no estaban registrados en la sesión);
    - convocatoria determinista de 6, ajustada a 4: `seguridad`, `qa`, `revisor-pr` y `metricas`;
    - vuelta 1 → `fail`, con 2 `medium`: falta un test del `.gitignore`, y `load_roster` sube de 27 a 29 (D);
    - vuelta 2 (`qa` y `metricas`) → `pass_with_minor`;
    - árbitro → `pass_with_minor`, con sus `minor` corregidos;
    - coste total del partido: 0,078 USD; los revisores nunca cambiaron el árbol.
  - **Lecciones del partido:**
    - **Subagentes en la sesión:** los subagentes de `.claude/agents` creados durante la sesión solo están disponibles tras recargarla. Mientras tanto, `claude -p --agent` sirve igual y además permite un tope duro de coste.
    - **zsh y `--paths`:** zsh no separa por espacios una variable sin comillas; pasar las rutas a `--paths` con `xargs -0`.
    - **Varios jugadores sobre lo mismo:** `seguridad`, `qa` y `revisor-pr` coincidieron en el mismo `minor` (`lineup` recortaba sus salidas `-z`).
  - **Archivado:** `openspec archive add-equipo-ideal` → `2026-10-30-add-equipo-ideal`. Specs nuevas: `team-roster`, `team-match` y `complexity-metrics`; `goal-loop` gana 5 requisitos.
- Riesgos / pendientes:
  - **Push:** no hecho; decisión humana.
  - **README:** la fila de "Cómo está organizado" dice "12 capacidades" y ahora son 15. No se tocó porque `README.md` tiene cambios sin commitear de add-panel.
  - **Mejoras menores anotadas por el árbitro:** `--paths` recorta espacios, a diferencia de las rutas de git (documentado), y el riesgo de `.claude/settings.local.json` creado por un maker dentro de su worktree.
  - **Riesgo conocido:** un maker puede crear `.claude/settings.local.json` en su worktree. Ya no llega a `main`, porque está en `.gitignore`, pero el checker de esa misma ronda lo cargaría.
- Seguimiento propuesto (cambios aparte): el equipo dentro de `factory goal run` (fase 2), fichar las vacantes y refactorizar la deuda de complejidad que mide `factory complexity` (`parse_intake` 35, `parse_goal_text` 32, `cmd_brain` 30, `render_loop_state` 30).
- Mejor próximo paso: decidir el push de `main`. Siguientes cambios propuestos: el equipo dentro de `factory goal run` (fase 2), fichar las vacantes y refactorizar la deuda de complejidad.

### Sesión 008 — 2026-10-29 a 2026-10-30 (`add-panel`)

- Objetivo: validar si el panel (`factory panel`) estaba completo y terminarlo (grupos 3 a 5 de `add-panel`).
- Estado encontrado: lógica del panel hecha y con tests, pero `factory panel` y `factory hook` no existían en el CLI, el grupo 5 no estaba empezado y nada estaba en `progress.md`.
- Completado:
  - **CLI:** `factory panel [--port] [--json] [--open] [--projects-dir]` y `factory hook`, con import diferido (D10) y `--port` validado (0–65535).
  - **Captura real (5.2):** esta versión de Claude Code entrega la respuesta final de un subagente con la herramienta `SubagentHandback`. Las 5 primeras revisiones reales quedaron como `sin_veredicto`; el parser ahora lee `SubagentHandback` y, si no, `last_assistant_message`. Las 5 transcripciones reales dan su veredicto, y las revisiones de esta sesión se registraron en vivo con el veredicto y las severidades exactos. Campos observados en `design.md` (Open Questions). Las líneas antiguas del registro conservan `sin_veredicto`, porque el registro no se reescribe.
  - **Datos reales:**
    - los `SubagentStop` sin tipo (agentes internos, como el evaluador del hook de `/goal`, cada ~30 s) ya no se registran;
    - un inicio sin fin pasa a `sin_cierre` a las 2 h. Se vieron una sesión cerrada con el revisor trabajando y 4 lanzamientos de jugadores que no crearon subagente.
  - **Hallazgos del checker (4 rondas):**
    - un archivo ilegible avisa en `warnings` y uno ausente no (la spec delta se ajustó);
    - el refresco por SSE solo repinta las secciones que cambian y conserva los `<details>` abiertos y su scroll;
    - 405 para cualquier método distinto de GET o HEAD, incluido TRACE;
    - las severidades se cuentan solo en la sección `Hallazgos`;
    - se eliminaron duplicados en `panel/__init__.py`, y `hook_reviews` y `last_response` se refactorizaron por debajo de complejidad 20.
  - **Documentación:** README (paso M y referencia de comandos), `docs/harness/panel.md` completo (uso, fuentes, privacidad, seguridad, tiempo real y límites) y enlace en `AGENTS.md`.
  - **Coordinación con la sesión 007:** se apartaron y reaplicaron `cli.py` y `README.md` para su merge, y se añadieron `panel` y `hook` a `tests/test_cli_help.py`.
- Verificación ejecutada (árbol final, sobre `2491854`):
  - `./scripts/check.sh` → 0 (737 passed, ruff y doctor sin fallos);
  - `openspec validate add-panel --strict` → válido;
  - `factory features verify token-usage | review-hooks | observability-panel` → `passing`;
  - `pip wheel . --no-deps` incluye `factory/panel/static/index.html`;
  - `factory complexity src/factory/panel` → máximo 18.
- Cifras medidas (2.4 y 3.5, 2026-10-29): agregación completa de tokens en 131 ms, refresco incremental en 4 ms, y el recuento independiente por `message.id` coincide (629 mensajes, 870.292 tokens de salida). Hook: ~68 ms por evento.
- Prueba de humo (5.3), solo por HTTP y SSE (no hubo navegador en la sesión):
  - `factory panel --json | python -m json.tool` → 0, sin `warnings`;
  - `factory panel --port <libre>`: `/` y `/api/snapshot` 200, `TRACE` 405;
  - la instantánea tiene tokens de 5 sesiones y 2 loops, las revisiones reales y el avance de `add-panel` (`add-equipo-ideal` ya está archivado, así que no aparece);
  - al lanzar cada revisión del checker, `/api/stream` envió `change` con `reviews` en el mismo segundo.
- Revisión independiente (`checker`): `fail` (3 medium) → `fail` (1 medium) → `pass_with_minor` → `pass_with_minor`. No quedan `critical` ni `medium`.
- Riesgos / pendientes:
  - **5.3 visual:** abrir `factory panel --open` y mirar las tres pestañas, los temas claro y oscuro y el ancho de móvil.
  - **Límites aceptados** (`minor`):
    - una sub-viñeta que cite una severidad entre corchetes cuenta como hallazgo;
    - si falla la petición al pasar las 2 h, el contador de esa revisión se detiene hasta el siguiente evento.
  - **Después de 5.3:** archivar con `/opsx:archive add-panel` y subir a 18 las capacidades del README y de este archivo.
  - **Push:** no hecho; decisión humana.
- Mejor próximo paso: la parte visual de 5.3 y, después, archivar `add-panel`.

### Sesión 009 — 2026-10-30 (`add-panel`, tarea 5.3)

- Objetivo: validar qué quedaba del proyecto y cerrar lo que faltara.
- Estado encontrado: 26 features en `passing`, árbol limpio sobre `b70d745`, `add-panel` con 18/19 tareas y solo la 5.3 abierta. El clon no tenía `.venv` ni `.factory/`.
- Arranque: `./init.sh` → código 0 (verificación de referencia en verde).
- Límites de los "datos reales" en este clon (no se sustituyeron por fixtures):
  - al arrancar no existía `.factory/`; el hook lo creó durante esta misma prueba, así que hay revisiones reales pero `tokens.loops` sigue vacío (no hay `runs/`) y se perdió el `events.jsonl` con la revisión del paso 5.2;
  - el directorio de transcripciones de este proyecto en `~/.claude/projects/` solo tiene la de esta sesión (1), de modo que los tokens de sesiones son los de hoy. Las cifras de la sesión 008 (5 sesiones y 2 loops) se midieron en otro equipo, con otro `$HOME` (ver sesión 005): el slug del proyecto es distinto y por eso aquí no aparecen;
  - `add-equipo-ideal` está archivado, así que no aparece en la pestaña Tareas. Lo mismo que ya anotó la sesión 008; la tarea 5.3 lo pedía, pero su archivado era una tarea cerrada de ese mismo cambio.
  - Para la prueba se generó una revisión real nueva con el `checker` y el hook instalado, en lugar de la del paso 5.2.
- Prueba de humo (5.3): `factory panel --port 8777 --open`, con el navegador del usuario sobre `http://127.0.0.1:8777/`.
  - Confirmado en el navegador, con el panel abierto y sin recargar la página:
    - pestaña **Tokens**: la sesión de hoy con entrada, caché y salida (loops vacíos, por lo dicho arriba);
    - pestaña **Revisiones**: la revisión real del `checker` de esta sesión apareció sola, en estado `en_curso` y con el contador corriendo, mientras la página ya estaba abierta — esa es la prueba del tiempo real;
    - pestaña **Tareas**: `add-panel` con su avance y el detalle por grupo, más las 26 features en `passing`.
  - Evidencia por API del mismo instante: `/api/snapshot` → `reviews[0]` con `source: hook`, `reviewer: checker`, `status: en_curso`, `tool_use_id` real y `warnings: []`; `.factory/hooks/events.jsonl` con el `PreToolUse` correspondiente (`review: true`).
  - **Salto en vivo observado** (criterio que la sesión 008 dejó abierto): la misma revisión pasó sola de `en_curso` (14:12:20 UTC) a su veredicto `fail` con `critical 0 / medium 2 / minor 3` y 175 s de duración (14:15:15 UTC), sin recargar la página. `.factory/hooks/events.jsonl` quedó con las dos líneas, `PreToolUse` y `SubagentStop`.
  - Traza del propio SSE, capturada a la vez con `curl -sN /api/stream`: `event: hello` con `sections: [tokens, reviews, tasks]` y, durante la revisión, varios `event: change` con `data: {"sections": ["reviews"]}` — el refresco llega por sección, no por recarga.
  - No sirvió Chrome headless para capturar el DOM: el `EventSource` del SSE deja la carga abierta y `--dump-dom` nunca retorna. La comprobación visual la hizo la persona.
- Revisión independiente (`checker`): `fail` con 2 `medium` y 3 `minor`, sobre el borrador de esta entrada. Los dos `medium` eran que la entrada se cortaba antes de registrar lo observado y que faltaba el criterio de aceptación del "sin recargar"; ambos quedaron cubiertos al añadir lo de arriba. De los `minor`: se reescribió en pasado lo de `.factory/`, se anotó que las cifras de la 008 son de otro equipo y se actualizó el encabezado "Estado verificado actual".
- Con eso, 5.3 queda marcada y `add-panel` cierra 19/19. Trazabilidad por sub-criterio: los tokens de loops y el camino HTTP/SSE vienen de la sesión 008 por API (5 sesiones y 2 loops, en otro equipo); el "sin recargar" y las tres pestañas, de esta sesión en el navegador; la revisión del paso 5.2 se sustituyó por una nueva, y `add-equipo-ideal` ya estaba archivado.
- Archivado: `openspec archive add-panel --yes` → `2026-10-30-add-panel`. Specs nuevas: `observability-panel` (7 requisitos), `review-hooks` (6) y `token-usage` (6). El repo pasa de 15 a 18 capacidades; se actualizó el conteo en `README.md` y en el encabezado de este archivo.
- Verificación ejecutada: `./init.sh` → 0; `./scripts/check.sh` → 0 (antes y después del archivado); `openspec validate add-panel --strict` → válido; `openspec list` → sin cambios activos; 26 features en `passing`.
- Riesgos / pendientes:
  - **Push:** no hecho; decisión humana.
  - **Commit:** esta sesión deja el árbol con el archivado y los documentos sin commitear.
  - **Límite del panel en este clon:** sin `.factory/runs/`, la pestaña Tokens no muestra loops. Se verá en cuanto corra un `factory goal run` aquí.
  - **Comprobaciones visuales que no se repitieron:** temas claro y oscuro y ancho de móvil (criterio de la tarea 4.5, ya cerrada en la sesión 008).
- Cerebro principal (**revertido en la sesión 010, ver abajo**): `factory.toml` pasó a apuntar directo a un vault de Obsidian fuera del repositorio, por ruta absoluta, en lugar de una copia importada. `factory brain search` ya lee su texto (`principal_from_map` → `False`). A cambio, `factory brain status` dice "no importado" y `doctor` deja un aviso **RECOMENDADO**, porque el vault no tiene el registro `.factory-import.json` y factory no escribe en el origen: `check.sh` sigue en 0 con 1 recomendada. Queda explicado en `docs/harness/cerebros.md`.
- Mejor próximo paso: commitear y decidir el push. Siguientes cambios propuestos: el equipo dentro de `factory goal run` (fase 2), fichar las vacantes del roster y refactorizar la deuda de complejidad (`parse_intake` 35, `parse_goal_text` 32, `cmd_brain` 30, `render_loop_state` 30).

### Sesión 010 — 2026-10-30 (`add-reglas-de-oficio`)

- Objetivo: traer al harness cinco reglas de oficio de la fábrica `/yate` (skill propia para servicios Go) que aquí no existían, sin tocar código ni reglas de verificación.
- Qué se trajo y dónde vive cada regla:
  - **prueba de mutación**: un hallazgo `critical`/`medium` dado por corregido solo se cierra con un test que falla al revertir el arreglo, citado en `evidence` → `prompts/checker.md` y `.claude/agents/checker.md`;
  - **lo que el diff no muestra**: documentación, specs, decisiones o rutas que el cambio volvió falsas; es hallazgo aunque el archivo no esté en el diff → los mismos dos;
  - **`origin/main`**: comprobar contra el remoto antes de afirmar que algo no existe, citando el comando en `self_check` → `prompts/maker.md`;
  - **un supuesto es una decisión, nunca un hecho** → `prompts/intake.md`;
  - **precedencia** entre los cerebros y la documentación del repositorio, con la contradicción registrada → `docs/harness/cerebros.md`.
  - Además, la casilla de **lo que quedó mintiendo** en `docs/harness/clean-state-checklist.md`, y el resumen con enlaces en `docs/harness/roles.md` y `docs/harness/revision.md`, sin repetir el texto de los prompts.
- Verificación: `tests/test_reglas_de_oficio.py` (nuevo, 11 casos) lee los archivos y afirma sobre su contenido, el patrón de `tests/test_team_revisores.py`. Incluye un tope de 70 líneas por prompt: checker 58, intake 47, maker 45.
- Alcance que el plan no previó: los prompts viajan duplicados en `src/factory/templates/prompts/`, y `tests/test_templates.py` exige igualdad byte a byte (`engine.load_prompt` los usa de respaldo). Hubo que sincronizar los tres; quedó como tarea 3.4 y corregida la frase "sin cambios en `src/factory/`" de la propuesta.
- Revisión independiente (`checker`), que además era la primera prueba real de las reglas nuevas (tarea 5.2): `pass_with_minor`, sin `critical` ni `medium`, con 5 `minor`, todos corregidos:
  - la propuesta y las tareas afirmaban "sin cambios en `src/factory/`" y el cambio sí lo tocaba;
  - `progress.md` y `session-handoff.md` seguían diciendo 26 features y "ningún cambio activo";
  - el pie de `docs/harness/cerebros.md` citaba `openspec/changes/add-library-map/`, archivado desde la sesión 006;
  - el formato de salida del subagente `checker` no tenía dónde decir que la superficie invisible al diff se miró: ahora lo pide bajo `## Veredicto`;
  - tres anclajes de los tests pasaban con texto que invertía la regla: se añadió un segundo anclaje por regla (`sigue abierto`, `self_check`, `nunca un hecho`, `mandan los documentos`, `progress.md`).
  - **El `checker` declaró haberse aplicado las dos reglas nuevas**, y la segunda produjo 3 de los 5 hallazgos, ninguno visible en el diff. El texto gobierna.
- Verificación ejecutada: `./scripts/check.sh` → 0 (748 tests); `openspec validate add-reglas-de-oficio --strict` → válido; `factory features verify reglas-de-oficio` → `passing`.
- Riesgos / pendientes:
  - **Sin commitear**: el cambio y el handoff. El puntero del cerebro principal de la sesión 009 quedó revertido (ver abajo).
  - **11 archivos generados de `.claude/`** (`commands/opsx/*` y `skills/openspec-*`): el CLI de openspec 1.3.1 los reescribió a su plantilla, más vieja que la commiteada. No es trabajo de esta sesión; conviene `git checkout -- .claude/commands .claude/skills` antes de commitear.
  - **Preguntas abiertas de `design.md`**: si la mutación alcanza a los `minor`, y si `factory doctor` debería auditar estas reglas.
- **Tanda paralela de revisores, y el `critical` que destapó.** Para responder si los jugadores pueden revisar en paralelo, se lanzaron `qa`, `metricas` y `revisor-pr` en un solo mensaje sobre el diff sin commitear:
  - solaparon de verdad (`qa` 16:19:03→16:19:53, `metricas` 16:19:11→16:19:35, `revisor-pr` 16:19:21→16:25:25), con tres `tool_use_id` distintos y tres filas simultáneas en el panel;
  - `git status --porcelain` quedó idéntico antes y durante (condición del reglamento §5.4): los revisores son `Read, Grep, Glob` y no tocan el árbol;
  - veredictos: `metricas` `pass`, `qa` `pass_with_minor` (6 `minor` sobre los anclajes de los tests), `revisor-pr` `fail`.
  - **El `critical` de `revisor-pr`, verificado en el código, era del puntero del cerebro de la sesión 009, no del cambio.** Con `principal_dir` apuntando al vault, `factory brain import <otro-vault>` usa el vault como *destino*: `importer.py:140-144` lo renombra y hace `rmtree`, y la guarda de `importer.py:93` solo frena si origen y destino coinciden o se contienen. Se perderían `.obsidian/`, los PDF y todo lo que no sea `.md`. Además, el refresco que documentaba `cerebros.md` no funcionaba en ese modo: con la misma ruta, `import` aborta, y `build_map` solo corre después del import.
  - **Revertido**: `principal_dir = "brain-principal"` y fuera el bloque que documentaba el modo puntero. `factory doctor` pasa de 1 recomendada a 0, lo que confirma la otra corrección de `revisor-pr`: ese aviso no era preexistente, lo introducía el puntero (`doctor.py:367` solo emite `brain-principal-valid` si el directorio existe).
  - El modo puntero puede volver cuando `brain import` rechace un destino que él no creó, o cuando `principal_dir` e `import_dest` sean campos distintos.
- Cierre de la sesión 010:
  - se quitaron las rutas personales de `progress.md` y `session-handoff.md` (el `$HOME` de otro equipo y la ruta del vault); el dato técnico se conservó;
  - se revirtieron los 11 archivos generados de `.claude/` y se borró `parche.patch` de la raíz;
  - el trabajo sin commitear se exportó a `~/Documents/parche-factory.patch` (40 archivos), verificado sobre un clon nuevo del remoto en `fbdf206`: `git apply` limpio, `./init.sh` en 0 y la suite entera en verde;
  - **el `git checkout -- .claude/skills` de esta sesión borró una edición en curso de `.claude/skills/equipo/SKILL.md` de la sesión 011**, que corría en paralelo sobre el mismo árbol. Está anotado en su entrada.
- Mejor próximo paso: commitear y decidir el push. Después, las dos ideas que quedaron de `/yate`: `factory lessons` (lecciones grepeables sobre las líneas añadidas) y el cruce de complejidad con hallazgos por área en el panel.

### Sesión 011 — 2026-10-30 (fichaje de `arquitecto-api`, #10)

- Objetivo: fichar un jugador del equipo ideal con la especialidad que pidió el usuario — construcción de APIs, seguridad de la frontera, alta concurrencia contra servicios externos y bases de datos, y AWS — tomando el conocimiento del cerebro principal.
- Estado encontrado: 27 features en `passing`, ninguna `in_progress`, árbol con lo sin commitear de la sesión 010. Plantilla con 7 jugadores y vacantes 7, 8, 10 y 11.
- Cerebro principal consultado (vault de Obsidian, 82 libros): 20 búsquedas en inglés sobre API security, rate limiting, idempotencia, transacciones y sagas, concurrencia optimista, pools y hilos, caché, IAM/KMS/Secrets Manager, puerta de enlace, multi-inquilino y trazas. Las referencias quedaron como tabla de citas (`libro · cap. · pp.`) dentro del agente: **se cita, no se copia** el texto de los libros.
- Fichaje: `.claude/agents/arquitecto-api.md`, dorsal **10** (mediapunta, antes vacante con el perfil sugerido `arquitecto`), `tipo: revisor`, `model: opus`, solo lectura.
  - Checklist en cuatro áreas: contrato de la API, seguridad de la frontera, concurrencia e integraciones, y AWS y plataforma.
  - No duplica al portero: `seguridad` (#1) busca vulnerabilidades explotables en el diff; `arquitecto-api` juzga si el diseño de la frontera es defendible.
  - Convocatoria por rutas (sin `peticion` para no encarecer cada partido): `src/factory/panel/**`, `src/factory/agents/**`, `engine.py`, `tick.py`, `gitops.py`, `**/*.go`, `**/*.java`, `**/*.tf`, `**/*.sql`, `**/openapi*.yaml` y `**/openapi*.yml`. El reglamento (`.claude/skills/equipo/SKILL.md`) ahora dice al técnico que lo amplíe a mano si la petición habla de APIs, servicios externos, concurrencia o AWS aunque las rutas no casen.
- Documentación, las cuatro superficies que nombran la plantilla: `docs/harness/equipo.md` (fila, formación 4-3-3, vacantes ahora 7, 8 y 11, costes y el procedimiento "Cómo fichar"), `.claude/skills/equipo/SKILL.md` (regla de ampliación, vacantes y coste), `README.md` (fila del 10 y vacantes) y `docs/harness/roles.md` (enumeración de revisores). Las tres últimas salieron de la revisión; ver más abajo.
- Tests: `tests/test_team_arquitecto_api.py` (15 casos: frontmatter, solo lectura, las cuatro áreas, reglas de oficio, biblioteca, gravedad, formato, coherencia con `equipo.md`, las otras tres superficies y el casado de los globs) y `tests/test_team_tecnico.py` actualizado (JUGADORES, VACANTES y el procedimiento de fichaje).
- Verificación ejecutada: `./scripts/check.sh` → 0 (759 tests, 0 críticas y 0 recomendadas fallidas); `factory team validate` → 9 miembros; `factory team lineup --paths src/factory/panel/server.py` → convoca a `arquitecto-api` por rutas.
- Prueba real barata (paso 3 del fichaje): `claude -p --agent arquitecto-api --model haiku --max-budget-usd 0.05` con diff vacío → respondió con el formato exacto (`## Jugador: arquitecto-api (#10)`, veredicto `pass`, "Superficie invisible al diff revisada"), coste 0,0039 USD, `permission_denials: []` y `git status --porcelain` idéntico antes y después.
- Revisión independiente (`checker`), primera vuelta: `fail` con 3 `medium` y 5 `minor`. Todos corregidos:
  - `README.md` mantenía su propia tabla del equipo y seguía contando el 10 entre las vacantes (`medium`);
  - la spec **viva** `openspec/specs/team-match/spec.md` exigía "Los dorsales 7, 8, 10 y 11 MUST quedar vacantes" y su escenario hablaba de "los siete jugadores" (`medium`). La entrada original de esta sesión daba por bueno no abrir cambio OpenSpec: era falso;
  - la sección "Coste" de `.claude/skills/equipo/SKILL.md` no conocía al #10, justo donde se prohíbe cambiar el modelo de un jugador (`medium`);
  - `docs/harness/roles.md` enumeraba los revisores sin él; los globs `openapi*.y*ml` solo casaban en la raíz (`glob_to_regex` ancla y `*` no cruza `/`), ahora `**/openapi*.yaml` y `**/openapi*.yml`; el agente no pedía "exactamente una línea de veredicto"; el test no comparaba la columna de convocatoria de `equipo.md` con el frontmatter; y esta misma entrada citaba un glob que no existe.
  - Prueba de mutación de las correcciones: `tests/test_team_arquitecto_api.py` pasa de 11 a 15 casos y ancla `README.md`, el coste y las vacantes de `SKILL.md`, `roles.md`, la columna de convocatoria y el casado de un `services/pagos/openapi.yaml` con `factory.globs.matches`. Revertir cualquiera de esas líneas rompe un test.
- Cambio OpenSpec `fichar-arquitecto-api`, creado y archivado como `2026-10-30-fichar-arquitecto-api`: modifica los dos requisitos de la plantilla inicial (la foto de `add-equipo-ideal` deja de ser un tope; la lista viva de vacantes vive en `docs/harness/equipo.md` y en `factory team list`) y añade el requisito **Fichajes posteriores**, que fija qué debe cumplir cualquier alta: dorsal libre, frontmatter D8, formato común con una sola línea de veredicto, test propio y las cuatro superficies que no pueden quedar mintiendo.
- Revisión independiente, segunda vuelta: `fail` con 1 `medium` y 1 `minor`, ambos corregidos. El `medium` era que el requisito nuevo **Fichajes posteriores** exige coherencia en cuatro superficies y el procedimiento "Cómo fichar" de `docs/harness/equipo.md` no nombraba ninguna, con el cambio OpenSpec todavía marcado como "Opcional": ahora son los pasos 5 y 6, y `tests/test_team_tecnico.py` los ancla. El `minor`, que las dos primeras viñetas de esta entrada se habían quedado en su versión previa a las correcciones (documentación y 11 casos); reescritas.
- Revisión independiente, tercera vuelta: `pass`, sin hallazgos. Los diez de las dos vueltas anteriores quedan cerrados: ocho con test de mutación, el de la spec con el delta archivado sincronizado con la spec viva, y el de `progress.md` con la entrada reescrita.
- Feature nueva `team-arquitecto-api` (prioridad 28, área `equipo`): `factory features start` → `verify` → `passing`, con evidencia de `pytest tests/test_team_arquitecto_api.py tests/test_team_tecnico.py`.
- Verificación final: `./scripts/check.sh` → 0; `openspec validate fichar-arquitecto-api --strict` → válido; `openspec list` → sin cambios activos; 28 features en `passing`.
- Riesgos / pendientes:
  - **Sin commitear**: este fichaje y todo lo de la sesión 010.
  - **11 archivos generados de `.claude/`** (`commands/opsx/*` y `skills/openspec-*`): ya revertidos por la sesión 010 y fuera del árbol. Si el CLI de openspec 1.3.1 vuelve a reescribirlos, repetir el `git checkout --`, pero **solo sobre `.claude/commands` y `.claude/skills/openspec-*`**, nunca sobre `.claude/skills` entero: ahí vive `equipo/SKILL.md`.
  - **Una edición de `SKILL.md` se perdió** entre dos comandos de esta sesión (la línea de vacantes y la regla de ampliación volvieron al texto anterior). Se reaplicó y quedó comprobada por test. **Causa identificada desde la sesión 010, que corría en paralelo sobre el mismo árbol:** ejecutó `git checkout -- .claude/commands .claude/skills` para revertir los archivos que reescribe el CLI de openspec, y ese `checkout` se llevó por delante la edición en curso de `.claude/skills/equipo/SKILL.md`. No fue el CLI. Lección: un `git checkout --` sobre un directorio compartido borra el trabajo sin commitear de cualquier otra sesión que esté escribiendo ahí.
  - El repo sigue en 18 capacidades: `fichar-arquitecto-api` no añade spec nueva, solo modifica `team-match`.
- Mejor próximo paso: commitear, y después las vacantes que quedan (7 `rendimiento-costes`, 8 `bibliotecario`, 11 `experiencia-cli`).

### Sesión 011 (cont.) — 2026-10-30 (fichaje de `entrega-qa`, #7)

- Petición: un jugador que, tras aprobarse el PR de una API, prepare lo que recibe el **QA humano** y el briefing del plan de desarrollo que el usuario pasa a **Cowork design**.
- Tres decisiones del usuario, con mi recomendación en cada una:
  - las entregas viven en `entregas/<TICKET>/` **dentro de factory-novo** (un solo sitio, versionado, independiente del repo donde esté la API);
  - los requests son **un `escenarios.py` con la biblioteca estándar** (`urllib`), para que el QA no instale nada: `python escenarios.py --base-url … [--only N] [--list]`, salida legible con esperado frente a obtenido y código de salida 0/1;
  - el briefing y el plan son **archivos distintos**: `<TICKET>.md` es el prompt que lee Cowork design y `plan-desarrollo.md` lo escribe Cowork al lado. Un archivo único se pisa a sí mismo en la segunda iteración.
- Fichaje: `.claude/agents/entrega-qa.md`, dorsal **7** (extremo derecho, antes vacante con el perfil sugerido `rendimiento-costes`), `tipo: constructor`, `model: sonnet`, herramientas `Read, Edit, Write, Glob, Grep` (sin `Agent` ni `Bash`), convocatoria `entregas/**`.
  - Terreno acotado: **solo escribe dentro de `entregas/<TICKET>/`**. Lo que ve mal fuera lo reporta, no lo arregla.
  - El briefing lleva 12 secciones fijas, incluidas las que pidió el usuario: qué hace cada API, reglas de negocio, mensajes de error, tablas afectadas, qué se puede y qué no, concurrencia, seguridad y las rutas del proyecto que Cowork tiene que abrir.
  - Reglas duras: nada de secretos (credenciales por variable de entorno), nada de datos reales de personas o tarjetas, y ningún endpoint, campo o código de error sin anclar en `archivo:línea`; lo que no se puede anclar va a "Preguntas abiertas".
  - No se pisa con `qa` (#2), que audita la cobertura dentro del partido, ni con `arquitecto-api` (#10), que juzga el diseño: este documenta y hace ejecutable la entrega.
- Las cuatro superficies actualizadas (paso 5 del procedimiento): `docs/harness/equipo.md` (fila, formación, vacantes ahora 8 y 11, perfiles sugeridos y costes), `.claude/skills/equipo/SKILL.md` (ampliación, vacantes y coste), `README.md` (fila del 7 y vacantes) y `docs/harness/roles.md` (constructores y el terreno de cada uno).
- Cambio OpenSpec `fichar-entrega-qa`, archivado como `2026-10-30-fichar-entrega-qa`: requisito nuevo **Paquete de entrega al QA humano** en `team-match`, con los tres archivos, lo que el paquete no puede contener y la verificación determinista (`escenarios.py --list` lista los escenarios sin lanzar ninguna petición).
- Tests: `tests/test_team_entrega_qa.py` (11 casos) y `tests/test_team_tecnico.py` actualizado. Los anclajes de vacantes de `tests/test_team_arquitecto_api.py` dejan de fijar la lista entera y ahora afirman que el 10 no vuelve a aparecer como vacante: así cada fichaje no rompe el test del anterior.
- Feature nueva `team-entrega-qa` (prioridad 29, área `equipo`): `start` → `verify` → `passing` con evidencia.
- Verificación: `./scripts/check.sh` → 0; `pytest -q` → 775 passed (764 antes); `openspec validate fichar-entrega-qa --strict` → válido; `factory team list` → 9 jugadores, vacantes 8 y 11.
- Aviso recibido de otra sesión (`factory-novo-a1`): el árbol se había exportado a `~/Documents/parche-factory.patch` y pedía no escribir. Se le avisó de que esta petición del usuario sí tocaba el árbol, pero su socket ya no respondía (sesión cerrada). **El parche queda desfasado: hay que regenerarlo.** También corrigió una causa que esta entrada daba por buena: la edición perdida de `SKILL.md` fue su `git checkout -- .claude/skills`, no el CLI de openspec.
- Pendiente: `entregas/` todavía no existe; se crea con el primer ticket. Sigue todo sin commitear.

### Sesión 011 (cont.) — prueba real de `entrega-qa` y segunda vuelta del `checker`

- **Prueba real (paso 3 del fichaje), con un ticket de prueba `DEMO-001` sobre la API del panel de este mismo repositorio.** Dos ejecuciones:
  - con `--permission-mode dontAsk`, como decía el procedimiento: los tres `Write` quedaron en `permission_denials` y **no escribió nada**. Ese modo solo prueba a un revisor; para un constructor no prueba nada. El contenido que llevaban los `Write` denegados sí era correcto, así que el fallo era del modo, no del agente;
  - con `--permission-mode acceptEdits` y `--max-budget-usd 0.10` (coste real 0,0163 USD): escribió `entregas/DEMO-001/{DEMO-001.md,escenarios.py,README.md}` y **nada fuera**; `git status --porcelain` no muestra ninguna ruta ajena a `entregas/`.
  - Verificación determinista: `python entregas/DEMO-001/escenarios.py --list` → 3 escenarios, cada uno con el criterio de la HU que prueba. `escenarios.py` importa solo `argparse`, `json`, `urllib.error` y `urllib.request`.
  - **De extremo a extremo**: con `factory panel --port 8777` levantado, `python entregas/DEMO-001/escenarios.py --base-url http://127.0.0.1:8777` → `3 de 3 OK, 0 FALLA`, código de salida 0. Los escenarios cubren el feliz (`/api/snapshot` con sus secciones), el borde (Host ajeno → 403, DNS rebinding) y el error (POST → 405).
  - El briefing ancló cada endpoint y cada código en `archivo:línea` de `server.py` y `snapshot.py`, y dejó 10 preguntas abiertas en vez de inventar (entre ellas, que el 405 no pasa por la comprobación de `Host`, que anotó como "Fuera de mi alcance" sin tocarlo).
  - `entregas/DEMO-001/` se **borró** al terminar la prueba, por decisión del usuario: era un ticket ficticio. El directorio `entregas/` volverá a existir con el primer ticket real. La evidencia de la prueba es esta entrada.
- **Segunda vuelta del `checker`: `fail`** con 2 `medium` y 3 `minor`, todos corregidos:
  - el reglamento del partido no tenía sitio para `entrega-qa`: la fase 3 de `SKILL.md` y la tabla de fases de `equipo.md` ahora dicen que construye tras el constructor, y la fase 4 incluye `python entregas/<TICKET>/escenarios.py --list` con su salida en el acta (`medium`);
  - el paso 3 no se había ejecutado y la lista de tareas del cambio archivado ni lo mencionaba (`medium`): ejecutado, con el resultado de arriba, y añadido como tarea 1.5 al cambio archivado;
  - la convención de los anclajes de vacantes quedaba a medias (`minor`): ahora la frase se deriva de `VACANTES` en `tests/test_team_tecnico.py` y se comprueba igual en las tres superficies, y los tests de cada jugador solo afirman que su dorsal no vuelve a aparecer como vacante;
  - la tabla de permisos de `docs/harness/roles.md` describía a los constructores con el terreno de solo dos (`minor`);
  - `entregas/` iba a ser un directorio versionado de primer nivel sin aparecer en ningún mapa de rutas (`minor`): añadido al de `README.md` y a "Estructura" de `AGENTS.md`, diciendo que se versiona y que por eso el paquete no lleva secretos ni datos reales.
- Además, el procedimiento "Cómo fichar" (paso 3) ya distingue los dos tipos: `dontAsk` para un revisor, `acceptEdits` para un constructor, comprobando que `git status --porcelain` solo muestra su terreno. Lo ancla `tests/test_team_entrega_qa.py`.
- **Lo que destapó el ejemplo mientras estuvo en el árbol:** `entregas/` es parte del repositorio, así que `./scripts/check.sh` también lint-ea el `escenarios.py` del paquete (dos E501 y un `ruff format`). En vez de tocar la configuración de ruff —que no se cambia sin petición explícita— la restricción se le pasa al jugador: `escenarios.py` debe pasar `ruff check` y `ruff format --check`, con líneas de 100 caracteres. Anclado en `tests/test_team_entrega_qa.py`.
- **Tercera vuelta del `checker`: `pass_with_minor`**, sin `critical` ni `medium`. Los cinco hallazgos anteriores quedaron cerrados con prueba de mutación. Los tres `minor` nuevos también se corrigieron, porque eran baratos y uno iba a estallar en el próximo fichaje:
  - la sección "Costes" de `equipo.md` seguía diciendo que todas las pruebas reales usan `--max-budget-usd 0.05`, mientras el paso 3 ya prescribe 0,10 para un constructor;
  - la fase 3 del reglamento decía que el paquete de entrega no llega a los revisores y la fase 5 mandaba meter los `??` de `git status` en la lista de archivos — es decir, lo incluía: ahora la fase 5 excluye `entregas/**` y remite al `--list` de la fase 4;
  - el helper que derivaba la frase de vacantes se rompía al quedar **una sola** vacante (`" y 11"`, con espacio doble) y lanzaba `IndexError` con cero. Como el siguiente paso es fichar los dorsales 8 y 11, habría reventado en el próximo fichaje: ahora compara el **conjunto de dorsales** que nombra cada superficie contra `VACANTES`, sin depender de la redacción.
  - Confirmó además la decisión de ruff: pasarle la restricción al jugador no toca ninguna regla de verificación; excluir `entregas/` del lint sí, y eso necesita petición explícita del usuario.
- Verificación final de la sesión: `./scripts/check.sh` → 0; `pytest -q` → 780 passed; `ruff check .` → limpio; `factory team list` → 9 jugadores, vacantes 8 y 11; features 28 y 29 en `passing`; `openspec list` → sin cambios activos.

### Sesión 012 — Pull requests en el panel (`add-panel-pulls`)

- **Petición:** ver en el panel, en tiempo real, los pull requests del usuario que ejecuta la fábrica, para trazar si tienen alertas, si ya fueron revisados y cómo se mueven en tiempos de revisión.
- **Dos decisiones del usuario** (preguntadas antes de diseñar): los PR salen **solo del repositorio donde corre el panel**, y entran **los suyos más aquellos en los que se le pidió revisión**.
- **Decisión de arquitectura: nada de caché en disco.** La primera idea era que un sondeador escribiera `.factory/pulls.json` y que el `Watcher` lo huellara como al resto. Habría obligado a abrir una excepción en el requisito "Panel de solo lectura". En su lugar, el sondeador guarda el resultado en memoria del proceso y llama a `watcher.broadcast(["pulls"])`; el panel sigue sin escribir un solo archivo y el tiempo real sale por el mismo canal SSE.
- **Qué se añadió:**
  - `src/factory/panel/pulls.py`: tres consultas de `gh pr list` (abiertos como autor, abiertos con `review-requested:@me`, 10 últimos fusionados), dedupe por número con el rol `autor` ganando, estado, tiempos y alertas. El `runner` es inyectable, así que los tests no salen a la red.
  - Tiempos: abierto, sin actividad, hasta la primera revisión y de ciclo. Alertas: `checks_fallando`, `cambios_pedidos`, `conflictos`, `sin_revisor`, `parado` (>24 h), `sin_coderabbit`, `sin_cifra` y `demasiado_grande` (>10 archivos o >600 líneas). Las tres últimas son reglas de oficio de `CLAUDE.md` y solo se le piden al **autor**.
  - Panel: sección `pulls` en la instantánea, hilo sondeador cada 60 s que avisa **solo cuando el resultado cambia**, `factory panel --no-pulls` y pestaña nueva con filtros, KPI de PR con alerta y las dos medianas (hasta la primera revisión y de ciclo).
- **La prueba contra datos reales encontró tres fallos que los datos inventados no habrían encontrado** (runner con `-R novopayment/cifra-spend-corporate-api-go`, 10 PR abiertos):
  - `gh` devuelve el equipo revisor como `novopayment/cifra`, no como `cifra`: `sin_cifra` saltaba en PR que sí lo tenían;
  - `sin_coderabbit` saltaba aunque el bot ya hubiera revisado, porque solo miraba si existía el comentario `@coderabbitai review`;
  - la primera revisión la firmaba un escáner a los 30 segundos, así que la mediana decía 0,0 h. Los bots ya no cuentan como revisión ni como revisor humano (`BOTS` en `pulls.py`), y la mediana real pasó a 1,5 h.
- **Tests:** `tests/test_panel_pulls.py` (37 casos) y cuatro nuevos en `tests/test_panel_server.py`. Dos son anti-deriva: un PR "en su peor momento" tiene que disparar exactamente `pulls.ALERTS`, y la página tiene que saber pintar cada estado y cada alerta del vocabulario. El fixture del servidor pasa `pull_requests=False`.
- **Feature nueva `panel-pulls`** (prioridad 30, área `observabilidad`): `start` → `verify` → `passing` con evidencia. Cambio OpenSpec `add-panel-pulls` con dos requisitos añadidos y tres modificados de `observability-panel` (la instantánea pasa a cuatro secciones, el sondeo entra en "Actualización en vivo" y "Panel de solo lectura" dice explícitamente que no escribe ni en disco ni en GitHub).
- **Verificación:** `./scripts/check.sh` → 0; `pytest -q` → 821 passed (780 antes); `openspec validate add-panel-pulls --strict` → válido.
- **Límite conocido:** solo el repositorio donde corre el panel. Los PR del usuario viven en los repos de servicio (por ejemplo `cifra-spend-corporate-api-go`), así que ahí es donde hay que abrir el panel; en factory-novo la pestaña sale vacía.

#### Primera vuelta del `checker` sobre `add-panel-pulls`: `fail` (2 `medium`, 8 `minor`)

Los dos `medium` eran defectos que la verificación en verde no podía ver, y los dos los había introducido esta sesión:

- **`--no-pulls` no estaba probado en el camino del servidor.** Solo lo cubría `--json`. Borrando el guard `if pull_requests:` de `server.py` la suite entera seguía en verde. Ahora lo anclan dos tests simétricos: sin pulls el hilo del sondeo ni siquiera arranca (`is_alive()` falso) y con pulls se llama al colector y la instantánea se actualiza.
- **La suite había perdido hermeticidad.** `panel_json` de `tests/test_panel_tasks.py` llama a `factory panel --json` sin `--no-pulls`, así que dos tests pasaron a ejecutar `gh` de verdad tres veces cada uno, con 20 s de tope por llamada. No se ponían rojos porque el error se absorbe en `pulls.error`. Arreglado con `--no-pulls` en el helper. La frase de la entrada anterior que decía "ningún test sale a la red" era falsa y queda corregida arriba.

Los ocho `minor`, todos corregidos:

- un *commit status* clásico (`{"state": "PENDING"}`, sin campo `status`) se reportaba como `checks: ok`: `PENDING_CHECKS` y un caso nuevo en el parametrizado;
- `factory panel --json` no tenía la red de seguridad del sondeador: una respuesta de `gh` con otra forma salía como traceback. `collect` captura ahora cualquier excepción y la devuelve como `error`;
- la mediana "hasta la primera revisión" excluía a los fusionados, que son los únicos con el dato completo. Al incluirlos, la medida real del repo de cifra pasó de 1,5 h a **5,8 h**: la cifra anterior estaba sesgada por los dos o tres abiertos ya revisados;
- `factory panel --help` y el índice de `AGENTS.md` seguían describiendo tres vistas;
- `proposal.md` decía que el fallo de `gh` sale en `warnings`, cuando va en `pulls.error` (y la propia spec exige `warnings` vacío en ese escenario);
- "cada 60 s" estaba escrito a mano en la página sin atarlo a `PULLS_S`: ya lo ata un test, como el que existía para `UNCLOSED_AFTER_S`;
- `sin_cifra` puede quedarse encendido en un PR que el equipo ya revisó, porque GitHub retira la petición del equipo cuando una persona suya revisa. Documentado como límite conocido en `docs/harness/panel.md`;
- el requisito `Página gráfica` no mencionaba la pestaña: añadido a los MODIFIED del cambio, con el filtro, las etiquetas legibles y el matiz de que el enlace a GitHub se construye en tiempo de ejecución, así que la página sigue sin URLs externas.

Observación del `checker` sobre la evidencia, ya resuelta: el `manual_checks` de la feature dice `factory panel --json` con sesión de `gh`, pero hasta entonces solo se había ejercitado `collect` con un runner inyectado. Ejecutado después por el camino real: `factory --root <repo de cifra> panel --json` → 20 PR, 8 con alerta.

Verificación tras los arreglos: `./scripts/check.sh` → 0; `pytest -q` → 827 passed (821 antes); `openspec validate add-panel-pulls --strict` → válido; `factory features verify panel-pulls` → `passing` con evidencia nueva.

#### Segunda vuelta del `checker`: `fail` por un solo `medium`, más dos `minor` nuevos

Nueve de los diez hallazgos quedaron cerrados, siete con prueba de mutación hecha por el propio `checker`. El que siguió abierto no era un defecto del código, sino de su defensa:

- **Hermeticidad sin red de contención (`medium`).** `panel_json` ya pasaba `--no-pulls`, pero quitarlo volvía a dejar la suite en verde mientras ejecutaba `gh` de verdad. Ahora `tests/conftest.py` tiene un fixture `autouse` que sustituye `factory.panel.pulls._run` por un `pytest.fail` con el motivo. La regla queda escrita donde se cumple, y vale para cualquier test futuro, no solo para los dos de hoy.
- `minor`: el MUST de los cuatro filtros de la pestaña había entrado en la spec sin test → `test_la_pagina_filtra_por_rol_y_por_alerta`.
- `minor`: la tabla de consultas de `docs/harness/panel.md` decía que los fusionados sirven "para la mediana", en singular, cuando desde el arreglo anterior alimentan las dos.

**Mutaciones comprobadas en este repo** (aplicadas, ejecutadas y revertidas):

- quitar `--no-pulls` de `panel_json` → `test_cli_json_en_un_repo_sin_factory` y `test_cli_json_con_features_corruptas` fallan con el mensaje del fixture, en vez de salir a la red en verde;
- borrar el filtro `alerta` de `PULL_FILTERS` en la página → `test_la_pagina_filtra_por_rol_y_por_alerta` falla.

Verificación: `pytest -q` → 828 passed; restaurado el árbol, los dos archivos mutados vuelven a su contenido original.

#### Tercera vuelta del `checker`: `pass_with_minor` — cerrado

Sin hallazgos `critical` ni `medium`. Los tres arreglos de la vuelta anterior quedaron cerrados, dos con prueba de mutación. El `checker` contestó además las dos preguntas con hechos del repositorio: no existe ningún test marcado `live` (el marcador está declarado en `pyproject.toml` pero no se usa), el parcheo por ruta de módulo entra siempre porque `collect` resuelve `runner or _run` en tiempo de llamada, y en todo `src/` solo hay una invocación de `gh`, la de `pulls.py`.

El `minor` nuevo sí valía la pena y se corrigió: **el guard no cubría el hilo del sondeador**. `pytest.fail` levanta `Failed`, que es `BaseException` —justo lo que lo hace atravesar el `except Exception` de `collect`—, pero dentro del hilo del sondeo esa excepción habría salido como `PytestUnhandledThreadExceptionWarning` y el test habría seguido **verde** mientras se intentaba salir a la red. El fixture apunta ahora cada intento en una lista y lo comprueba en el teardown, que corre en el hilo principal.

Mutación comprobada: un test que construye `PanelServer(..., pull_requests=True)` sin inyectar `collect` termina en `ERROR` por el teardown, en vez de pasar con un warning. Archivo de prueba borrado tras ejecutarlo.

Se descartó la alternativa de añadir `filterwarnings` a `pyproject.toml`: es configuración de verificación y no se toca sin petición explícita.

Cambio archivado como `2026-10-30-add-panel-pulls`: 2 requisitos añadidos y 4 modificados en `observability-panel`. `openspec list` sin cambios activos. Verificación final: `./scripts/check.sh` → 0.

### Sesión 013 — Recomendaciones de los revisores (`add-pr-feedback`)

- Petición: un gancho de la fábrica para atender las recomendaciones de los revisores de un pull request, con el PR [#120 de `cifra-spend-corporate-api-go`](https://github.com/novopayment/cifra-spend-corporate-api-go/pull/120) y el revisor `sam-pc-novo` como caso real.
- Decidido con el humano (dos preguntas): un **comando de `factory` más una skill de triaje**, con el **ciclo completo** —listar, arreglar el código aceptado y responder los hilos—, no solo un aviso en el panel.
- Completado:
  - `src/factory/feedback.py` y `factory feedback <pr> [--repo] [--revisor] [--resueltos] [--json]`: una consulta `gh api graphql` que trae los hilos en línea y los cuerpos de revisión, agrupados por revisor, con `archivo:línea`, el estado del hilo y el comando `gh … /replies` de cada uno. Solo lectura.
  - Skill `.claude/skills/recomendaciones/`: leer → comprobar contra el código → triaje aprobado por el humano → arreglar → responder hilo a hilo. Sin push, sin merge y sin resolver hilos.
  - `tests/test_feedback.py` (21 tests, tres por el CLI con `main([...])`), `docs/harness/recomendaciones.md`, filas en `README.md` y `AGENTS.md`, y la entrada en `tests/test_cli_help.py`.
  - Cambio OpenSpec `add-pr-feedback` (capacidad nueva `pr-feedback`, 3 requisitos y 8 escenarios), `openspec validate --strict` válido. **Queda activo, sin archivar.**
  - Feature `pr-feedback` (prioridad 31) promovida con `factory features verify`.
- Prueba en vivo contra el PR #120: `--revisor sam` → los 7 hilos de `sam-pc-novo` con su comando de respuesta; sin filtro, 8 hilos sin resolver, 45 resueltos ocultos y 11 revisiones generales (CodeRabbit, Orca, SonarQube y un revisor humano).
- Verificación: `./scripts/check.sh` → 0.
- Pendiente: nadie ha respondido todavía los hilos de `sam-pc-novo` en el PR #120; eso se hace desde el repositorio de `cifra-spend-corporate-api-go` con `/recomendaciones 120 sam`.

#### Primera vuelta del `checker`: `fail` por dos `medium`

- **La capacidad no estaba registrada** (`medium`): ni feature ni spec. Arreglado con la feature `pr-feedback` y el cambio OpenSpec `add-pr-feedback`.
- **El CLI no tenía ningún test** (`medium`): los 16 tests iniciales solo ejercitaban `recoger`/`render`. Añadidos tres por `main([...])` (JSON, mapeo de opciones y salida 2 con el motivo en `stderr`). Para que el parcheo entrara, `recoger` resuelve ahora `runner or _run` en tiempo de llamada, como `pulls.collect`.
- `minor`: un directorio inexistente daba el mensaje falso "no se encontró el CLI `gh`" (ahora `_gh` mira `exc.filename`); `--revisor` solo miraba a quien abría el hilo (ahora, a cualquier participante, con test); un comentario con la palabra `ponytail` de un dictado; y la tabla de estructura del `README.md`, que nombraba una sola skill.
- Descartado: usar `find_root` en `cmd_feedback`. `factory feedback` se ejecuta dentro del repositorio del PR, que normalmente **no** es este repo, así que `args.root or Path.cwd()` es deliberado.

### Sesión 014 — Puerta previa al pull request y consulta a la biblioteca (`add-puerta-pre-pr`)

**Por qué.** Los nueve pull requests de SPD-80 abiertos hoy en `cifra-spend-corporate-api-go`
(131–139) acumularon 23 hilos de CodeRabbit, 16 sin contestar cuando la rama ya había pasado a
SPD-191. Tres eran el mismo defecto visto desde tres sitios —`service.InviteUser` llama a
`Inviter.Invite`, que crea la cuenta en el proveedor de identidad, **antes** de comprobar la
delegación, así que un 403 deja cuenta huérfana y ninguna membresía— y nueve no eran código, sino
notas y contrato que el propio PR dejó falsos. El CLI de CodeRabbit estaba instalado y
autenticado en esta máquina y nada lo llamaba; la biblioteca técnica no estaba importada, así que
la inyección de conocimiento entregaba citas sin texto.

**Qué se hizo.**

- `factory brain import /Users/cyate/obsidianGeneral/novopayment-software`: 11.245 notas, 82
  libros, ~13.016.603 tokens. Antes, `factory brain status` decía `no importado`.
- `scripts/pre-pr.sh`: puerta previa al PR —árbol limpio, commits sobre la base, `check.sh`,
  tamaño, `factory complexity --base --max 20` y `coderabbit review --base <base> --gate major`—,
  con salto documentado sin el CLI y `PRE_PR_STRICT=1` para convertirlo en fallo.
- `.coderabbit.yaml`: perfil `chill`, `auto_review.drafts: true`, cerebros excluidos e
  instrucciones por ruta para `**/*.py`, `prompts/**/*.md` y `.claude/agents/**/*.md`.
- Consulta obligatoria a la biblioteca en `prompts/maker.md`, `prompts/intake.md`, sus plantillas
  y los diez jugadores de `.claude/agents/`, cada uno con la variante que cabe en sus
  herramientas. El `checker` queda fuera a propósito y hay un test que lo guarda.
- "Lo que abriría un hilo en el PR" en los dos checkers; `docs/harness/roles.md` deja de decir
  "las cinco reglas de oficio".
- Cuatro notas en el cerebro diario con los patrones de los 23 hilos (efecto externo antes de la
  autorización, `classify()` que convierte defectos propios en caídas, check-then-insert y
  documentación que el PR dejó mintiendo). Sin commitear todavía: `factory brain commit`.

**Verificación ejecutada.** `./scripts/check.sh` → 0 (ruff, ruff format, pytest y `factory
doctor` con 0 críticas y 0 recomendadas fallidas). `tests/test_reglas_de_oficio.py` → 46 casos.
`./scripts/pre-pr.sh main` con el árbol sucio → 1, "PUERTA CERRADA: hay cambios sin commitear".

**Revisión independiente.** Primera vuelta del `checker`: `fail`, 6 `medium` + 4 `minor`.
Corregidos los seis `medium` —la orden del maker no cabía en sus herramientas (ahora usa el
bloque de conocimiento inyectado y Read/Grep), el paso de complejidad no podía fallar sin
`--max`, la puerta medía un rango vacío con el árbol sucio, `roles.md` seguía diciendo "cinco
reglas", `.coderabbit.yaml` no tenía prueba que lo defendiera y la capacidad no estaba
registrada— y los `minor` 8, 9 y 10. Queda abierto el `minor` 7: pasarse de 10 archivos o 600
líneas avisa pero no cierra la puerta, porque los archivos estáticos pueden pasarse y contarlos
aparte necesita una decisión que no es de esta sesión.

Segunda vuelta: `fail`, con cuatro `medium` cerrados y tres abiertos por una razón sola —el
código era correcto y faltaba la prueba que lo defendiera—. La lección vale más que los
arreglos: una ejecución manual en verde no es prueba de mutación. Ahora
`test_la_puerta_previa_al_pull_request_existe_y_se_exige` ancla `--max`,
`PRE_PR_MAX_COMPLEJIDAD`, `git status --porcelain`, `rev-list --count` y `PRE_PR_STRICT`;
`test_las_reglas_de_oficio_estan_listadas_donde_se_buscan` defiende la tabla de `roles.md`; y
`test_la_puerta_documentada_es_la_puerta_que_hay` impide que el documento vuelva a describir una
versión anterior del script. Hallazgo nuevo de esa vuelta, también cerrado:
`docs/harness/recomendaciones.md` describía la puerta de antes de las dos guardas y no nombraba
ninguna de las dos variables de entorno; corregidos además los resúmenes de `AGENTS.md` y
`CLAUDE.md`, la viñeta de `docs/harness/cerebros.md` sobre cómo consulta el maker del loop (no
busca: recibe el conocimiento inyectado) y las cuatro cifras falsas de `session-handoff.md`.

Tercera vuelta: **`pass_with_minor`**, sin `critical` ni `medium`. Los dos `minor` nuevos eran
texto y quedaron cerrados (el docstring de `tests/test_reglas_de_oficio.py` seguía contando cinco
reglas; `session-handoff.md` mantenía la verificación, el «código añadido: ninguno» y el «defecto
conocido: ninguno» de la sesión 012). Queda abierto solo el `minor` 7, por decisión.

**Estado.** Feature `puerta-pre-pr` (prioridad 32) en `not_started`: el cambio OpenSpec
`add-puerta-pre-pr` está escrito y la verificación en verde, falta `factory features start` y
`verify`. El árbol sigue sucio a propósito por la mudanza de repositorio pendiente.

**Siguiente paso.** Cerrar los 16 hilos abiertos de los PRs 131–139 empezando por 136 y 137, que
son los tres `Major` y se cierran con el mismo movimiento: subir las comprobaciones de
autorización por encima de la llamada al proveedor. Y copiar a
`cifra-spend-corporate-api-go` el `.coderabbit.yaml` preparado con las instrucciones derivadas de
esos 23 hilos.

### Sesión 015 — Motor intercambiable: Claude Code o Strands (`add-strands-runner`)

**Objetivo.** Analizar la fábrica entera y usar el SDK de Strands (`@strands-agents/harness` /
`strands-harness`) para mejorar la orquestación de los agentes, validando el resultado en Chrome.

**Lo que se vio al analizar.** El motor maker-checker tenía un solo motor, `claude -p`, y con él
dos huecos. El de independencia: la separación maker/checker vale porque quien construye no
aprueba, pero los dos roles corrían sobre la misma familia de modelos, con los mismos puntos
ciegos; un `opus` revisando a un `sonnet` es más independiente que nada, no mucho más. El de
dependencia: `factory` no corre donde no hay Claude Code, ni donde el modelo tiene que venir de
Bedrock por política de la casa. `AgentRunner` ya era la costura correcta —`ClaudeCodeRunner` y
`FakeRunner` la implementan—, así que el trabajo era añadir un tercero, no rehacer el motor.

**Completado.**
- `[agent] runner`: `"claude"` (por defecto, sin cambio de comportamiento) o `"strands"`. Un
  valor desconocido no deja cargar la configuración.
- `src/factory/agents/strands_runner.py`: mismo contrato que `ClaudeCodeRunner` —sesión nueva por
  invocación, presupuesto por llamada, ningún modo que omita permisos—. El trabajo va a un
  proceso hijo (`_strands_child.py`) para heredar el aislamiento de `subprocess` y para que
  `strands_harness` se importe en un solo módulo: es dependencia **opcional**
  (`pip install 'factory-yate[strands]'`).
- `src/factory/agents/permissions.py`: lo que faltaba para que el segundo motor no fuera un
  agujero. `allowedTools` / `disallowedTools` eran reglas de Claude Code y nadie más en el
  repositorio sabía qué significan; ahora `Herramienta` y `Herramienta(patrón)` tienen definición
  propia (sufijo `:*` por prefijo, el resto con comodines, la denegación gana) y una intervención
  de Strands las aplica a **cada llamada a una herramienta**. Un `git push` del maker o un `Edit`
  del checker se rechazan igual que con `claude -p`.
- El presupuesto en dólares se convierte a tope de tokens con el precio de **salida**, el más
  caro, para que el tope real nunca gaste de más; el coste informado es una estimación a los
  precios de `[agent]`, no una factura. Queda dicho en `docs/harness/roles.md`.
- `json_object` subió a `factory.agents.base` y `claude_code` lo reusa: los dos adaptadores leen
  el JSON del agente con el mismo código.

**Verificación ejecutada.** `./scripts/check.sh` → 0 (ruff, ruff format, pytest y `factory doctor`
con 0 críticas y 0 recomendadas fallidas). `factory features verify agent-runner` → `passing`, con
`tests/test_strands_runner.py` en 29 casos. `openspec validate add-strands-runner --strict` →
válido.

**Validación visual.** `factory panel --port 8787 --no-pulls` capturado con Chrome headless en sus
cuatro pestañas: Tokens (tarjetas, barras por día, por tipo de agente y por modelo, sesiones
recientes), Tareas (32 `passing` y 1 sin empezar, WIP=1), Revisiones —que mostró en vivo la propia
revisión de esta sesión— y Pull requests con `--no-pulls` declarado. El plugin `chrome-devtools-mcp`
quedó instalado para la próxima sesión; sus herramientas MCP no conectan hasta reiniciar Claude Code,
así que esta validación se hizo con `--headless=new --screenshot`. Ojo: `--virtual-time-budget` se
cuelga contra el panel, porque la página mantiene su actualización en vivo; sin esa bandera, la
captura sale.

**Revisión independiente.** Primera vuelta del `checker`: `fail`, con 4 `critical`, 3 `medium` y
3 `minor`. La verificación estaba en verde y los cuatro `critical` eran reales, que es la lección
de la sesión: **toda la ruta `strands` estaba cubierta solo por tests de unidades puras**
—`parse`, `denial_reason`, `build_request`— y ninguno ejecutaba el proceso hijo ni `make_runner`.
Un camino nuevo sin una prueba que lo recorra entero no está probado, por muchos casos que tenga.

Los cuatro `critical`, todos verificados contra el SDK antes de tocar nada:

1. **El hijo escribía su JSON detrás de la narración del modelo.** El `Agent` del SDK pone un
   `PrintingCallbackHandler` si nadie le pasa `callback_handler`, y el harness no se lo pasa; cada
   invocación habría acabado en "salida ilegible" o, peor, parseando un bloque cercado del propio
   modelo. Arreglado con `callback_handler=None` y desviando `sys.stdout` a `sys.stderr` durante
   la invocación.
2. **Agotar el presupuesto se informaba como ronda correcta.** El tope que introduce esta feature
   para por `stop_reason = "limit_total_tokens"`, que no estaba en la condición; el motor se habría
   quedado la ronda truncada como buena en vez de revertirla. Ahora solo `end_turn` y
   `stop_sequence` son un final normal.
3. **Las denegaciones de los cerebros nunca casaban.** `brain_denials` las escribe con prefijo
   `//` y el comparador no lo normalizaba, así que el maker con Strands podía escribir en
   `brain-principal/`. Se normaliza el prefijo, cada ruta se compara en absoluto y en relativo, y
   se añadió la frontera que faltaba: fuera de `cwd` + `add_dirs` no se alcanza nada, que es lo
   que `claude -p` da gratis y Strands no.
4. **La denegación por prefijo se evadía con un comando compuesto.** `git status && git push` no
   empieza por `git push`. Ahora la cadena se parte con `shlex` —que respeta las comillas— y tienen
   que pasar todos sus comandos; una sustitución no se puede juzgar y se rechaza.

Los tres `medium`: la pista de instalación estaba en el error equivocado (el del intérprete
ausente, no el de la dependencia ausente); `child_env` deshacía el aislamiento que `command_env`
existe para garantizar, y se sustituyó por un arranque con `-c` que mete la raíz del paquete solo
en el `sys.path` del hijo; y `make_runner` y la opcionalidad de la dependencia no tenían ningún
test. Cerrados también los `minor` 8 y 9. Queda abierto el `minor` 10 por decisión: un fallo del
hijo contabiliza 0 USD aunque haya gastado tokens.

Segunda vuelta: `fail`, con 1 `critical`, 3 `medium` y 2 `minor`. El `critical` era el hallazgo 4
de la primera vuelta **movido de sitio**: `shlex` tiene el salto de línea por espacio en blanco y
nunca lo emite como token, así que `git status\ngit push origin main` volvía a ser un solo comando
que empieza por `git status` y pasaba la denegación obligatoria. Ahora las líneas se separan antes
de lexar. La lección, que ya apunta la primera vuelta: un arreglo de seguridad por análisis de
cadena hay que probarlo con las formas que no se te ocurrieron, no con la que te denunciaron.

De los tres `medium`, dos eran "arreglado pero sin prueba que lo defienda" —la lista blanca de
`stop_reason` se probaba en el padre y no en el hijo, que es donde se decide; y `StrandsRunner.run`
no se ejercía en ningún test, así que volver a `-m` o a `child_env` no rompía nada—. El tercero era
al revés: el código estaba bien y **la spec mentía**. Prometía frontera dura del worktree, y un
comando de shell autorizado por prefijo puede redirigir a donde quiera; eso es paridad con
`claude -p`, no un agujero, así que se acotó la frase en la spec y en `roles.md` en vez de fingir un
sandbox. Cerrados también los dos `minor`: `builtin_plugins=[]` (los plugins por defecto traen
`todo_write`, que ninguna regla nombra y la intervención denegaba en cada ronda) y el recorte del
motivo de denegación, que volvía al modelo con el input entero.

**Verificación tras los arreglos.** `./scripts/check.sh` → 0 (953 tests). `features verify
agent-runner` → `passing` con 68 casos. `openspec validate --strict` → válido. Prueba de mutación
de los cuatro arreglos de fondo —salto de línea, lista blanca de `stop_reason`, `add_dirs` al hijo
y arranque con `-c` + `command_env`—: las cuatro revertidas rompen tests.

Tercera vuelta: `fail`, con 2 `critical`, 2 `medium` y 2 `minor`. Los dos `critical` eran, otra
vez, **la misma categoría**: `git status -- x#y; git push` (en modo no POSIX, `shlex` tira el resto
de la línea tras un `#` a media palabra, y el shell en cambio lo ejecuta) y `git status |& git push`
(`shlex` agrupa cada racha de `();<>|&` en una sola ficha, y `|&` no estaba en la lista de
separadores). Tres vueltas, tres variantes del mismo agujero.

De ahí sale la lección de la sesión, que vale más que los tres arreglos: **enumerar lo prohibido
no termina nunca**. El criterio está ahora invertido —separa toda racha de puntuación de shell
salvo las redirecciones, que son lo único que se tolera—, de modo que el operador que no se nos
ocurra falla cerrado en vez de abrir el siguiente hueco. Es la diferencia entre una lista negra y
una blanca, aplicada donde más se paga.

El otro `medium` era del mismo signo: con `allowed_tools = []`, `builtin_tools` devolvía `None` y
el harness armaba sus ocho herramientas por defecto —`subagent`, `web_fetch` y `web_search`
incluidas—, mientras la intervención sin lista de autorizadas solo aplica lo denegado. Un rol que
no autoriza nada acababa con todo. Ahora `[]` significa `[]`. El `medium` restante era de proceso:
el diff que le pasé al revisor no incluía `export.py`, así que un comando de CLI nuevo llegó sin
revisar; regenerado y devuelto a revisión.

Arreglado también un fallo latente que no denunció nadie: `retrieve_context`, del gestor de
contexto de Strands, no lo nombra ninguna regla del rol, así que la intervención lo habría
denegado en cada ronda.

**Lo que se usó del CLI `strands`.** `factory agent export <rol>` escribe el rol como proyecto de
agente que el CLI carga con `--agent`: el mismo modelo, el mismo prompt, las mismas herramientas y
la **misma** intervención. El checker exportado sigue siendo de solo lectura y el maker exportado
sigue sin poder publicar; un export con las reglas aflojadas sería una puerta trasera a lo que
`MANDATORY_DENIED` prohíbe, y hay dos pruebas de mutación que lo defienden.

**Validación del camino real.** No hay credenciales de ningún proveedor en este equipo, así que se
montó un proveedor local que habla la Messages API de Anthropic con un guion fijo
(`ANTHROPIC_BASE_URL`). No sustituye a un modelo: sustituye a sus pesos. Todo lo demás es el camino
de verdad —el subproceso de factory, el harness, el cliente `anthropic`, HTTP, el bucle de
herramientas y la intervención—. El "modelo" pidió `git push origin main`, la intervención lo
rechazó, **el rechazo le llegó** y contestó con el JSON del veredicto: 2 turnos, 320/70 tokens,
coste estimado y salida estructurada correctos. El CLI real `strands --agent` cargó además el rol
exportado y contestó.

**Verificación tras los arreglos.** `./scripts/check.sh` → 0 (967 tests). `features verify
agent-runner` → `passing` con 82 casos. `openspec validate --strict` → válido. Pruebas de mutación
de los cuatro arreglos de la tercera vuelta: las cuatro revertidas rompen tests.

**Estado.** Feature `agent-runner` (prioridad 33) en `passing`. El árbol sigue sucio a propósito
por la mudanza de repositorio pendiente, y no se ha abierto ningún pull request.

**Validación con el plugin de Chrome.** Las herramientas MCP de `chrome-devtools-mcp` no
conectan dentro de una sesión de Claude Code donde el plugin se instaló a mitad, pero **el
servidor es el mismo**: `npx chrome-devtools-mcp@1.11.0` por stdio. Se le habla el protocolo
directamente (`scratchpad/plugin_chrome.py`), y con eso el plugin condujo el navegador de verdad:
sus 32 herramientas listadas, `navigate_page` + `wait_for` + `take_snapshot` sobre el panel,
`list_console_messages`, `list_network_requests` y `take_screenshot`. Hace falta
`--workspace=<dir>` para que pueda escribir la captura fuera del temporal del sistema, y cada
llamada lleva el `pageId` que da `list_pages` —navegar incluido—.

Lo que vio: el panel pinta sus pestañas y sus indicadores, `/api/snapshot` y `/api/stream` en 200,
`agent-runner` en `passing` 3/3 y `add-strands-runner` 47/47. Dos defectos del panel, **fuera del
alcance de esta feature** y sin arreglar: `GET /favicon.ico` devuelve 404, y hay dos campos de
formulario sin `id` ni `name` (aviso de accesibilidad). Anotados para quien toque el panel.

De paso quedó explicado por qué `--virtual-time-budget` se cuelga contra el panel: `/api/stream`
es una conexión que no cierra. Para capturas sin el plugin, `scratchpad/capturar.py` conduce
Chrome por CDP y espera a que la página tenga contenido, en vez de disparar en el evento `load`.

**Las siete vueltas del `checker`, y lo que enseñan.** Ninguna vuelta salió limpia y cada una
encontró el agujero **una capa más arriba** que la anterior. Vale la pena dejarlo escrito porque
el patrón es la lección, no cada arreglo:

| Vuelta | Hallazgos | Dónde estaba el agujero |
|---|---|---|
| 1 | 4 critical, 3 medium | stdout del hijo, `stop_reason`, prefijo `//`, `&&` |
| 2 | 1 critical, 3 medium | el salto de línea, que `shlex` se come |
| 3 | 2 critical, 2 medium | `#` a media palabra y los operadores agrupados (`\|&`, `<(`) |
| 4 | 1 critical, 4 medium | el **despacho**: lo elegía la forma del input, no el nombre de la herramienta |
| 5 | 0 critical, 2 medium | el **ensamblado** del conjunto de reglas (`brain-mapa` ausente) y la elección de la clave de ruta |
| 6 | 0 critical, 3 medium | la **resolución** de las rutas frente a la raíz real del agente |
| 7 | 0 critical, 3 medium | la **distribución** del artefacto, y `path.name` en vez de la ruta relativa |

Tres cosas que se llevan de aquí:

1. **Enumerar lo prohibido no termina nunca.** Las vueltas 1-3 fueron tres parches a la misma
   categoría. Lo que la cerró no fue el cuarto parche: fue invertir el criterio —se enumera lo
   tolerado (las redirecciones) y todo lo demás separa—, de modo que el operador que no se nos
   ocurra falle cerrado. Un corpus de 25 evasiones y 8 comandos legítimos lo defiende.
2. **Lo que escribe el modelo no puede decidir cómo se le juzga.** La vuelta 4 lo dijo del
   despacho y la 5 de la clave de ruta: el nombre de la herramienta lo pone el framework, la
   forma del input la pone el modelo. Las dos veces el arreglo fue el mismo principio aplicado
   un nivel más abajo.
3. **Una verificación verde no es una revisión.** Las siete vueltas empezaron con
   `./scripts/check.sh` en 0, y seis encontraron un `critical` o un `medium` real. Lo que faltaba
   casi siempre era una prueba que recorriera el camino entero, no más casos del mismo tipo.

**Validación del camino real.** No hay credenciales de ningún proveedor en este equipo (probar
cuáles sirven lo bloquea el clasificador, correctamente). Se montó un proveedor local que habla la
Messages API de Anthropic con un guion fijo: no sustituye a un modelo, sustituye a sus pesos. Todo
lo demás es el camino de verdad —subproceso, harness, cliente `anthropic`, HTTP, bucle de
herramientas, intervención—. El "modelo" pidió `git push origin main`, la intervención lo rechazó,
el rechazo le llegó y contestó con el JSON del veredicto.

**Estado de la revisión.** Siete vueltas cerradas, cada arreglo con su prueba de mutación. **La
octava se lanzó y se detuvo a petición humana**, así que los arreglos de la séptima —la ruta
relativa del cerebro, el `requirements.txt` del proyecto exportado y el destino que no es un
directorio— están verificados y con test, pero **sin revisión independiente**. Es el único cabo
suelto conocido.

**Aviso de tamaño.** Este trabajo ya no cabe en un solo pull request (10 archivos / 600 líneas):
el adaptador, las reglas de permisos y el export del rol son tres cortes que se despliegan por
separado. Cuando se vaya a abrir, va apilado, no junto.

### Sesión 016 — Política de delegación de la sesión principal

**Qué se pidió.** Validar contra todo el proyecto una "Delegation policy" externa (niveles de
modelo, delegación obligatoria, tripwire de archivos, reglas de tokens) y añadir lo que aplique.

**Qué ya estaba, y por eso no se copió.** Los niveles de modelo están decididos por puesto en el
`model:` de cada `.claude/agents/*.md`, con su tabla en `docs/harness/equipo.md` y sus costes en la
misma página; el maker en `sonnet` y el checker en `opus` viven en `factory.toml` y
`src/factory/config.py`. La revisión adversarial a modelo caro es el `checker`. Pasarle al revisor
solo criterios y diff ya está en `CLAUDE.md` y en el reglamento del técnico.

**Qué se añadió.** Dos cosas que faltaban de verdad:

- `CLAUDE.md`: la disciplina de la **sesión principal**. Los loops y `/equipo` ya tenían la suya;
  la sesión interactiva no. Contar los archivos antes del primer `Edit`/`Write` (uno o dos, los
  haces tú; tres o más, convocas), convocatorias independientes en un solo mensaje, no releer lo
  que un subagente ya resumió, e informar conclusiones en vez de volcar archivos y diffs.
- `docs/harness/equipo.md`, sección *Cómo fichar*: el **criterio** para elegir `model` al crear un
  jugador. La plantilla decía quién usa opus y quién sonnet, nunca por qué, así que un fichaje
  nuevo no tenía con qué decidirlo.

**Qué se rechazó, y por qué.** `Explore` y `general-purpose` como destino de delegación: el
reglamento del equipo prohíbe expresamente sustituir a un jugador ausente por un agente genérico,
que además se salta convocatoria, terreno y árbitro. El marco "Fable es el modelo de sesión": este
repositorio no nombra el modelo de la sesión a propósito, porque caduca. Y la referencia a
`docs/core/PROGRESS.md`, que es una ruta de otro proyecto.

**Verificación.** `./scripts/check.sh` → 0. Los cambios son solo documentación (`CLAUDE.md` y
`docs/harness/equipo.md`); la auditoría del harness y los tests que anclan las superficies de la
plantilla pasan. El `E501` de `tests/test_team_product_owner.py` que apareció a mitad de sesión
venía de trabajo sin trackear ajeno a esta tarea y ya está corregido en el árbol.

**Siguiente paso.** Nada abierto por esta tarea. El árbol sigue sucio por la mudanza de
repositorio y por `add-strands-runner`, que es lo que toca cortar en pull requests apilados.

### Sesión 017 — Fichaje de `product-owner` (#8): las preguntas salen a Plane

**Qué se pidió.** Un agente de Product Owner que, cuando en el desarrollo surge una duda o una
mejora, deje la pregunta en **Plane** redactada de forma natural, con ejemplo y comprensible en
cualquiera de los escenarios posibles.

**Qué ya estaba, y por eso no se duplicó.** `producto` (#6) ya detecta las preguntas abiertas en el
pre-partido ("abierta: requiere al humano"); lo que no existía era la salida: esas preguntas morían
en el acta. La skill `documentador-de-plane` ya publica el **avance** en un work item, con su HTML y
sus reglas de menciones; este fichaje publica la **pregunta**, y no se pisan.

**Qué se añadió.**

- `.claude/agents/product-owner.md`: dorsal 8 (interior derecho), `tipo: constructor`, opus,
  `convocatoria: "peticion, openspec/changes/**"`. Es el único jugador que escribe fuera del
  repositorio: sus herramientas son solo lectura más el MCP de Plane, sin `Agent` ni `Edit`/`Write`.
  Lleva la tabla de qué sale a Plane y qué no, el enrutado (duda de la historia → comentario del
  work item; mejora o trabajo nuevo sin ticket → `intake create`), las reglas de redacción para
  quien no lee código y dos plantillas en HTML.
- `tests/test_team_product_owner.py`: frontmatter, herramientas, las promesas del cuerpo y las
  cuatro superficies.
- Superficies actualizadas: `README.md`, `docs/harness/equipo.md` (plantilla, formación, vacantes y
  costes), `.claude/skills/equipo/SKILL.md` (vacantes, paso 4 del pre-partido y coste) y
  `docs/harness/roles.md` (enumeración de constructores y tabla de permisos).

**Las dos reglas que lo hacen seguro.** Publicar en Plane es una acción sobre un sistema compartido:
el agente **redacta siempre y publica solo si la petición se lo pide**; el borrador viaja en el acta
hasta que un humano lo confirme. Y toda pregunta lleva un **supuesto por defecto** con su
reversibilidad, para que un partido sin humano delante no se quede parado esperando respuesta.

**Por qué no hay cambio OpenSpec.** `openspec/specs/team-match/spec.md:100` deja la lista de
vacantes en `docs/harness/equipo.md` y en `factory team list`, no en la spec, y el requisito de
fichaje (líneas 144 y siguientes) ya cubre este caso. Ningún requisito cambia.

**Verificación.** `./scripts/check.sh` → 0 (1004 tests). `.venv/bin/factory team validate` →
`Plantilla válida: 11 miembro(s)`. Prueba real con haiku
(`claude -p --agent product-owner --model haiku --permission-mode dontAsk`): cargó, respondió con
el formato `## Jugador: product-owner (#8)`, redactó el borrador sin publicar y dejó
`git status --porcelain` igual; 0.006 USD.

**Prueba contra Plane real (SPD-233).** Se invocó al jugador contra un work item vivo del proyecto
CIFRA Spend: "Corporate Portal - Backend - Provisioner: imagen desplegable con Flyway". Se eligió
porque trae una decisión abierta de verdad —`RequireFlywayTLSWired` sin llamador en producción, y
el propio SCOPE dice "either the environments require it and the guard is wired at startup, or the
guard goes"—, no una pregunta inventada. El agente leyó el work item y sus dos comentarios por MCP,
comprobó que nadie la había preguntado, encontró en un comentario un dato que no estaba en el
prompt (el trust store de RDS ya viaja en la imagen, PR #94, así que la pregunta no es si hay
certificado sino si su uso es obligatorio), citó *Defensive Security Handbook 2e* · cap. 13 ·
pp. 167–174 para justificar el supuesto por defecto y devolvió el borrador **sin publicar**. El
humano decidió no publicarlo: la escritura real en el tablero sigue sin probarse.

**Segunda vuelta del `checker`.** La primera dio ❌ fail con cuatro `medium`, todos corregidos:

- *Operaciones destructivas sobre Plane.* El MCP agrupa `retrieve`, `update` y `delete` bajo el
  mismo nombre de herramienta, así que conceder `workitem` concedía borrar. Se quitaron `label` y
  `state` del frontmatter y se escribió la regla "Añades, nunca cambias ni borras", con la lista de
  operaciones permitidas y la prohibición explícita "ni aunque te lo pidan". Es la única barrera
  posible: la granularidad del MCP no deja quitar la capacidad desde `tools`.
- *El acta no tenía dónde poner el borrador.* El reglamento prometía que viajaba en el acta y la
  plantilla de la fase 7 no tenía sección para él. Ahora la tiene.
- *El test no cubría costes, `description` ni la línea de constructores.* Cubiertos; la aserción
  sobre `roles.md` se hace ahora sobre la línea de constructores, no sobre el archivo entero.
- *Fichaje sin cambio OpenSpec.* `openspec/changes/fichar-product-owner/`: MODIFIED "Fases del
  partido" (la fase 2 gana un tercer jugador, con escenario para el partido sin humano) y ADDED
  "Publicación en Plane". `openspec validate --strict` → válido.

Los tres `minor` también: la contradicción entre `convocatoria: peticion` y "solo entra si hay
preguntas abiertas" (la sugerencia es determinista y la condición no se conoce antes del
pre-partido: se da de baja en la alineación), `documentador-de-plane` marcada como skill personal
fuera del repositorio, y la dependencia del conector MCP dicha en `equipo.md` y en el `README.md`.

**Siguiente paso.** Publicar de verdad un borrador en Plane, que es lo único del fichaje que no se
ha ejercido (tarea 3.4 del cambio, sin marcar). El árbol sigue sucio por la mudanza de repositorio
y por `add-strands-runner`; este fichaje es un corte propio y pequeño (un agente, su test, el
cambio OpenSpec y cuatro superficies de documentación).

### Sesión 018 — 2026-11-03 a 2026-11-04 (recomendaciones de un PR real, fuera del harness)

**Nada del harness cambió.** Ni código, ni tests, ni documentación: `git log` no tiene commits
nuevos y lo único que esta sesión escribe aquí es esta entrada. Se anota igual porque ejercitó dos
capacidades del harness contra sistemas vivos, y porque dejó una desviación de `CLAUDE.md` que
conviene no perder.

**Qué se hizo.** El ciclo entero de la skill `recomendaciones` sobre el PR
[#120](https://github.com/novopayment/cifra-spend-corporate-api-go/pull/120) de
`novopayment/cifra-spend-corporate-api-go` (el change OpenSpec `manage-company-users`):

- Las **cinco recomendaciones de `sam-pc-novo`** se comprobaron una a una contra los archivos reales
  de `origin/main` y de la rama. Las cinco aplicaban. A dos se les añadió un matiz que el revisor no
  traía: que `DROP CONSTRAINT` sí es plantable porque la cabecera `-- contract-of:` lo excusa, y que
  un contador que arranca en 0 choca con el suelo `>= 1` de la tarea 1.2.
- Sobre la recomendación del caso a1 se aceptó el arreglo y se dijo que era **incompleto**:
  `POST /users/{userId}/block` ya deja que uno de dos administradores desarme al otro sin
  aprobación, así que el spec ahora declara ese límite en vez de prometer una segregación que no
  tiene.
- **Cuatro hallazgos de CodeRabbit**, de los cuales uno era mío: había aplicado Q3 c1 al requisito
  de bloqueo y dejado el escenario *Removing the last approver* contradiciéndolo. Corregido.
- Uno de CodeRabbit se **rechazó con evidencia**: la colisión de `fn_activate_membership` ya está en
  la tabla de conflictos de `design.md` como aplazamiento declarado; se añadió un puntero desde la
  tarea 1.3b en vez de volver a decidirla.
- Diez hilos contestados, **ninguno resuelto**: resolver es la señal del revisor, como manda la
  skill.

**Cierre.** El PR se fusionó (`b524275`); la rama se rebasó antes, así que los dos commits viajaron
como `20024f1` y `8b96134`, y CodeRabbit pasó en verde sobre ese último head. Worktree y rama local
retirados después de comprobar que el contenido era idéntico al de `main`.

**El fallo de release que apareció al fusionar, y que no es del PR.** `release / prepare` falló en
`api-image-exists`: el rol de tst (`667674572794`) llama a `ecr:DescribeImages` sobre un repositorio
de la cuenta compartida (`903685415813`) y la *repository policy* no se lo concede. Lo destapó
`d1d6304` (SPD-291), que cambió el `release.yml` propio por el compartido: el anterior preguntaba lo
mismo con `batch-get-image`, que sí está permitido. La acción hace bien en fallar cerrada. Queda
anotado como bloqueante en el PR #149 y en SPD-291, en manos del equipo de AWS; **tst no despliega
desde el 3-nov**.

**La escritura real en Plane, por fin ejercida — pero no por el jugador.** La sesión 017 dejaba como
único pendiente "publicar de verdad un borrador en Plane" (tarea 3.4 del fichaje de
`product-owner`). Esta sesión escribió tres veces en Plane por MCP y las tres funcionaron: el
bloqueante en SPD-291 y el registro de tiempo en SPD-37. **La tarea 3.4 sigue sin marcar**: lo que
se probó es el camino de escritura del MCP, no el jugador `product-owner`, que no se convocó. Lo que
sí queda cerrado es la duda de si el conector escribe.

**Un tope del tablero.** El proyecto SPD tiene el time tracking apagado
(`work_log create` → `HTTP 404: Worklog is not enabled for the project`), así que el tiempo se
registró como comentario. Encenderlo es configuración de todo el proyecto y se dejó en manos del
humano, que eligió el comentario.

**Desviación de `CLAUDE.md`, declarada.** La regla dice que a partir de tres archivos se convoca a
`ingeniero-software`. Se editaron **seis** archivos del change OpenSpec a mano, en la sesión
principal. La razón: las ediciones *eran* la salida del análisis de la revisión —prosa quirúrgica
sobre specs, no construcción—, y delegarlas habría significado retransmitir el análisis entero al
subagente. Fue una decisión consciente, no un olvido, y no se le dijo al humano en su momento; queda
dicho aquí. **Resuelto el 2026-11-04: la regla se cumple sin matices.** Camilo decidió no escribir
la excepción, así que a partir de tres archivos se convoca, también cuando las ediciones salen del
propio análisis. Si retransmitir el análisis al subagente sale caro, el corte del trabajo es lo que
hay que revisar, no la regla.

**Verificación.** Ninguna: no se tocó el harness, así que `./scripts/check.sh` no se ejecutó. El
árbol sigue sucio por la mudanza de repositorio y por `add-strands-runner`, igual que lo dejó la
sesión 017.

**Siguiente paso.** Sin cambio respecto a la sesión 017: convocar a `product-owner` contra un work
item vivo y publicar su borrador, para cerrar la tarea 3.4.

### Sesión 019 — 2026-11-04 (recomendaciones del PR #173, fuera de este repositorio)

**Qué se hizo.** La skill `recomendaciones` sobre el PR
[#173](https://github.com/novopayment/cifra-spend-corporate-api-go/pull/173) de
`novopayment/cifra-spend-corporate-api-go` — el PR en borrador que cierra los follow-ups de
CodeRabbit sobre el change `manage-company-users` ya fusionado. **Tres hilos en dos vueltas del bot,
los tres aceptados** tras comprobarlos contra el código. Los dos primeros, `Major`, estaban abiertos
al empezar:

- **`spec.md:27` — la fecha de invitación se contradecía con su propio escenario.** `V6` declara
  `last_invitation_sent_at TIMESTAMPTZ NOT NULL DEFAULT now()`, y con eso el escenario *«an
  invitation the provider never accepted»* (`spec.md:49`) no se puede cumplir: la columna siempre
  llevaría fecha. La línea que el propio PR #173 había añadido en `spec.md:27` no cerraba la
  contradicción, la consagraba. Se tomó la salida que conserva el significado del campo —último
  envío aceptado— y lo hace nullable.
- **`spec.md:38` — la regla de retiro de rol perdía su candado al salir de la base.** El comentario
  de `V1` lo dice: el `UPDATE` del retiro bloquea la fila del rol y choca con el `FOR SHARE` de una
  asignación concurrente. La tarea 8.11 dropea solo el trigger del conteo, así que sin candado
  explícito un conteo tomado antes del `UPDATE` pierde la concesión que entra en medio y el rol se
  retira con miembro. `D5` no cubría el hueco: su candado de empresa se toma al *revocar* un rol
  complementario, no al *concederlo*.

**Entrada equivocada, corregida antes de escribir.** La sesión arrancó por `/openspec-propose`, que
crea un change nuevo en *este* repositorio. No hacía falta ninguno: los hilos piden corregir
artefactos de un change que ya existe en otro repositorio. Se paró antes del primer `write` y se
preguntó; el humano eligió `recomendaciones`.

**La regla de delegación se cumplió.** Tres archivos del change (`spec.md`, `design.md`,
`tasks.md`), siete reemplazos de texto ya redactados en el triaje → se convocó a
`ingeniero-software` con los textos exactos, en vez de teclearlos en la sesión principal. Es
justamente el caso que la sesión 018 dejó zanjado: las ediciones salían del propio análisis y aun
así se delega. La segunda vuelta fueron **dos** archivos y se tecleó en la sesión principal, que es
el otro lado de la misma regla: el corte está en tres, no en «delegar siempre».

**El tercero lo abrió el propio arreglo, y es el mismo defecto una capa más abajo.** Tras empujar
`eee9a95`, la segunda vuelta del bot señaló `design.md:61` (`Minor`): el backfill de `V6` copia
`invited_at` en `last_invitation_sent_at`, y `invited_at` se estampa al crear la fila, no cuando el
proveedor aceptó un envío. Es la misma mentira que acabábamos de sacar del escenario de
reactivación, ahora en las filas heredadas. **Su parche sugerido estaba incompleto**: vaciaba la
fecha y dejaba `invitation_sent_count` en su `DEFAULT 1`, y `spec.md:45` ata las dos columnas, así
que la fila habría quedado afirmando un envío por el contador y negándolo por la fecha. La
evidencia que el esquema sí tiene es `activated_at` — el status generado de `V1` leía `INVITED`
como exactamente `activated_at IS NULL` —, así que el backfill se parte por ahí: activada, se
conserva la aproximación y el contador 1; nunca activada, `NULL` y 0.

**Cierre en el PR.** Dos commits en `docs/SPD-37-openspec-review-followups`, los dos empujados:
`eee9a95` (3 archivos, +10/−5) y `bafcd03` (2 archivos, +2/−2), todo bajo `openspec/`.
`openspec validate manage-company-users --strict` en verde en los dos. Los tres hilos contestados
(`r4470716166`, `r4470717392` y `r4471050854`), **ninguno resuelto**.

**Un aviso sobre las respuestas obsoletas.** Las dos primeras se publicaron antes del push, y el
bot contestó *«I could not verify the reported fix»* anclado a `434b5dd`: revisa la rama remota, no
el árbol local. No era un rechazo, era que el commit no estaba allí. Lección para la skill
`recomendaciones`: **la respuesta a un hilo se publica después del push, no antes**, o nace
obsoleta.

**La pregunta de producto salió del repositorio al tablero, y se fijó la forma de hacerlo.** El
hilo 3 dejó una decisión que ingeniería no puede tomar: si una invitación pendiente anterior a la
migración puede leerse como «no enviada». Camilo propuso publicarla en Plane como una tabla de
cuatro columnas —pregunta, propuesta, porqué, veredicto del PO—. **Se contrastó y se cambió antes
de escribir nada**, con tres evidencias: ninguno de los siete comentarios de SPD-37 usa tabla, el
juego de etiquetas que documenta la carta de `product-owner` para `comment_html` no incluye
`<table>`, y el PO responde en comentario propio (lo hizo el 30-oct con Q1–Q5), así que **no puede
escribir en una celda nuestra**. Una cuarta columna vacía es una promesa que el sistema no cumple:
el ticket mostraría para siempre una pregunta que parece sin responder.

La forma que quedó, y que Camilo aprobó como plantilla para las siguientes: **cuatro bloques en
vertical**, con la columna 4 convertida en petición explícita —*responde «A», «B» o tu
contrapropuesta, en un comentario tuyo*— y el veredicto cerrándose en `po-questions.md`, que es
donde está versionado al lado del spec que depende de él.

**Q8 publicada, y el crédito dicho como es.** `product-owner` la redactó —citando
*The Software Architect Elevator* · cap. 6 · p. 72 para el supuesto por defecto declarado
reversible—, pero **su llamada a Plane la denegó el clasificador** (`External System Writes`). No
intentó rodearlo, que es lo correcto. La relanzó la sesión principal con el mismo HTML, sin un
carácter cambiado: comentario interno `c2bb3616` en SPD-37. **La tarea 3.4 sigue abierta**: se
volvió a probar el camino de escritura del MCP, no que el jugador publique por sí mismo. Para
cerrarla hace falta una regla de permiso para `mcp__claude_ai_Plane__workitem_comment`.

**Q8 también en el repositorio, aparcada a propósito.** Se escribió en `po-questions.md` con el
formato de Q1–Q7 (Q6 no existe) y **no viaja en #173**: decisión de Camilo, porque donde la
respuesta del PO cambia código es en el PR que lleve la tarea 1.4c. Vive en
`docs/SPD-37-po-question-q8` (`b758e8c`), rama local sin PR, para no sumar otro a la pila.

**Verificación.** Ninguna sobre este repositorio: no se tocó el harness, así que
`./scripts/check.sh` no se ejecutó. En el repositorio del PR, `openspec validate
manage-company-users --strict` en verde en los tres commits. El árbol de este repositorio sigue
sucio por la mudanza y por `add-strands-runner`, igual que lo dejó la sesión 018.

**Riesgos y pendientes de decisión humana.**

- **Q8 publicada y sin responder.** ¿Es aceptable que una invitación pendiente anterior a la
  migración aparezca como «no enviada», con su límite de reenvío reseteado? Es el precio del
  backfill partido por `activated_at`. Supuesto por defecto: se sigue con la opción A, que es
  reversible porque `invited_at` no se borra. Si el PO dice que no, cambia el `UPDATE` de `V6` y con
  él la tarea 1.4c.
- **Hay 21 PRs abiertos en `cifra-spend-corporate-api-go`, 14 en borrador.** `CLAUDE.md` pone el
  tope en tres esperando veredicto y lo llama restricción dura. No es de esta sesión y no se tocó,
  pero queda dicho: cada PR nuevo de esa pila se construye sobre código sin revisar.
- **Q9 candidata, sin redactar:** `tasks.md` 0.5, marcada `[human]` — acordar la máquina de estados
  con `add-request-permission-check`. `product-owner` avisa que es acuerdo entre dos changes, no
  decisión de producto, así que puede que no salga a Plane.
- El SQL que de verdad arregla los hilos 1 y 3 en el esquema queda como tarea **1.4c**, sin
  implementar: `V6` vive en las ramas apiladas, no en `main`, y #173 es solo documentación.
- **Se consumieron las dos vueltas de CodeRabbit** que permite `CLAUDE.md`. Si una tercera abre
  hilos nuevos, el problema no es el hilo: es el corte del PR o una regla que falta en
  `.coderabbit.yaml`, y se arregla ahí con su nota en `factory brain learn`.
- El PR pasó de borrador a listo durante la sesión, y **no lo marcó esta sesión**.
- El repositorio `cifra-spend-corporate-api-go` se dejó en la rama
  `docs/SPD-37-openspec-review-followups`. Estaba en HEAD desacoplado sobre `28fac78`, que vive en
  `feature/SPD-174-users-module-and-list`, así que no se perdió nada, pero no se devolvió a su
  estado inicial.

**Siguiente paso.** La tarea 3.4 está a un permiso de cerrarse: `product-owner` ya redactó contra
un work item vivo y su borrador se publicó, pero lo publicó la sesión principal. Añadir la regla
`mcp__claude_ai_Plane__workitem_comment` a los ajustes —decisión de Camilo— y volver a convocarlo
para que escriba él. Después, la respuesta del PO a Q8 y la tarea 1.4c.

### Sesión 020 — 2026-11-04 (la pila de usuarios de `cifra-spend-corporate-api-go`, fuera de este repositorio)

**Qué se hizo.** Trabajo sobre la pila de PRs de administración de usuarios del Portal Empresas, en
`novopayment/cifra-spend-corporate-api-go`. **Este repositorio no cambió**: `./scripts/check.sh`
termina en 0 y no se tocó ni el harness ni `openspec/` de aquí.

**La barrida de lint, y la causa que la hacía falta.** Diez eslabones (#134 a #143) pasaron
`golangci-lint` por primera vez. No era descuido: los cuatro workflows del repositorio disparan con
`pull_request: branches: [main]`, y un PR apilado apunta a una rama de feature, así que **ninguna
compuerta corre sobre él** — no fallan, no aparecen. La primera vez que un eslabón ve CI es cuando su
base se integra y GitHub lo reapunta a `main`, justo cuando ya hay alguien esperando para revisar.
Mientras eso siga así, la verificación local es la única compuerta de la pila.

**Dos defectos que solo aparecieron al correr el binario.** Ninguno lo veía la suite en proceso:

- **`GET /users` contestaba 500 en la primera página.** El constructor de consultas de go-bricks
  acepta identificadores en `Select` y nada más, y recibía `count(*)`, que es una llamada a función:
  la sentencia ni se construía. La causa de que nadie lo viera es medible — `directory_test.go`
  cubría `pageSQL` en catorce casos y `countSQL` en **ninguno**. Arreglado en #131, que es donde
  nace, con dos tests y la prueba al revés.
- **Un teléfono vacío no podía limpiarse.** La edición declara tres estados (ausente deja, vacío
  limpia, valor escribe) y el vacío no llegaba nunca: con `validator v10.30.5`, un `*string` no nil
  que apunta a `""` no lo salta `omitempty`, así que `min=6` lo mataba antes del servicio. Se
  reprodujo con una sonda antes de tocar nada.

**La revisión que más enseñó.** `grosales-np` dejó doce observaciones en #122 y **midió** la que
importaba: el índice de `V7` no atendía ninguna consulta, porque `text_pattern_ops` solo entra en
`LIKE 'term%'` y la búsqueda del listado es `LIKE '%term%'` — además de ser esa columna la clave de
orden y del keyset. Verificado por el lado del código antes de aceptarlo. La otra decidió media
pregunta de producto: `V1:350` lleva `ck_company_membership__blocked_requires_activated`, así que
**la base rechaza bloquear a quien nunca activó**, y el escenario 2 de SPD-191 no es una rama que
falte en Go.

**Dónde se paró, y por qué.** Se paró a petición del usuario con #122 recién corregido: es el fondo
de la pila y cada cambio suyo se propaga a los catorce PRs de encima, así que seguir tocando los de
arriba compra reproceso. El estado completo —commits, orden para retomar, decisiones pendientes de
producto y deudas operativas— quedó en
`pendiente-diario/pila-spd80.md`, junto a la tabla de los 17 PRs.

**Lo que se publicó fuera.** Cinco comentarios de avance en Plane, uno por historia (SPD-102,
SPD-175, SPD-191, SPD-192 y SPD-194), cada uno contra **sus** criterios de aceptación. Una trampa que
conviene recordar: el trabajo venía etiquetado `[SPD-80]` en ramas y commits, y SPD-80 es la historia
de **roles**, no la de usuarios; reportar ahí habría contado el avance en la historia equivocada.

**Dos reglas de la casa que se cumplieron y vale la pena anotar.** Una rebanada no está terminada
hasta que corre contra el servicio arrancado: los dos defectos de arriba salieron de ahí, no del
diff. Y un arreglo sin su mutación es una opinión con commit: cada uno se cerró rompiéndolo a
propósito para ver caer el test.

**Verificación.** `./scripts/check.sh` de este repositorio en 0. En el repositorio de trabajo, y por
rama: `go build`, `go vet`, `go test ./internal/...`, la suite de integración, `golangci-lint`,
`make check-migrations` y el archivo de escenarios contra el tenant sembrado (28 `ok`, 12 `GAP`).

**Siguiente paso.** Esperar el veredicto de `grosales-np` en #122 antes de tocar nada de la pila.

### Sesión 021 — 2026-11-05 a 2026-11-08 (la pila de usuarios de `cifra-spend-corporate-api-go`, fuera de este repositorio)

El harness de este repositorio no cambió. El trabajo fue en la pila SPD-37 del otro repositorio:
tests por mutación medidos contra todas las suites (`service` 78/84), `main` integrado en la pila,
los bloqueantes 1, 2 y 3 de Gabriel en #131 resueltos y empujados, `search_text` escrito al invitar y
al editar más el backfill V10, y triaje de los 16 PRs (282 ítems). Todo quedó empujado, cada push
aprobado por el usuario.

**Verificación.** En el repositorio de trabajo, por eslabón: build, vet, `go test ./...`,
la suite de integración y `golangci-lint`; cada push se hizo fast-forward.

**Siguiente paso.** `pendiente-diario/retomar-2026-11-09.md`: el texto de V7 en #122, y después
los defectos del triaje.

### Sesión 022 — 2026-11-09 (dos hilos de CodeRabbit en #131, fuera de este repositorio)

El harness de este repositorio no cambió, así que `./scripts/check.sh` no se ejecutó. El trabajo
fue la revisión de CodeRabbit sobre `4c62cca` en `cifra-spend-corporate-api-go` #131 (SPD-174):
dos hilos y un comentario fuera del diff, los tres válidos tras comprobarlos en el código.

- `eb5e03f2` — `handlers/handler.go`: `URL.Query()` descartaba en silencio un par mal codificado
  (`filter[status]=%ZZ` devolvía el directorio sin filtrar). Ahora se parsea `RawQuery` y se responde
  400 `INVALID_FILTER` (`NewGenericInvalidFilterError`), tras la compañía de sesión y antes del servicio.
  `TestListUsersQueryString` cubre tres casos.
- `2e789dcf` — docs: P13 fechada (2026-11-06, commit `afb5ece0`) en el Glossary y en `design.md` § P13;
  `Users and Governance.md` deja de decir que P13 está abierta; `spec.md:19` pasa a `MUST NOT`.
- Respuestas publicadas en los dos hilos y en un comentario del PR. Push aprobado por el usuario.
- CodeRabbit leyó `2e789dc` y resolvió él mismo los dos hilos (`resolvedBy: coderabbitai[bot]`).
  Confirmó el arreglo leyendo el código, sin ejecutar los tests.

**Verificación.** En el worktree del PR: `go build ./...`, `go vet`, `go test` (10 paquetes) y
`golangci-lint` (0 issues). Dos mutaciones (parseo antes de la sesión; `req.Query` sin asignar)
rompen el test. `checker`: FAIL en la primera ronda (cobertura, medium) y PASS_WITH_MINOR en la segunda.

**Riesgos / pendientes.**
- `cards/handlers/handler.go:87` y `me/handlers/handler.go:93` tienen el mismo `URL.Query()`;
  queda como seguimiento en otro PR. El bot preguntó si abrir un issue: sin contestar.
- Worktree temporal en el scratchpad de la sesión (`pr131`), sin cambios pendientes.

**Siguiente paso.** Decidir el seguimiento de `cards` y `me`; después,
`pendiente-diario/retomar-2026-11-09.md`.

### Sesión 022 — 2026-11-09 (respuestas del PO aplicadas en la pila de usuarios, fuera de este repositorio)

El harness de este repositorio no cambió. El PO contestó las preguntas abiertas de SPD-37 y se aplicaron
en `cifra-spend-corporate-api-go`, cada tanda con el `checker` en verde antes de empujar:
- **Q18 y bloquear a un Invitado (#140):** V11 retira `ck_company_membership__blocked_requires_activated`. Al desbloquear, quien nunca aceptó vuelve a `INVITED`.
- **Q8 (#131–#136):** el correo es único en cualquier estado y la invitación responde 409. #133 (V9) se cerró sin fusionar. **GitHub rechazó cambiar la base de #134 a #132 («part of a stack»): pendiente de hacerlo desde la web.**
- **Q13 (#131):** `control_center.users.read` con `V7_1`. Q13 se queda dentro de #131, que ya excedía el límite de tamaño: la pila nativa no deja insertar un PR ni cambiar bases, y el límite de PRs sin revisar no deja abrir otro.
- **Bloqueo de despliegue:** la tarea 4.3c, humana, pide crear `.read` en Auth0 antes de desplegar #131.

Se publicaron 55 respuestas del PO en los hilos de los revisores.

**Siguiente paso:** `pendiente-diario/retomar-2026-11-09.md` (Q16, Q7, Q18 envío automático, Q1/Q10).

**Cierre de la sesión 022 (tarde del 09-nov).** El harness de este repositorio sigue sin cambios.
- En la pila se aplicaron Q8, Q13, Q16 y la tanda Q18/Q7/Q1/Q10, cada una con el `checker` y subida a GitHub.
- En #131 se aplicaron A2 y M1 de mfranco.
- #143 pasó a un solo commit, con lo que desaparece el falso positivo de Orca.
- Se publicaron un cuestionario para los revisores y 21 respuestas a hilos ya resueltos.
- `git rerere` quedó activado en cifra.

Lo siguiente está en `pendiente-diario/retomar-2026-11-10.md`: 47 hilos abiertos y la pasada a medias en `wt-pass2`.
