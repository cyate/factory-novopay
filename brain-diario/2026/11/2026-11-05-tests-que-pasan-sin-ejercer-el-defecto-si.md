---
id: 2026/11/2026-11-05-tests-que-pasan-sin-ejercer-el-defecto-si
type: gotcha
title: 'Tests que pasan sin ejercer el defecto: si quitas la línea que protege, nada
  se pone rojo'
date: '2026-11-05'
tags:
- cifra-spend
- revision
- tests
keywords:
- test
- caso
- fixture
- linea
- nombra
- nombre
- promete
- protege
abstract: 'El test existe y pasa, y aun así el defecto vivía justo donde nadie miraba:
  `grosal-np` lo marcó cuando **quitar la línea que protege no pone nada en rojo**,
  y por eso es bloqueante, no menor.'
source: manual
tokens: 607
---

# Tests que pasan sin ejercer el defecto: si quitas la línea que protege, nada se pone rojo

> Cerebro diario · gotcha · 2026-11-05 · manual

El test existe y pasa, y aun así el defecto vivía justo donde nadie miraba: `grosal-np` lo marcó cuando **quitar la línea que protege no pone nada en rojo**, y por eso es bloqueante, no menor.

**Evidencia.**

- **Texto en lugar de comportamiento.** Un test que solo busca una cadena en la constante SQL: sin la llamada a `d.lockCompany` en `Block`, las dos suites siguen verdes y nada protege contra dos bloqueos en carrera (#140 `edit_test.go:15`).
- **Lo que fija es otra cosa.** Un test «que se entera de una decisión» y sigue pasando porque solo comprueba el 403 (#131 `service_test.go:178`); el mensaje promete más que la aserción: se cuentan 7 membresías y nunca se lee el motivo (#122 `user_role_scenarios.sql:120,186,240,279,323`); una línea que revisa el nombre de un trigger y no ejecuta ninguno de los caminos que nombra (:351); un caso que nombra «dos roles suman» con los mismos hechos del caso anterior (#140 `administrators_test.go:44`); «Quitar el log no rompe el test, y es lo que el PR promete» (#142 `service_test.go:859`).
- **El fixture no tiene el caso.** Sin persona borrada por GDPR, sin rol de alcance `PRODUCT`, sin filas en `membership_role`: `erased`, el alcance y los roles adicionales no se ejercitan (#140 `edit_integration_test.go:157,173`). El rol de sistema «sin rol» no tiene test (#137 `delegation.go:26`).
- **Pruebas que fijan una regla prohibida o descartada.** El trigger append-only (#134 `audit_integration_test.go:85`), `enforceNow`/`TestTheSchemaWouldHaveRefusedItToo` (#140 `edit_integration_test.go:126`), `TestAnEmailThatAlready…` que fijaba lo que Plane prohíbe (#135 `…_test.go:147`), `invite_test.go:30` que exigía que Go **no** nombre el estado.
- **Código de test sin llamador** (`Edit` de `fakeDirectory`, #143 `http_test.go:67`) y cuerpos duplicados (#143 `service_test.go:1041`).

**Cómo se comprueba antes de subir.** Mutación a mano, un minuto: se borra la línea que debería proteger (el lock, el `uuid.Validate`, la fila de auditoría, el log) y se corre el test: **tiene que ponerse rojo**. Y la pregunta sobre el nombre: ¿el fixture contiene el dato que el test dice ejercitar? `grep -c` sobre el fixture, no sobre el test.

**El arreglo.** El test que ejerce el comportamiento (con el servicio real o la ruta), un fixture con el caso borde, y la aserción que nombra lo que el mensaje promete. Si el test es incorrecto, no se debilita: se documenta y se pide revisión.
