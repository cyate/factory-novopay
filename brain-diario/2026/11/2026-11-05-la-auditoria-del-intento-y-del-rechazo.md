---
id: 2026/11/2026-11-05-la-auditoria-del-intento-y-del-rechazo
type: gotcha
title: 'La auditoría del intento y del rechazo: lo que no se guarda hoy no se guarda
  nunca'
date: '2026-11-05'
tags:
- auditoria
- cifra-spend
- revision
- seguridad
keywords:
- audit
- auditoria
- contexto
- guarda
- rechazo
- cliente
- columna
- escritura
abstract: Un rechazo o un acceso denegado que **no deja rastro**, o que deja un rastro
  que no se puede completar después, es un hallazgo bloqueante, porque la tabla de
  auditoría es append-only y no admite corrección.
source: manual
tokens: 593
---

# La auditoría del intento y del rechazo: lo que no se guarda hoy no se guarda nunca

> Cerebro diario · gotcha · 2026-11-05 · manual

Un rechazo o un acceso denegado que **no deja rastro**, o que deja un rastro que no se puede completar después, es un hallazgo bloqueante, porque la tabla de auditoría es append-only y no admite corrección. `grosal-np` lo encontró en #134, #137, #141 y #143.

**Evidencia.**

- **El contexto de la petición cancela la escritura.** Si el cliente corta la conexión, la fila de auditoría no se escribe, y es quien recibe el rechazo quien decide si queda rastro: usar `context.WithTimeout(context.WithoutCancel(ctx), …)` (#134 `audit.go:40`).
- **La columna no cabe.** `correlation_id` es `VARCHAR(100)` (V1:447), el middleware acepta 1 a 128 caracteres: con id largo la columna queda `NULL` y `traceId` leerá null (#134 `repository/audit.go:25,59`). Con `sel.OrgID` numérico el INSERT daba `22P02`, no `ErrCompanyUnknown`: sin fila (#134 `audit.go:27`).
- **Un dato del cliente entra sin filtro.** El header de correlación acepta `^[A-Za-z0-9_-]{1,128}$`, o sea un PAN, en una tabla con `pci_scope: FALSE` (#134 `audit.go:36`).
- **Denegaciones sin registrar.** Sin company en la sesión y sub-rutas sin ruta registrada (#134 `audit.go:42,53`); un 403 distinto de `PERMISSION_DENIED` que `deniedByPermission` no reconoce (#137 `handler.go:185`).
- **Falta el evento.** «User invited», «User blocked» (con motivo), «User unblocked», y la edición con nombres de campos y nunca valores, en la misma transacción que la escritura (#136 `handler.go:148`, #141 `service.go:308`, #143 `service.go:345`). Hasta entonces `unblockSQL` borra el motivo, y el comentario que dice que sobrevive es falso (#140 `edit.go:54`).
- **Se pierde el contexto del intento.** En `GET /users/{userId}` no queda qué usuario se pidió, ni `ip`, ni `userAgent` (#134 `domain/audit.go:39`).

**Cómo se comprueba antes de subir.** Por cada rechazo nuevo: `grep -n 'denied\|Audit' internal/modules/<mod>`, y una prueba que corte el contexto a mitad. Por cada columna que escribe un dato del cliente: comparar su longitud con la DDL (`grep -n 'VARCHAR' migrations/`) y preguntarse qué pasa si el valor es más largo, numérico o con forma de PAN. Sin poder completar después, **lo que no se guarda hoy no se guarda nunca**.

**El arreglo.** Escritura de auditoría con contexto desacoplado, clasificación antes del INSERT, un identificador del servidor en vez del header, y tarea abierta hasta que el evento exista.
