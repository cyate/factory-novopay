---
id: 2026/11/2026-11-05-los-escenarios-del-ticket-son-la-lista-de
type: gotcha
title: 'Los escenarios del ticket son la lista de comprobación: cada hueco vuelve
  como bloqueante'
date: '2026-11-05'
tags:
- cifra-spend
- criterios
- revision
- spec
keywords:
- ticket
- cada
- escenario
- in_out
- directory
- escenarios
- linea
- abierto
abstract: 'Los escenarios del ticket son una lista de comprobación: cada uno que el
  PR no cubre vuelve como hilo bloqueante, y a veces cuesta una migración.'
source: manual
tokens: 594
---

# Los escenarios del ticket son la lista de comprobación: cada hueco vuelve como bloqueante

> Cerebro diario · gotcha · 2026-11-05 · manual

Los escenarios del ticket son una lista de comprobación: cada uno que el PR no cubre vuelve como hilo bloqueante, y a veces cuesta una migración. `grosal-np` los cita por número (`SPD-191 Sc.8`) y compara la implementación línea por línea con la frase del ticket.

**Evidencia, por tipo de hueco.**

- **Validación a medias.** «4 a 255 caracteres»: solo existía el mínimo y `block_reason` es `TEXT` sin tope (#140 `transition.go:58`, #141 `in_out.go:107`); nombre «2 a 60 letras, espacios y acentos» (#136 `in_out.go:43`); búsqueda desde 2 caracteres, teléfono desde 6 solo dígitos, filtro de rol «No role», filtro desconocido → `400 INVALID_FILTER` (#131 `query.go:119,135,288`, `directory.go:225`); `AdditionalProperties: false` que descartaba campos en silencio (#143 `in_out.go:116`).
- **Valores por defecto.** El listado excluye `ARCHIVED` sin `filter[status]`; 20 por página, máximo 100, página vacía tras la última (#131 `directory.go:213`, `query.go:48`).
- **Reglas de autoría.** Nadie se bloquea a sí mismo (#141 `service.go:259`, Sc.8); roles adicionales «solo activos» (#135 `domain/invite.go:16`); permiso `control_center.users.read`/`.write` en vez de `.view`/`.manage` (#131 `permissions.go:10`, #136 `permissions.go:15`), que además queda escrito en filas de auditoría que no se pueden corregir (#134 `module.go:102`).
- **Efectos que el escenario pide.** Bloquear cierra la sesión (#142 `module.go:238`: con `custom.session.enabled` por defecto devolvía 200 y no cerraba nada); si el proveedor no envía, el usuario no se crea (#137 `po-questions.md:171`); la invitación caduca a las 24 h; un cambio de rol genera solicitud de cambio de perfil, no un `400` «for good» (#143 `in_out.go:127`).
- **Campos que el contrato exige y la proyección omite.** `status_changed_at` (#131 `directory.go:106`); quién bloqueó (#132 `detail.go:119`).

**Cómo se comprueba antes de subir.** Se extraen los escenarios del ticket y se mira que cada uno tenga un test con su comportamiento:

```
# una línea por escenario del ticket, y para cada una:
grep -rniE '<palabra-clave-del-escenario>' internal --include='*_test.go'
```

Si el escenario depende de otro PR de la pila, no se marca hecho: queda abierto en `tasks.md` con su número (#134 `tasks.md:159`, #132 5.3b/5.3c).

**El arreglo.** Implementar o dejar abierto y escrito; nunca cerrar la tarea con la mitad del escenario.
