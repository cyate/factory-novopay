# Tasks

> No se tocan `scripts/check.sh` ni la configuración de ruff o pytest. El comando es de solo lectura: no escribe en GitHub ni en el repositorio.

## 1. Lectura de las recomendaciones (`pr-feedback`)

- [x] 1.1 `src/factory/feedback.py`: `recoger(pr, root, repo, revisores, resueltos, runner)` con una consulta `gh api graphql` (hilos y revisiones), `runner` inyectable y referencia por número o URL.
- [x] 1.2 Filtro por revisor sobre cualquier participante del hilo, por subcadena del login.
- [x] 1.3 Hilos resueltos ocultos por defecto y contados en `ocultos`; `--resueltos` los incluye.
- [x] 1.4 Recortes: 4.000 caracteres por hilo y 1.500 por cuerpo de revisión, con la URL siempre presente.
- [x] 1.5 Degradación: sin `gh`, sin sesión, sin red, con un directorio inexistente o con un PR que no existe, termina en 2 con el motivo en `stderr`.

## 2. CLI y presentación

- [x] 2.1 `factory feedback <pr> [--repo] [--revisor] [--resueltos] [--json]` en `src/factory/cli.py`.
- [x] 2.2 `render`: Markdown agrupado por revisor, con `archivo:línea`, estado del hilo y el comando `gh … /replies` de cada uno.

## 3. Ciclo completo

- [x] 3.1 Skill `.claude/skills/recomendaciones/`: leer, comprobar, triaje aprobado por el humano, arreglar y responder, sin push ni resolver hilos.

## 4. Verificación y documentación

- [x] 4.1 `tests/test_feedback.py` y la entrada en `tests/test_cli_help.py`.
- [x] 4.2 `docs/harness/recomendaciones.md`, y las filas de `README.md` y `AGENTS.md`.
- [x] 4.3 Prueba en vivo contra `novopayment/cifra-spend-corporate-api-go#120`.
