# Registro de progreso

## Estado verificado actual

- Raíz del repositorio: `factory-yate/`, la que contiene `AGENTS.md`.
- Arranque estándar: `./init.sh`.
- Verificación estándar: `./scripts/check.sh`.
- OpenSpec: specs principales en `openspec/specs/` (18 capacidades; `add-reglas-de-oficio` no añade ninguna, solo requisitos). Cambios archivados: `2026-10-27-add-harness-loop-engine`, `2026-10-28-extend-factory-pipeline`, `2026-10-28-add-knowledge-brains`, `2026-10-29-add-library-map`, `2026-10-30-add-equipo-ideal` (sesión 007) `2026-10-30-add-panel` (sesiones 008 y 009) `2026-10-30-add-reglas-de-oficio` (sesión 010) y `2026-10-30-fichar-arquitecto-api` (sesión 011). No hay ningún cambio activo.
- Feature activa / siguiente: ver `.venv/bin/factory features list`.
- Commits: ver `git log`. HEAD de la última sesión verificada: `b70d745`.
- Bloqueos actuales: el push de `main` es una decisión humana pendiente. La prueba live (9.2) nunca se aprobó y quedó superada por el dogfooding de la sesión 003 (9.3), que confirmó el contrato de `--json-schema`.

## Registro de sesiones

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
