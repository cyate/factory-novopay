---
id: 2026/11/2026-11-05-cuando-plane-openspec-y-las-notas-chocan-gana
type: decision
title: Cuando Plane, openspec y las notas chocan, gana Plane, y el código no fija
  la versión vieja
date: '2026-11-05'
tags:
- cifra-spend
- plane
- revision
- spec
keywords:
- plane
- ticket
- openspec
- transition
- vieja
- decision
- frente
- gana
abstract: Cuando el ticket de Plane, `openspec/` y las notas se contradicen, **gana
  Plane** (decisión del 2026-11-04) y el código no debe fijar la versión vieja.
source: manual
tokens: 538
---

# Cuando Plane, openspec y las notas chocan, gana Plane, y el código no fija la versión vieja

> Cerebro diario · decision · 2026-11-05 · manual

Cuando el ticket de Plane, `openspec/` y las notas se contradicen, **gana Plane** (decisión del 2026-11-04) y el código no debe fijar la versión vieja. `grosal-np` lo escribió literalmente («Plane gana») cuatro veces en #143 y dejó un PR entero (#133) sin mergear por implementar la lectura de openspec en lugar de la del ticket.

**Evidencia: lo que se fijó y se tuvo que invertir.**

- «Archivado es terminal» y «Desactivado solo vuelve por Invitado» frente a SPD-193 («Reactivar: de Desactivado o Archivado a Activo, con sus roles actuales; a Invitado solo quien nunca aceptó»): #133 `…unique_key_to_live_memberships.sql:12,21`, #139 `service.go:224`, #140 `transition.go:35-42` (tabla de transiciones entera), `transition_test.go:28`, #141 `http_test.go:324`, #143 `transition.go:90`, `http_test.go:377`, `openapi:4867`, `tasks.md:357`.
- «Un Invitado no se bloquea» frente a SPD-191 Sc.2: #122 `user_role_scenarios.sql:195`, #140 `transition.go:38`, #141 `service_test.go:703`, #143 `http_test.go:366`.
- «El correo se reutiliza si la cuenta existe» frente a SPD-175 («único entre todos los usuarios, en cualquier estado»): #133 `…sql:21`, #135 `invite.go:166` y `invite_integration_test.go:147`, que fijaba lo contrario.
- Preguntas ya contestadas que seguían abiertas en `po-questions.md` (#133:165, #140:223, #143:249-282).

**Cómo se comprueba antes de subir.** No se puede automatizar del todo, y eso también es información. Lo que sí: (1) abrir el ticket y copiar la frase literal que decide la regla al `tasks.md`; (2) buscar la regla vieja en todo el árbol:

```
grep -rniE 'terminal|only through INVITED|never accepted|archived.*cannot' openspec notes internal --include='*.go' --include='*.md' --include='*.yaml'
```

(3) preguntarse: **¿hay un test que fije lo contrario de un escenario del ticket?** Un test así convierte una decisión vieja en regla.

**El arreglo.** Si el ticket y la spec chocan y no hay decisión, se pregunta a producto antes de codificar (#140 `transition.go:38` quedó como «conflicto para confirmar»). Si la hay, se corrige spec, tabla, tests, contrato y `po-questions.md` en el mismo PR, y se registra quién decidió.
