---
id: 2026/11/2026-11-03-en-la-base-solo-tablas-claves-e-indices
type: decision
title: 'En la base solo tablas, claves e indices: las reglas van en Go'
date: '2026-11-03'
tags:
- base-de-datos
- cifra-spend
- go
- migraciones
- revision
keywords:
- trigger
- base
- regla
- sql
- tablas
- contar
- cuatro
- indices
abstract: En la base de datos solo pueden existir **tablas** y **constraints** (claves
  foráneas e índices).
source: manual
tokens: 583
---

# En la base solo tablas, claves e indices: las reglas van en Go

> Cerebro diario · decision · 2026-11-03 · manual

En la base de datos solo pueden existir **tablas** y **constraints** (claves foráneas e
índices). Toda validación y toda regla de negocio se resuelve en código Go.

Quedan fuera, sin excepción: triggers, funciones, procedimientos almacenados, vistas, y
los `CHECK` que codifican una regla de negocio.

**Quién lo pidió y dónde.** Gabriel Rosales (`grosales-np`), revisando la pila de
`cifra-spend-corporate-api-go` el 2026-11-03, con palabras suyas: «no quiero ver lógica o
reglas de validación en BDD. Para que quede más claro, en BDD sólo pueden existir: Tablas,
Constraints (FK e índices; validaciones se hacen en código go)».

**Por qué importa, medido.** Bloqueó cuatro PRs seguidos por esto, y los cuatro eran
*dependencias nuevas* sobre objetos que ya estaban en el esquema, no objetos nuevos. Esa es
la trampa: la regla parece cumplirse mientras nadie escriba un trigger, y se incumple
igual leyendo uno. Los cuatro casos reales fueron:

- leer la vista `vw_role_effective_permission` para contar administradores;
- apoyarse en el trigger diferido `fn_reject_company_without_admin` en vez de contar en Go;
- apoyarse en el trigger append-only de la tabla de auditoria, y fijarlo en un test;
- dejar `updated_at` a cargo del trigger `set_updated_at`.

**Como se incumple sin darse cuenta.** Lo mas caro no fue escribir logica nueva en SQL:
fue construir *encima* de la que ya estaba. Un trigger diferido ademas juzga en el `COMMIT`,
asi que su rechazo llega como fallo de infraestructura --un 500-- y no como respuesta al
cliente. Quien escribe la regla en Go puede contestar 422; quien la deja en la base, no.

**Que hacer en su lugar.** Contar y decidir en Go, sobre la transaccion que escribe y con
la fila bloqueada (`SELECT ... FOR UPDATE`) cuando la decision dependa de lo que otros
puedan cambiar a la vez. Escribir `updated_at` explicitamente en el `UPDATE`. Si una
garantia solo puede vivir en el esquema, es una clave unica o un indice, nunca un trigger.

**Que si es legitimo en SQL.** Leer tablas, unir, filtrar y agregar; y que una sentencia
lleve condicionales (`CASE`, `COALESCE`, `nullif`) impulsados por parametros que decide
Go. La frontera no es «SQL simple contra SQL complejo»: es si la regla **vive** en la base
--y sigue ahi cuando nadie la llama desde Go-- o si la base solo ejecuta lo que Go le pide.

**Ampliación (2026-11-05, destilada de los 16 PRs de la pila).** La regla se repitió más allá
de los triggers, y lo que `grosal-np` marcó cada vez fue una de estas formas:

- *Columna generada*: `search_text GENERATED ALWAYS AS (…) STORED` (#122 `V7…sql:16`), `r.is_active`
  (#135 `invite.go:45`, #137 `invite.go:55`). Se escribe como columna normal desde Go
  (#131 `directory.go:33` fue el primer consumidor).
- *`CHECK` de negocio* (#131 `V8__add_user_mfa_state.sql:16`) y *predicado de negocio en un índice
  único parcial* (#133 `…live_memberships.sql:22`: «el unique está permitido, la validación va en Go»).
- *Vista leída desde Go*: `vw_membership_master_account` (#132 `detail.go:210`),
  `vw_role_effective_permission` (#140 `edit.go:56`). La definición de «administrador» o de
  «efectivo» la decide la base (#137 `invite.go:66`, #140 `edit.go:62`).
- *`updated_at` a cargo de `trg_*__set_updated_at`* en cada `UPDATE` nuevo (#138 `resend.go:41`,
  #140 `edit.go:71`, #143 `edit.go:239`) y el estado inicial a los `DEFAULT` (#135 `invite.go:76,78`).
- *El literal de la regla dentro del `WHERE`* (`membership_status_code = 'ACTIVE'`): como guarda de
  carrera sirve, pero el estado esperado se pasa como parámetro desde Go (#138 `resend.go:47`,
  #140 `edit.go:84`).
- *Tests que fijan el trigger* (#134 `audit_integration_test.go:85`, #140 `edit_integration_test.go:126`).

**Cómo se comprueba antes de subir.**

```
git diff -U0 origin/main... -- '*.sql' | grep -niE 'GENERATED|CREATE (OR REPLACE )?(FUNCTION|TRIGGER|VIEW)|CHECK *\(|\$\$'
git diff -U0 origin/main... -- '*.go' | grep -nE '^\+.*(vw_|fn_|trg_)'
git diff -U0 origin/main... -- '*.go' | grep -nE '^\+.*UPDATE ' # cada UPDATE nuevo: ¿escribe updated_at?
```

La pregunta de fondo: **¿mi código se apoya en algo que la base hace sola?** Si la respuesta es
sí, aunque no lo haya escrito yo, es una dependencia nueva y se cuenta como violación.
Ver también: [rechazos sin código propio](2026-11-05-rechazos-sin-codigo-propio-errores-sin-sentinel-y.md) para lo que
ocurre cuando la regla se deja a la base y su rechazo llega como 500.
