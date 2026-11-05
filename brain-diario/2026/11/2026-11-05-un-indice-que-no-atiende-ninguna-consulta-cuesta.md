---
id: 2026/11/2026-11-05-un-indice-que-no-atiende-ninguna-consulta-cuesta
type: gotcha
title: Un índice que no atiende ninguna consulta cuesta escritura y no da nada
date: '2026-11-05'
tags:
- base-de-datos
- cifra-spend
- indices
- revision
keywords:
- consulta
- indice
- cast
- columna
- like
- scan
- atiende
- comentario
abstract: Un índice que ninguna consulta usa **cuesta escritura y no da nada**, y
  `grosal-np` midió cada uno con `EXPLAIN` antes de rechazarlo.
source: manual
tokens: 440
---

# Un índice que no atiende ninguna consulta cuesta escritura y no da nada

> Cerebro diario · gotcha · 2026-11-05 · manual

Un índice que ninguna consulta usa **cuesta escritura y no da nada**, y `grosal-np` midió cada uno con `EXPLAIN` antes de rechazarlo. Salió en tres formas.

**Evidencia.**

- **El operador no lo usa.** #122 `V7__add_user_search_column.sql:26`: índice sobre `search_text` con `varchar_pattern_ops`. Medido en PostgreSQL 16 con 40.000 usuarios, `enable_seqscan` y `enable_sort` apagados, no sirve ni a `ORDER BY` ni a `LIKE '%t…%'`; solo a `LIKE 'ana%'`. #131 `directory.go:173,214` lo confirmó en PG18: el código envolvía el término en `%…%` y ordenaba por esa columna, así que hacía Seq Scan + Sort y el comentario decía otra cosa.
- **La consulta lo esquiva.** `m.external_id::TEXT = $2` en `edit.go:35,51,61` (#140) impide usar `uk_company_membership__external_id`; `resend.go:23` ya comparaba sin cast.
- **La regla lo deja sin uso.** Un unique parcial sobre membresías vivas, cuando el correo queda ocupado en cualquier estado y la reactivación vuelve a la misma fila: nunca atiende un caso, y además responde `23505` junto a una fila viva (#133 `…unique_key_to_live_memberships.sql:21`).

**Cómo se comprueba antes de subir.** Se escribe la consulta que lo justifica y se mide, no se razona:

```
SET enable_seqscan = off; SET enable_sort = off;
EXPLAIN SELECT … ;     -- debe decir Index Scan/Index Only Scan sobre el índice nuevo
```

Y `grep -rn "<columna>" internal --include='*.go'` para ver quién la consulta, con qué operador y con qué cast. Si la consulta aún no existe en la pila, el índice no entra: se crea en el PR de la consulta.

**El arreglo.** Quitar el índice, o cambiar la consulta para que lo use (`LIKE 'x%'` con `text_pattern_ops`, sin cast sobre la columna), con la medición en el comentario de la migración (una línea, máximo tres).
