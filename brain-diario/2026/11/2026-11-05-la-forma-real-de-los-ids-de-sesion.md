---
id: 2026/11/2026-11-05-la-forma-real-de-los-ids-de-sesion
type: gotcha
title: 'La forma real de los ids de sesión no es la que el código supone: OrgID numérico'
date: '2026-11-05'
tags:
- cifra-spend
- ids
- revision
- sesion
keywords:
- sesion
- uuid
- real
- service
- columna
- numerico
- companyid
- forma
abstract: Hay identificadores cuya **forma real no es la que el código supone**, y
  el fallo no sale hasta que se prueba con una sesión real.
source: manual
tokens: 470
---

# La forma real de los ids de sesión no es la que el código supone: OrgID numérico

> Cerebro diario · gotcha · 2026-11-05 · manual

Hay identificadores cuya **forma real no es la que el código supone**, y el fallo no sale hasta que se prueba con una sesión real. `grosal-np` lo marcó como bloqueante cinco veces, siempre en la misma frontera: el `companyId` de la sesión y los ids que viajan en el contrato.

**Evidencia.**

- **`sel.OrgID` es numérico, no UUID.** `session/module.go:52` lo pone en el contexto y `company-data/design.md:27` lo deja escrito: es el `org_id` numérico de Nuvy. Todo `uuid.Validate` sobre él falla y termina en 403 con sesión real (#131 `service.go:57`, #132 `service.go:91`); en la auditoría da `22P02` en vez de un error de dominio, probado con `100234` (#134 `repository/audit.go:27`). El mapeo se cierra en SPD-318, no en el PR que lo tropieza.
- **Comparar contra la columna equivocada.** El `companyId` de sesión se compara con `company.external_id`, un UUID generado por la base (`gen_random_uuid()`), cuando el dato que corresponde vive en otra columna (#131 `directory.go:187`).
- **Un id guardado en una columna de nombre.** `departmentNodeId` (ejemplo `dep_marketing`, comparado con el scope de la sesión) se llenaba con `area_name`, texto libre (#131 `directory.go:309`, #136 `service.go:156`, #143 `edit.go:251`).
- **Un id que no es UUID llega al driver** y vuelve 500 en vez de 4xx (#139 `service.go:207`).

**Cómo se comprueba antes de subir.** Los tests con UUID inventados no lo ven. Pregunta concreta: **¿hay un test con un `companyId` de la forma que da la sesión real (numérico) y otro con un id mal formado?** Y por cada id que entra: `grep -n 'Validate\|uuid' internal/modules/<mod>/service` y comprobar en la DDL qué columna es y de qué tipo (`grep -n 'external_id\|area_name' migrations/`).

**El arreglo.** Clasificar el id antes de tocar la base, con su test, y dejar escrito en `tasks.md` el PR que fija el mapeo (SPD-318) en lugar de arreglarlo a medias.
