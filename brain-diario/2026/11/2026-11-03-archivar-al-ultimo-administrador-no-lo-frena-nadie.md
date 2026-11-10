---
id: 2026/11/2026-11-03-archivar-al-ultimo-administrador-no-lo-frena-nadie
type: gotcha
title: 'Archivar al último administrador no lo frena nadie: el trigger mira cuatro columnas'
date: '2026-11-03'
tags:
- base-de-datos
- cifra-spend
- migraciones
- rbac
- verificacion
keywords:
- trigger
- archived_at
- administrador
- update of
- constraint trigger
- diferido
- simulacion
abstract: El trigger que garantiza que una empresa no se queda sin administrador
  se declara `UPDATE OF` sobre cuatro columnas, y `archived_at` no es ninguna.
source: manual
tokens: 520
---

# Archivar al último administrador no lo frena nadie: el trigger mira cuatro columnas

> Cerebro diario · gotcha · 2026-11-03 · manual

En `cifra-spend-corporate-api-go`, `V2` instala un constraint trigger diferido que
impide dejar una empresa sin administrador activo. Se lee como una garantía del
esquema. No lo es en el camino más nuevo:

```sql
CREATE CONSTRAINT TRIGGER trg_company_membership__require_admin
  AFTER DELETE OR UPDATE OF user_account_id, base_role_id, blocked_at, deactivated_at
  ON company_membership DEFERRABLE INITIALLY DEFERRED ...
```

`archived_at` no está en la lista. `V6` añadió el archivado y no tocó el trigger,
así que archivar al único administrador **commitea** y la empresa queda con cero.

## Cómo se comprobó

Esquema migrado `V1`→`V9` en un `psql` local, una empresa con un solo administrador
activo, los tres caminos seguidos:

- desactivarlo → `ERROR: company 1 would be left without an active administrator`
- cambiarle el rol base → el mismo error
- archivarlo → `COMMIT`, y el recuento de administradores activos da `0`

## Las dos lecciones, que son generales

**Un `UPDATE OF` es una lista blanca que envejece.** El trigger no protege la
tabla: protege las columnas que alguien enumeró el día que lo escribió. Cada
`ADD COLUMN` que represente un estado nuevo es una puerta que ese trigger no mira,
y nada en la migración lo recuerda.

**Una regla partida entre la base y el código no es una regla, son dos.** Mientras
el servicio cubría solo el archivado y el trigger solo los otros cuatro caminos,
el agujero quedaba justo donde ninguno de los dos se sentía responsable. El arreglo
no fue extender el trigger: fue contar en Go sobre la empresa bloqueada
`FOR UPDATE` en **todos** los caminos, y dejar el trigger como redundante.

**Y leer el SQL no bastaba.** La definición está a la vista en `V1`, y yo la había
leído sin ver la lista. Lo que lo encontró fue correr los tres caminos contra una
base real y mirar cuál commiteaba.

Relacionado: [[2026-11-03-en-la-base-solo-tablas-claves-e-indices]],
[[2026-11-03-el-esquema-rbac-vive-de-triggers-y-vistas]]
