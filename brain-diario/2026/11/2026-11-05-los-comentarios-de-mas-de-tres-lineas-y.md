---
id: 2026/11/2026-11-05-los-comentarios-de-mas-de-tres-lineas-y
type: gotcha
title: Los comentarios de más de tres líneas, y los ids de ticket en el código, son
  bloqueantes
date: '2026-11-05'
tags:
- cifra-spend
- comentarios
- estandares
- revision
keywords:
- lineas
- diff
- service
- bloque
- codigo
- ticket
- comentario
- commit
abstract: 'Un comentario de más de tres líneas es bloqueante en esta pila: `CLAUDE.md:25`
  del repositorio de cifra-spend fija el tope en **3 líneas**, y `grosal-np` lo marcó
  en al menos nueve PRs.'
source: manual
tokens: 443
---

# Los comentarios de más de tres líneas, y los ids de ticket en el código, son bloqueantes

> Cerebro diario · gotcha · 2026-11-05 · manual

Un comentario de más de tres líneas es bloqueante en esta pila: `CLAUDE.md:25` del repositorio de cifra-spend fija el tope en **3 líneas**, y `grosal-np` lo marcó en al menos nueve PRs. No es estilo: pidió mover el razonamiento al commit o a `design.md`.

**Evidencia.** #122 `V7__add_user_search_column.sql:6,11,18` (9, 4 y 5 líneas); #134 `module.go:88` (7 líneas), `audit.go:48-51`, `module_test.go:253-257`, `audit_test.go:9-12`, y la frase «ningún linter lo detecta»; #135 `invite.go:55` (9); #137 `delegation.go:18` (8) y `invite_integration_test.go:281`; #139 `in_out.go:74` y `handler.go:239`; #141 `http_test.go:27`: cumplía en la base y el diff lo alargó a 4; #142 `service.go:345` (7); #143 `transition_test.go:59` (15). Variantes del mismo hallazgo: el doc quedó sobre otra declaración (#142 `service.go:345`, #143 `handler.go:169`), un doc de algo que ya no existe (#143 `service.go:72`) y un identificador de ticket dentro del comentario (#141 `service.go:269`, `service_test.go:753`, `http_test.go:416`: «la regla se entiende sin SPD-191»).

**Cómo se comprueba antes de subir.** Sobre lo que el diff añade, no sobre el archivo entero (el diff puede alargar un bloque que ya cumplía):

```
git diff -U0 origin/main... -- '*.go' '*.sql' | awk '/^\+[ \t]*(\/\/|--)/{n++; if(n==4) print "bloque >3 lineas cerca de: "$0; next}{n=0}'
git diff -U0 origin/main... | grep -nE '^\+.*(//|--).*SPD-[0-9]+'
```

El primero solo ve bloques añadidos enteros; si tocaste una línea en medio de un bloque viejo, ábrelo. No hay linter que lo haga: hay que correrlo.

**El arreglo.** Una frase con el dato que el lector no puede sacar del código; el porqué largo va al mensaje de commit o a `design.md`. Los ids de ticket (`SPD-191 Sc.8`) no entran en el código ni en los tests.
