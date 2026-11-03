## Why

El panel ya cuenta lo que pasa **dentro** de la fábrica: tokens, revisiones de subagentes y estado de implementación. Pero el trabajo no termina cuando el checker da `pass`: termina cuando el pull request se integra, y esa parte hoy no se ve en ningún sitio. Para saber si un PR está parado, si los checks fallan, si alguien ya lo revisó o si CodeRabbit nunca llegó a mirarlo, hay que ir a GitHub y abrirlos uno a uno.

Esa es justo la zona donde se pierde la trazabilidad: un PR abierto hace tres días sin revisor asignado no avisa a nadie, y los tiempos de revisión —cuánto tarda la primera respuesta, cuánto vive un PR abierto— no se miden, así que no se pueden mejorar.

Las reglas de oficio de `CLAUDE.md` (10 archivos y 600 líneas, comentario `@coderabbitai review`, revisión del equipo `cifra`) tampoco tienen hoy ninguna comprobación: se cumplen de memoria.

## What Changes

- **Sección `pulls` nueva en la instantánea**, con los pull requests abiertos que el usuario creó (`--author @me`) y aquellos en los que se le pidió revisión (`review-requested:@me`), más sus últimos PR fusionados para medir el ciclo completo.
- **Tiempos de revisión por PR**: horas abierto, horas sin actividad, horas hasta la primera revisión y horas de ciclo (creación → fusión).
- **Alertas accionables** por PR: checks en rojo, cambios pedidos, conflictos, sin revisor, sin `@coderabbitai review`, sin el equipo `cifra`, parado más de 24 h y pasado de tamaño (10 archivos o 600 líneas).
- **Pestaña «Pull requests» en la página**, con KPI de PR con alerta y actualización en vivo por el mismo canal SSE que el resto.
- **Los datos se leen con `gh`**, el CLI que ya usa el flujo del repositorio, y **viven solo en memoria**: el sondeador no escribe ningún archivo, así el panel sigue siendo de solo lectura.

Sin `gh`, sin sesión iniciada o sin red, la sección queda vacía con el motivo en `pulls.error`, que la pestaña pinta como subtítulo; `warnings` no se toca y el resto del panel no se entera. `factory panel --no-pulls` apaga por completo las llamadas de red.

## Impact

- Specs: `observability-panel` (tres requisitos modificados, dos añadidos).
- Código: `src/factory/panel/pulls.py` (nuevo), `snapshot.py`, `server.py`, `cli.py` y `static/index.html`.
- Tests: `tests/test_panel_pulls.py` (nuevo) y `tests/test_panel_server.py`.
- Red: el panel pasa a hacer llamadas salientes a GitHub mediante `gh`, cada 60 s mientras el servidor corre. Es la primera vez que el panel sale a la red, por eso lleva interruptor explícito.
