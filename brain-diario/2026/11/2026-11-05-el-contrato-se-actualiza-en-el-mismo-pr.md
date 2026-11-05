---
id: 2026/11/2026-11-05-el-contrato-se-actualiza-en-el-mismo-pr
type: gotcha
title: El contrato se actualiza en el mismo PR, y el sobre data no se duplica
date: '2026-11-05'
tags:
- cifra-spend
- contrato
- openapi
- revision
keywords:
- contrato
- data
- openapi
- handler
- meta
- notes
- in_out
- mismo
abstract: El contrato publicado (`notes/corporate-api.openapi.yaml`, `notes/modules/…`,
  `spec.md`) **se actualiza en el mismo PR que cambia el comportamiento**.
source: manual
tokens: 580
---

# El contrato se actualiza en el mismo PR, y el sobre data no se duplica

> Cerebro diario · gotcha · 2026-11-05 · manual

El contrato publicado (`notes/corporate-api.openapi.yaml`, `notes/modules/…`, `spec.md`) **se actualiza en el mismo PR que cambia el comportamiento**. Cuando no, el revisor lo encuentra como hilo propio: pasó en #132, #139, #142 y #143, y CodeRabbit lo pidió con las mismas palabras («This behavior-changing PR must update `notes/corporate-api.openapi.yaml`», #143 `handler.go:343`).

**El caso caro: el sobre `data` duplicado.** go-bricks (v0.72.0) ya envuelve lo que devuelve el handler en `{data, meta}`. Devolver un tipo con campo `data` propio produce `{"data":{"data":[…]},"meta":…}`, y el contrato pide un arreglo. Salió tres veces: #131 `handlers/handler.go:73` (`ListUsersResponse`), #132 `in_out.go:34` (detalle) y #136 `in_out.go:57` (`InviteUser`); en #132 el contrato además decía «no `meta`», imposible porque el framework siempre añade `meta.timestamp` y `meta.traceId` (`corporate-api.openapi.yaml:4701`). Ningún test del módulo lo vio porque llamaban al servicio, no a la ruta.

**Otras formas del mismo hallazgo.**

- El `Location` sin el prefijo público `/corporate` (#136 `handler.go:151`).
- Un enum cambiado en el contrato y no en las notas (`SMS`, #139 `Users and Governance.md:78`) y un `400` nuevo sin listar en las respuestas (#139 `openapi:4894`).
- `max=255` en el DTO y el contrato sin tocar (#141 `in_out.go:107`); el ejemplo `reactivate` del `requestBody` que con `roleId` devuelve `400` (#143 `openapi:4867`).
- Caso de sesión apagada, que es el valor por defecto, sin nombrar en el contrato (#142 `openapi:4740`); decisión de seguridad escrita en `notes/` cuando va en `design.md` (#142 `Users and Governance.md:90`).

**Cómo se comprueba antes de subir.**

```
git diff --name-only origin/main... | grep -E 'handlers?/|in_out\.go|errorcodes\.go|domain/'   # si sale algo...
git diff --name-only origin/main... | grep -E 'openapi|notes/|specs/'                           # ...aquí también tiene que salir
```

Y el que vale más: levantar el servicio y comparar la forma real: `curl -s … | jq 'keys, (.data|type)'`. Un test que ejerce el handler en proceso prueba el enrutado, no el sobre.

**El arreglo.** Devolver el tipo directo con `server.NewResult` y dejar que el framework ponga `data`; actualizar contrato, notas y ejemplos en el mismo commit; un test que lea el body HTTP completo.
