@AGENTS.md

## Notas para Claude Code

- **Revisión independiente.** Antes de declarar terminada una feature, invoca el subagente `checker` (definido en `.claude/agents/checker.md`).
  - Pásale solo el diff (`git diff`) y los criterios de la feature, no tu razonamiento.
  - Corrige los hallazgos `critical` y `medium` y vuelve a pedir revisión.
- **El `checker` es de solo lectura.** Si hace falta verificar, ejecuta tú `./scripts/check.sh` y pásale el resultado.
- **Trabajo largo o desatendido.** Usa el motor de loops de `factory` en lugar de encadenar prompts a mano (ver `docs/harness/loops.md`).
- **Equipo ideal.** En sesiones interactivas, para trabajo con varias facetas (seguridad, QA, documentación, producto, complejidad), usa `/equipo` (el técnico y los jugadores que convoque) o `claude --agent tecnico` (ver `docs/harness/equipo.md`).
  - El acta del equipo **no sustituye** al `checker`: sigue siendo el árbitro obligatorio antes de dar por terminada una feature.
- **Tamaño de un pull request.** Un PR se corta para que una persona pueda leerlo: **10 archivos y 600 líneas como máximo**, y el corte se decide **antes** de escribir, no cuando ya está escrito.
  - El límite cuenta **código y tests**. Los archivos estáticos —contrato OpenAPI, documentación, specs, datos de prueba— pueden pasarse, y conviene decir en el cuerpo del PR cuántas líneas son suyas.
  - Si la feature no cabe, se parte en PRs apilados, cada uno desplegable por sí solo. Un PR que se pasa sin haberlo intentado es un defecto de planificación, no un detalle.
- **Toda ruta nueva nace detrás de un feature-flag.** Una clave `custom.<módulo>.enabled` inyectada con `config:"..."`, que decide si la ruta se registra, para poder apagarla sin desplegar si algo sale mal.
  - **Una bandera no es una puerta.** El flag decide si la ruta **existe**; el permiso decide **quién pasa**. Van los dos, nunca uno en lugar del otro.
  - Toda clave nueva lleva su entrada en `.env.example`, su fila en la tabla del README y su valor por defecto en `config.yml`.
- **Antes de abrir un pull request.** `./scripts/pre-pr.sh [base]` tiene que terminar en 0. Comprueba primero que haya algo que medir (árbol limpio y commits sobre la base) y corre contra el diff lo mismo que correrá el revisor —verificación, tamaño, complejidad y la revisión de CodeRabbit en local—; lo que se arregla ahí no llega a ser un hilo que contestar. `PRE_PR_STRICT=1` exige además que el CLI de CodeRabbit esté instalado.
  - **Dos vueltas como máximo.** Si tras la segunda vuelta de CodeRabbit siguen abriéndose hilos, para: el problema es el corte del PR o una regla que falta en `.coderabbit.yaml`, no el hilo. Arréglalo ahí y deja la nota con `factory brain learn`.
  - Las reglas con las que el bot revisa este repositorio viven en `.coderabbit.yaml`: un hilo que repite algo que las reglas de la casa ya deciden es una instrucción que falta en ese archivo.
- **Al abrir un pull request.** Siempre, incluido un PR en borrador o apilado sobre otro que aún no se ha integrado:
  1. deja un comentario cuyo cuerpo sea exactamente `@coderabbitai review`, para que el bot lo tome; un PR en borrador no lo dispara solo, salvo en los repositorios donde `.coderabbit.yaml` ya lleva `auto_review.drafts: true` en su rama por defecto;
  2. pide revisión al equipo `cifra` (`gh pr edit <n> --add-reviewer novopayment/cifra`), que es el grupo a cargo de las revisiones.
- **Una rebanada no está terminada hasta que corre contra el servicio arrancado.** Un test que
  ejerce el router en proceso prueba el enrutado y la forma de la respuesta; no prueba que el
  binario arranque, lea su configuración y conteste. Ese recorrido va **en la misma rebanada**, no
  en una tarea final de certificación: al final ya no evita nada, solo lo constata.
  - El agente `entrega-qa` escribe esos escenarios en `entregas/<TICKET>/`. Si ese directorio está
    vacío mientras hay rutas construidas, el recorrido no se ha hecho — da igual lo verde que esté
    la compuerta.
- **Un PR nace en borrador y se marca listo cuando la rebanada vertical está verde.** Borrador no
  significa a medias: significa que el bot ya puede revisarlo y que todavía no reclama tiempo de una
  persona. Se marca listo (`gh pr ready <n>`) cuando modelo, ruta y su recorrido contra el servicio
  pasan — y nunca con el último commit sin revisar por el bot, porque pedir revisión humana sobre
  código que nadie ha mirado es justo el ruido que hace que no revisen ninguno.
- **Hay un límite de PRs abiertos sin revisar, y es una restricción dura como el WIP=1.** Con **tres
  o más** esperando veredicto, no se abre otro: se empuja la revisión de los que hay. Una pila
  apilada crece peor que lineal — cada PR nuevo se construye sobre código sin revisar, así que un
  cambio pedido abajo se propaga por todos los de arriba.
  - Empujar la revisión es trabajo concreto, no insistir: cerrar los hilos del bot, dejar sin ruido
    los de más abajo, y decir por cuál empezar. Una lista de nueve iguales no se empieza.
- **Cierre de sesión.** Sigue la lista de `AGENTS.md`. No termines con `./scripts/check.sh` en rojo sin documentarlo en `progress.md`.
- **OpenSpec.** Los comandos `/opsx:*` gestionan las specs y los cambios de `openspec/`.
