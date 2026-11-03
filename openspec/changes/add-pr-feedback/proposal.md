## Why

El panel ya avisa de que un pull request tiene revisiones; nadie dice **qué piden**. Un PR como [#120 de `cifra-spend-corporate-api-go`](https://github.com/novopayment/cifra-spend-corporate-api-go/pull/120) acumula 53 hilos en línea de cinco revisores —CodeRabbit, Orca, SonarQube, un revisor humano y el agente `sam-pc-novo`—, mezclados con los ya resueltos y con los resúmenes de cada revisión. Para atenderlos hay que abrir el PR en el navegador, distinguir a ojo lo vivo de lo cerrado y copiar a mano el identificador de cada comentario para poder responderlo.

Esa fricción se paga en recomendaciones sin contestar: siete de `sam-pc-novo` en ese PR, cada una con archivo y línea, sin respuesta. Una recomendación sin respuesta es trabajo abierto, aunque la respuesta sea rechazarla.

## What Changes

- **`factory feedback <pr>`**: lee los hilos en línea y los cuerpos de revisión de un pull request con `gh api graphql`, agrupados por revisor, con `archivo:línea`, el estado del hilo y el comando `gh` exacto para responderlo. Acepta número o URL, filtra por revisor con un trozo del login (`sam` → `sam-pc-novo`), oculta por defecto los hilos resueltos y tiene salida `--json`.
- **Solo lectura**: ninguna escritura en GitHub ni en el repositorio. Las respuestas las publica el humano, o un agente con su aprobación.
- **Skill `recomendaciones`**: dirige el ciclo entero —leer, comprobar cada recomendación contra el código, enseñar el triaje, arreglar lo aceptado y responder los hilos uno a uno con aprobación humana—, sin push, sin merge y sin resolver hilos.

## Impact

- Specs: `pr-feedback` (capacidad nueva).
- Código: `src/factory/feedback.py` (nuevo) y `src/factory/cli.py`.
- Tests: `tests/test_feedback.py` (nuevo) y `tests/test_cli_help.py`.
- Documentación: `docs/harness/recomendaciones.md` (nuevo), `README.md`, `AGENTS.md` y `.claude/skills/recomendaciones/SKILL.md` (nuevo).
- Red: una consulta `gh api graphql` por invocación, de solo lectura y con la sesión de `gh` del usuario. No hay sondeo ni proceso de fondo.
