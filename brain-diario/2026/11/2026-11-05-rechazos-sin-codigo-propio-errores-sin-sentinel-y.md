---
id: 2026/11/2026-11-05-rechazos-sin-codigo-propio-errores-sin-sentinel-y
type: gotcha
title: Rechazos sin código propio, errores sin sentinel y 500 donde toca 4xx
date: '2026-11-05'
tags:
- cifra-spend
- errores
- go
- revision
keywords:
- codigo
- edit
- errores
- existe
- module
- nil
- propio
- responde
abstract: Un rechazo que el cliente no puede distinguir por su código, o un error
  que se pierde en el camino, vuelve como hallazgo.
source: manual
tokens: 605
---

# Rechazos sin código propio, errores sin sentinel y 500 donde toca 4xx

> Cerebro diario · gotcha · 2026-11-05 · manual

Un rechazo que el cliente no puede distinguir por su código, o un error que se pierde en el camino, vuelve como hallazgo. La regla de la casa es doble: **el motivo de cara al cliente es el propio `error.code`** y los errores se envuelven con `%w` sobre los sentinels del paquete.

**Evidencia.**

- **Rechazo sin código propio.** «the request names no change» como mensaje de un código genérico (#143 `handler.go:189`; el spec dice «A refusal is told apart by its code»). Un fallo del proveedor que `mapError` no conoce acaba en `500 the users request failed` cuando el ticket pide «We couldn't send the invitation» (#136 `service.go:150`); el fallback 500 sin mensaje de la operación (#136 `handler.go:146`); `LAST_ADMIN` documentado como 409 en el spec y lanzado con otro código (#141 `errorcodes.go:121`).
- **Un 500 donde toca 4xx.** Un `roleId` que no es UUID responde 400 cuando el contrato pide `422 UNKNOWN_ROLE` (#136 `in_out.go:51`); un no-UUID llega al driver y vuelve como 500: falta `uuid.Validate` en el reenvío (#139 `service.go:207`); un fallo a mitad del scan sale como 500 en vez de 503 (#140 `edit.go:123`).
- **Sin `%w` o sin sentinel.** `return rows.Err()` crudo junto a dos ramas que sí clasifican (#140 `edit.go:123`, #137 `invite.go:280`); `ErrSubjectTaken` con el correo dentro del texto y sin mapeo, que acaba en el log como dato personal (#135 `invite.go:223`).
- **Dos causas, una respuesta.** `n == 0` junta «no existe» con «existe en otro estado», y una carrera responde 404 sobre alguien que existe (#140 `edit.go:153`; #138 ya lo había resuelto).
- **Rechazos inalcanzables.** `s.Inviter == nil` responde 503 antes de cualquier regla, y `module.go` no conecta ningún `Inviter`: toda petición permitida da 503 y ni el 403 ni el 422 se alcanzan (#137 `INTENT.md:114`, #139 `service.go:204`).
- **Errores tragados.** `LoadSessionSettings` falla y `Sessions` queda `nil` sin log (#142 `module.go:216`); un `InjectInto` que devuelve `err` crudo cuando los módulos vecinos registran y degradan (#134 `module.go:47`).

**Cómo se comprueba antes de subir.**

```
git diff -U0 origin/main... -- '*.go' | grep -nE '^\+.*(errors\.New|fmt\.Errorf)\(' | grep -v '%w'
curl -s -o /dev/null -w '%{http_code}\n' -X POST .../users -d '{"roleId":"no-es-uuid"}'   # nunca 500
```

Y por cada `if x == nil { return … }` anterior a las reglas: ¿se llega a las reglas en producción, con el módulo real cableado?
