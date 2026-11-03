# Tasks

> No se tocan `scripts/check.sh` ni la configuración de ruff o pytest. El panel sigue sin escribir archivos.

## 1. Recolección (`panel-pulls`)

- [x] 1.1 `src/factory/panel/pulls.py`: `collect(root, runner, now)` con las tres consultas de `gh pr list` (autor abiertos, revisión pedida, fusionados recientes), dedupe por número y `runner` inyectable.
- [x] 1.2 Clasificación de estado y tiempos: horas abierto, sin actividad, hasta la primera revisión y de ciclo.
- [x] 1.3 Alertas: checks fallando, cambios pedidos, conflictos, sin revisor, sin `@coderabbitai review`, sin equipo `cifra`, parado y pasado de tamaño.
- [x] 1.4 Degradación: sin `gh`, sin sesión o con error, la sección queda vacía con el motivo en `error`, sin excepción.

## 2. Panel

- [x] 2.1 `snapshot.py`: sección `pulls` en `SECTIONS` y en `build`.
- [x] 2.2 `server.py`: hilo sondeador cada 60 s, resultado en memoria y `broadcast(["pulls"])` solo cuando cambia.
- [x] 2.3 `cli.py`: `factory panel --no-pulls` y una consulta única para `--json`.
- [x] 2.4 `static/index.html`: pestaña «Pull requests», KPI de PR con alerta y tabla con tiempos.

## 3. Tests y documentación

- [x] 3.1 `tests/test_panel_pulls.py`: consultas, dedupe, roles, estados, tiempos, cada alerta y los modos degradados.
- [x] 3.2 `tests/test_panel_server.py`: la instantánea trae `pulls` y el panel no sale a la red si no se le pide.
- [x] 3.3 `docs/harness/panel.md` y `README.md`: qué muestra la pestaña, qué necesita (`gh auth login`) y cómo apagarla.
- [x] 3.4 `openspec validate add-panel-pulls --strict` y `./scripts/check.sh` en 0.
