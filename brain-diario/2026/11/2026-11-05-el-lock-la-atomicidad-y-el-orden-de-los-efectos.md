---
id: 2026/11/2026-11-05-el-lock-la-atomicidad-y-el-orden-de-los-efectos
type: gotcha
title: 'Concurrencia y efectos externos: el lock, la atomicidad y el orden estaban
  en el comentario'
date: '2026-11-05'
tags:
- cifra-spend
- concurrencia
- revision
- seguridad
keywords:
- lock
- invite
- service
- cada
- coderabbit
- externo
- rechazos
- rol
abstract: 'Cuatro hallazgos de `grosal-np` comparten una raíz: **la decisión de concurrencia
  o de orden de efectos estaba escrita en el comentario, no en el código**, y varios
  los comprobó él contra PostgreSQL.'
source: manual
tokens: 593
---

# Concurrencia y efectos externos: el lock, la atomicidad y el orden estaban en el comentario

> Cerebro diario · gotcha · 2026-11-05 · manual

Cuatro hallazgos de `grosal-np` comparten una raíz: **la decisión de concurrencia o de orden de efectos estaba escrita en el comentario, no en el código**, y varios los comprobó él contra PostgreSQL.

**Evidencia.**

- **Un lock que nadie más toma.** «D5 already takes this lock» cuando este era el único `FOR UPDATE` de producción: el lock solo cierra la carrera si cada revocación toma el mismo (#137 `invite.go:43`); sin la llamada a `lockCompany` dos bloqueos en carrera pasan (#140 `edit_test.go:15`). La comprobación de último administrador no miraba la compañía inactiva, que `rbac-access-model/spec.md:140` acepta (#140 `edit.go:29`, probado contra PostgreSQL).
- **Comprobar y luego insertar.** `findPerson` y luego `insertPerson` no son atómicos, y todo `23505` se mapeaba a `ErrAlreadyAMember` (CodeRabbit, #135 `invite.go:181`); las escrituras de cuenta y membresía en el pool commitean la primera antes de la segunda (CodeRabbit, #135 `invite.go:105`).
- **El efecto externo va antes que los rechazos.** Los rechazos (rol no asignable, ya miembro, borrado, delegación) viven dentro del SQL de escritura, así que no pueden correr antes de llamar al proveedor de identidad: un caller sin permiso ya había disparado la invitación (#136 `service.go:150`, CodeRabbit #137 `invite.go:128`); el reintento que el doc de `InvalidateUser` promete no existía (#142 `service.go:367`; `me/service/session.go` ya reintenta con `closeOnce`).
- **Seguridad que olvida el alcance.** La comparación de «no entrego más acceso del que tengo» ignora el scope: quien tiene X solo vía un rol `PRODUCT` sobre la cuenta A pasa (#137 `invite.go:85`); no mira `c.is_active` ni `pr.is_active` como sí hace la vista (#137 `invite.go:92`, #132 `detail.go:146`).

**Cómo se comprueba antes de subir.** Por cada «atómico», «bajo lock» o «antes de llamar a»: `grep -n 'FOR UPDATE\|lock' internal` y comprobar que **todas** las rutas que invalidan la regla toman el mismo lock; una prueba con dos goroutines; y una pregunta: **si el proveedor externo acepta y la escritura falla, ¿qué queda?** Por cada regla de acceso: ¿lo prueba un caso con rol de alcance `PRODUCT` y otro con compañía inactiva?

**El arreglo.** Decidir en Go, sobre la transacción que escribe, con la fila bloqueada, los rechazos antes del efecto externo, y la compensación escrita. Lo que se difiere va a `tasks.md` (#136 `service.go:150`, #137 `tasks.md:216`).
