---
id: 2026/11/2026-11-05-doc-falsa-el-comentario-la-tarea-o-la
type: gotcha
title: 'Doc falsa: el comentario, la tarea o la nota afirma lo que el código no hace'
date: '2026-11-05'
tags:
- cifra-spend
- comentarios
- doc-falsa
- revision
keywords:
- codigo
- tasks
- cierto
- comentario
- escribe
- grep
- hace
- siguiente
abstract: '«Doc falsa» es el hallazgo que más veces nos devolvió `grosal-np` con una
  etiqueta propia: un comentario, un `tasks.md` o una nota que **afirma algo que el
  código no hace**.'
source: manual
tokens: 645
---

# Doc falsa: el comentario, la tarea o la nota afirma lo que el código no hace

> Cerebro diario · gotcha · 2026-11-05 · manual

«Doc falsa» es el hallazgo que más veces nos devolvió `grosal-np` con una etiqueta propia: un comentario, un `tasks.md` o una nota que **afirma algo que el código no hace**. Suele ser peor que no comentar, porque el texto queda en el catálogo y la siguiente persona decide a partir de él.

**Las cuatro formas que se repiten.**

- **Futuro escrito en presente.** «El repositorio la escribe en cada insert» cuando `tasks.md` 3.3b seguía abierta (#122 `V7…sql:11,28`); «ya no ocurre» o «Was a deferred trigger; it left with the others» sobre un trigger que nunca se publicó (#122 `user_role_scenarios.sql:345`); «The screen reads the state view» sobre una vista que no existe (:406).
- **Cierto en este commit, falso en el siguiente de la pila.** «The contract also offers SMS» y #139 quita `SMS` (#138 `domain/users/resend.go:8`, #139 `in_out.go:74`); «archiving is terminal», descartado el 2026-11-04 (#139 `service.go:224`).
- **Absolutos y superlativos.** «el único test que ve lo que ve un cliente» cuando `http_test.go:264` hace lo mismo (#139 `http_test.go:149`); «impossible» donde el filtro `gdpr_erasure_at` lo permite (#139 `service.go:224`); «exactly» que en el código es `> 0` (#122 `user_role_scenarios.sql:189`); «permissions from two roles add up» sin roles en el fixture (#140 `administrators_test.go:44`).
- **Marcar hecho lo que no está.** Tarea `[x]` mientras una denegación sigue sin registrarse (#134 `tasks.md:159`); el comentario dice que el motivo sobrevive en la auditoría y nada la escribe (#140 `edit.go:54`, #141 `handler.go:343`); `LAST_ADMIN` «recorded as a disagreement» sin aparecer en `openspec/` (#141 `errorcodes.go:121`).

**Cómo se comprueba antes de subir.** Se barren los comentarios añadidos buscando las palabras que prometen, y por cada una se abre el código que debería cumplirla:

```
git diff -U0 origin/main... | grep -nEi '^\+.*(//|--|#).*\b(only|every|always|never|impossible|exactly|already|todos?|nunca|siempre|único)\b'
git diff -U0 origin/main... | grep -nEi '^\+.*\b(will|writes it on every|is written by|reads the)\b'
```

Y una pregunta: **¿esto sigue siendo cierto si el PR siguiente de la pila quita o añade algo?** Si no, se escribe lo que es cierto hoy o se deja fuera.

**El arreglo.** Decir solo lo verificable en el commit; lo pendiente va a `tasks.md` como tarea abierta, no como hecho. Cuando una decisión cambia, se busca el texto viejo en todo el árbol (`grep -rniE 'terminal|no vuelve' openspec notes internal`), no solo en el archivo que se tocó (#141 `spec.md:106` quedó diciendo lo viejo tras editar el párrafo).
