---
id: 2026/11/2026-11-05-constantes-copiadas-errores-duplicados-y-codigo-sin-llamador
type: pattern
title: 'Constantes copiadas, errores duplicados y código sin llamador: una búsqueda
  antes de dejarlos'
date: '2026-11-05'
tags:
- cifra-spend
- duplicacion
- go
- revision
keywords:
- grep
- busqueda
- constante
- error
- include
- internal
- llamador
- codigo
abstract: 'Tres hallazgos menores se repitieron lo bastante como para pedirse con
  la misma frase: «Duplicated Code», «Speculative Generality» y código sin llamador.'
source: manual
tokens: 524
---

# Constantes copiadas, errores duplicados y código sin llamador: una búsqueda antes de dejarlos

> Cerebro diario · pattern · 2026-11-05 · manual

Tres hallazgos menores se repitieron lo bastante como para pedirse con la misma frase: «Duplicated Code», «Speculative Generality» y código sin llamador. No son bloqueantes, pero sumaron una docena de hilos que se evitan con una búsqueda.

**Evidencia.**

- **Constante copiada.** `"X-Tenant-ID"` por quinta vez cuando `middleware/session.TenantHeader` está exportado (#142 `handler.go:32`); `PermissionManageUsers` repetida en `domain` cuando `domain` ya importa `platformauth` (#140 `administrators.go:5`); la lectura de timings sin `platformsession.TimingsFrom(settings)` como en `middleware/auth/session.go:66` (#142 `module.go:241`).
- **Dos copias del mismo error.** `ErrArchived` (#140, que nadie compara ni retorna) y `users.ErrArchivedReadOnly` con el mismo mensaje (#143 `transition.go:86`, #140 `edit.go:24`); `trimmed` repetido (#143 `service.go:420`); `contains` cuando `slices.Contains` ya lo hace (#140 `transition.go:64`).
- **Ceremonia.** `Query/Next/Scan/Err` para una sentencia que siempre devuelve una fila (#138 `resend.go:86`); `errors.Is(...)` evaluado dos veces en lugar de un `switch` (#139 `service.go:200`); `nullif($5,'')` normalizando en SQL cuando un `*string` nil ya se bindea como NULL (#136 `invite.go:54`).
- **Sin llamador.** `Edit` de `fakeDirectory` (#143 `http_test.go:67`); `liveMembershipSQL` y `alreadyAMember` tras el cambio de `personFor` (#135 `invite.go:71`); una constante entre el doc de `companyID` y `companyID` (#141 `service_test.go:25`).

**Cómo se comprueba antes de subir.** Por cada literal, constante o error nuevo, una búsqueda antes de dejarlo:

```
grep -rn '"X-Tenant-ID"\|<literal>' internal --include='*.go' | grep -v _test
grep -rn '<NuevoSentinel>\|errors.New(".*")' internal --include='*.go'
# símbolo nuevo sin usos fuera de su definición y sus tests:
grep -rn '\b<Simbolo>\b' internal --include='*.go' | grep -v '_test.go' | wc -l    # 1 = solo la definición
```

**El arreglo.** Reutilizar lo exportado; un solo error por significado; borrar lo que ningún PR de la pila usa. Si lo va a usar el PR siguiente, se introduce en ese.
