---
id: 2026/11/2026-11-03-el-esquema-rbac-vive-de-triggers-y-vistas
type: gotcha
title: 'El esquema RBAC vive de triggers y vistas: 45 objetos que la regla prohibe'
date: '2026-11-03'
tags:
- base-de-datos
- cifra-spend
- migraciones
- planificacion
- rbac
keywords:
- regla
- triggers
- cualquier
- constraint
- deciden
- prohibe
- administrador
- cada
abstract: El esquema RBAC de `cifra-spend-corporate-api-go` esta construido sobre
  exactamente lo que la regla de la casa prohibe.
source: manual
tokens: 574
---

# El esquema RBAC vive de triggers y vistas: 45 objetos que la regla prohibe

> Cerebro diario · gotcha · 2026-11-03 · manual

El esquema RBAC de `cifra-spend-corporate-api-go` esta construido sobre
exactamente lo que la regla de la casa prohibe. Medido el 2026-11-03 sobre
`migrations/tenant/`, con `V1` a `V9` aplicadas:

| Tipo | Cantidad | Migraciones |
| --- | --- | --- |
| Funciones | 13 | V1, V2, V6 |
| Triggers | 20 | V1, V2 |
| Constraint triggers (diferidos) | 8 | V2 |
| Vistas | 4 | V1, V5 |

**Lo que deciden, no solo cuantos son.** No son objetos accesorios: son las
reglas del dominio.

- `fn_reject_company_without_admin` y sus ocho constraint triggers deciden la
  regla del ultimo administrador.
- `vw_role_effective_permission` y `vw_membership_effective_permission`
  deciden que concede cada rol y cada membresia.
- `fn_activate_membership` pasa de Invitado a Activo, y **no tiene llamador en
  Go**: una persona invitada entra y se encuentra el portal vacio.
- `fn_reject_membership_reactivation` prohibe reactivar, lo que contradice la
  epica de usuarios.
- Dos triggers hacen `aud_access_event` append-only.
- `fn_set_updated_at` mantiene `updated_at` en todas las tablas.
- Diez triggers `__notify_rbac_change` invalidan cache por `NOTIFY`.

**Por que esto importa al planificar, y no solo al revisar.** La estimacion
ingenua es «aplicar la regla al codigo nuevo». La real es que cualquier lectura
de permisos efectivos, cualquier regla de ultimo administrador y cualquier
garantia de auditoria que uno quiera usar **ya vive ahi**, asi que construir
encima incumple la regla sin escribir una sola linea de SQL nueva. Eso bloqueo
cuatro PRs seguidos en una sola revision.

**El coste tecnico concreto.** Un constraint trigger diferido juzga en el
`COMMIT`. Su rechazo llega como `check_violation` a mitad del commit, y
`classify()` pasa cualquier `PgError` sin clasificar: sale como **500**. La
misma regla escrita en Go contesta **422** con un codigo que el cliente
entiende. Esa diferencia es la razon practica de la regla, por encima del
estilo.

**Lo que ya se movio a Go** (modulo de usuarios): `updated_at` explicito en las
seis sentencias de escritura, y el conteo de administradores sobre la empresa
bloqueada con `FOR UPDATE`, con la definicion copiada de `V2` al pie. Sigue
leyendose `vw_role_effective_permission` en ese conteo: es la violacion viva, y
retirarla es rediseno, no retoque.
