---
name: recomendaciones
description: Atiende las recomendaciones de los revisores de un pull request (sam, CodeRabbit, Orca, humanos). Lee los hilos con `factory feedback`, comprueba cada uno contra el código, arregla los aceptados y responde el hilo. Úsala cuando el usuario diga "revisa las recomendaciones", "atiende lo que dejó sam", "contesta los hilos del PR" o dé la URL de un pull request con revisiones pendientes.
argument-hint: "<url-o-número-del-PR> [revisor]"
---

# Recomendaciones de los revisores

Un revisor deja una recomendación; alguien tiene que decidir si tiene razón. Esta skill hace
ese recorrido entero: leer, comprobar contra el código, arreglar lo aceptado y responder el
hilo. Una recomendación sin respuesta es trabajo abierto, aunque sea para rechazarla.

## Antes de empezar

1. **Estás en el repositorio del PR**, en su rama. `gh pr status` o `git branch --show-current`
   lo confirma. Si no, **para**: no se arregla un PR desde otro repositorio.
2. El árbol está limpio (`git status --porcelain`). Si no, pregunta antes de tocar nada.

## 1. Leer

```bash
factory feedback <pr> --revisor <login>     # el PR acepta número o URL; el revisor, un trozo del login (sam)
factory feedback <pr>                       # todos los revisores
factory feedback <pr> --resueltos --json    # también los hilos ya cerrados, para máquina
```

Salen los hilos en línea sin resolver, agrupados por revisor, con `archivo:línea`, el cuerpo
entero, quién ya respondió y el comando exacto para contestar. Las **revisiones generales**
(el resumen de un revisor) van al final: son contexto, no tienen hilo al que responder.

Si un hilo ya tiene respuesta tuya, no lo repitas: léelo y sigue.

## 2. Comprobar, uno a uno

Para cada recomendación, **abre el archivo citado** y compruébala contra el código de verdad.
Un revisor también se equivoca, y uno que cita líneas de otro PR o de `main` se equivoca más.

Clasifícala:

| Veredicto | Cuándo |
|---|---|
| `aceptada` | reproduces el problema en el código: hay que cambiar algo |
| `rechazada` | el código ya lo cubre, o la premisa no se sostiene. Necesita evidencia: archivo, línea y por qué |
| `pregunta` | depende de una decisión de producto o de arquitectura que no te toca a ti |

No aceptes una recomendación por cortesía ni rechaces una por pereza. La evidencia decide.

## 3. Presentar el triaje

Antes de tocar nada, enseña al humano la tabla: revisor, `archivo:línea`, una línea de
resumen, veredicto y, si es `aceptada`, qué piensas cambiar. **Espera su aprobación.** Él
puede volcar un veredicto: es su PR.

## 4. Arreglar lo aceptado

- El cambio más pequeño que resuelve el problema de fondo, no el síntoma citado.
- Si varias recomendaciones son la misma causa, se arregla una vez y se responden todas.
- **Respeta el alcance del PR.** Una recomendación que pide algo de otro PR se responde, no se
  implementa aquí.
- Ejecuta la verificación del repositorio del PR (`./scripts/check.sh`, `make test`, lo que
  use) y no des por bueno lo que no pase.

## 5. Responder los hilos

Una respuesta por hilo, con el comando que imprime `factory feedback`:

```bash
gh api repos/<owner>/<name>/pulls/<pr>/comments/<id>/replies -f body='…'
```

Qué dice cada respuesta:

- **aceptada:** qué se cambió y dónde (`archivo:línea`), en una o dos frases;
- **rechazada:** por qué, con la evidencia del paso 2;
- **pregunta:** qué hace falta decidir y quién decide.

Reglas duras:

- **una por una, con aprobación del humano**: publicar es salir hacia fuera y no se deshace;
- **no resuelvas los hilos** (`resolve`): esa es la señal del revisor, no tuya;
- **no hagas push, merge ni PR** (AGENTS.md). Dejas el commit hecho; el push lo decide el humano.

## 6. Cerrar

Resume: cuántas aceptadas, rechazadas y preguntas, qué commit las implementa y qué queda
pendiente de decisión humana. Si el PR es de este repositorio, anótalo en `progress.md`.
