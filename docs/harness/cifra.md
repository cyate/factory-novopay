# Servicios Go de cifra

Reglas de los repositorios Go de `cifra`. Las de feature-flag y servicio arrancado son de Go; las de PR (apertura, borrador, límite) rigen en todo PR de un repo cifra. Se leen antes del primer `Edit` o del primer PR en un repo cifra.

## Toda ruta nueva nace detrás de un feature-flag

Una clave `custom.<módulo>.enabled` inyectada con `config:"..."`, que decide si la ruta se registra, para poder apagarla sin desplegar si algo sale mal.

- **Una bandera no es una puerta.** El flag decide si la ruta **existe**; el permiso decide **quién pasa**. Van los dos, nunca uno en lugar del otro.
- Toda clave nueva lleva su entrada en `.env.example`, su fila en la tabla del README y su valor por defecto en `config.yml`.

## Al abrir un pull request

Siempre, incluido un PR en borrador o apilado sobre otro que aún no se ha integrado:

1. deja un comentario cuyo cuerpo sea exactamente `@coderabbitai review`, para que el bot lo tome; un PR en borrador no lo dispara solo, salvo en los repositorios donde `.coderabbit.yaml` ya lleva `auto_review.drafts: true` en su rama por defecto;
2. pide revisión al equipo `cifra` (`gh pr edit <n> --add-reviewer novopayment/cifra`), que es el grupo a cargo de las revisiones.

## Una rebanada no está terminada hasta que corre contra el servicio arrancado

Un test que ejerce el router en proceso prueba el enrutado y la forma de la respuesta; no prueba que el binario arranque, lea su configuración y conteste. Ese recorrido va **en la misma rebanada**, no en una tarea final de certificación: al final ya no evita nada, solo lo constata.

- El agente global `entrega-qa` (`~/.claude/agents/`) escribe esos escenarios en `entregas/<TICKET>/`. Si ese directorio está vacío mientras hay rutas construidas, el recorrido no se ha hecho, da igual lo verde que esté la compuerta.
- **Decisión del usuario:** el paquete `entregas/<TICKET>/` se entrega **directo a QA** y **no va en un pull request**; no es un bloqueo de aprobación.

## Un PR nace en borrador

Borrador no significa a medias: significa que el bot ya puede revisarlo y que todavía no reclama tiempo de una persona. Se marca listo (`gh pr ready <n>`) cuando modelo, ruta y su recorrido contra el servicio pasan, y nunca con el último commit sin revisar por el bot, porque pedir revisión humana sobre código que nadie ha mirado es justo el ruido que hace que no revisen ninguno.

## Límite de PRs abiertos sin revisar

Es una restricción dura, como el WIP=1. Con **tres o más** esperando veredicto, no se abre otro: se empuja la revisión de los que hay. Una pila apilada crece peor que lineal: cada PR nuevo se construye sobre código sin revisar, así que un cambio pedido abajo se propaga por todos los de arriba.

- Empujar la revisión es trabajo concreto, no insistir: cerrar los hilos del bot, dejar sin ruido los de más abajo, y decir por cuál empezar. Una lista de nueve iguales no se empieza.
