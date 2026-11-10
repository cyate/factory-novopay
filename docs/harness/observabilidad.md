# Observabilidad de los loops

Cuanto más rápido corre un loop, más necesitas ver qué pasa dentro (L11). Con estos archivos, un humano audita una ejecución sin leer transcripciones.

## Estado externo

Cada ejecución deja su memoria en `.factory/` del repo principal. Está fuera de los worktrees e ignorada por git, así que sobrevive cuando se borra el worktree:

| Archivo | Contenido |
|---|---|
| `.factory/runs/<run-id>/loop-state.md` | estado legible: rondas, verificación, hallazgos, decisión, estadísticas, resultado final |
| `.factory/runs/<run-id>/state.json` | lo mismo, legible por máquina (fuente de verdad, escritura atómica) |
| `.factory/runs/<run-id>/events.jsonl` | una línea por invocación de agente (rol, modelo, coste, tokens, denegaciones) o comando (código, salida truncada) |
| `.factory/runs/<run-id>/goal.md` | copia del objetivo usado |
| `.factory/runs/<run-id>/rounds/<n>/` y `decision.md` | artefactos legibles por ronda (abajo) |
| `.factory/results.tsv` | una fila por ronda de todas las ejecuciones (solo-añadir) |
| `.factory/inbox/<run-id>.md` | resumen de la ejecución para revisarla (lo escribe el motor; ningún comando lo lee) |

### Artefactos legibles por ronda

Además de `events.jsonl`, el orquestador escribe archivos pensados para leerse. Empiezan con cabeceras `CLAVE: valor` hasta la primera línea en blanco, y `factory.artifacts.read_header` las lee. Las claves entre corchetes son opcionales.

<!-- tabla-artefactos: se valida en tests/test_artifacts.py -->
| Archivo | Cabeceras | Contenido |
|---|---|---|
| `rounds/<n>/maker.md` | STATUS, MODEL, COST_USD | resumen del maker, archivos cambiados, notas del orquestador |
| `rounds/<n>/checks.md` | GATE, [COMMIT], [SCORE], [REVERTED_TO], DECISION | rutas protegidas tocadas y cada criterio con el final de su salida si falló |
| `rounds/<n>/review.md` | VERDICT, [MODEL] | hallazgos del checker, o el motivo si no hubo veredicto |
| `decision.md` | RESULT, REASON, BRANCH, BEST_ROUND, [BASE], [PARENT], [LANDED] | resumen final, pregunta para el humano y bloqueos |

- `GATE` vale `PASS`, `FAIL` (también en reversiones por alcance o por rutas protegidas) o `NOT_RUN` (error del agente o ronda bloqueada).
- `VERDICT` vale `pass`, `fail`, `pass_with_minor`, `inválido`, `omitido` (sin presupuesto) o `no_invocado`.
- `COMMIT` es el commit verificado. Si el ratchet revirtió la ronda, `REVERTED_TO` indica la mejor ronda a la que volvió la rama.

Cada ronda recibe un **resumen acotado** (`summary_max_chars`), no la transcripción anterior. El resumen prioriza los bloqueos, la mejor ronda y la más reciente.

---
Adaptado de walkinglabs/learn-harness-engineering (MIT), lecciones 11 y 13.
