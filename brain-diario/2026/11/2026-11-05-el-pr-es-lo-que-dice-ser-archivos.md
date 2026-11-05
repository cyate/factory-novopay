---
id: 2026/11/2026-11-05-el-pr-es-lo-que-dice-ser-archivos
type: gotcha
title: 'El PR es lo que dice ser: archivos ajenos, tareas marcadas sin hacer y lo
  diferido sin escribir'
date: '2026-11-05'
tags:
- alcance
- cifra-spend
- revision
- tasks
keywords:
- tasks
- tarea
- diferido
- diff
- git
- tareas
- trabajo
- archivos
abstract: 'El PR debe ser lo que dice ser: sin archivos de otro trabajo, sin tareas
  marcadas que no están hechas, y con lo diferido escrito.'
source: manual
tokens: 558
---

# El PR es lo que dice ser: archivos ajenos, tareas marcadas sin hacer y lo diferido sin escribir

> Cerebro diario · gotcha · 2026-11-05 · manual

El PR debe ser lo que dice ser: sin archivos de otro trabajo, sin tareas marcadas que no están hechas, y con lo diferido escrito. `grosal-np` y `pnadal` lo trataron como bloqueante de **estándares**, no de código.

**Evidencia.**

- **Archivo suelto.** Un `…ship_archival_and_reactivation.sql.fixed` idéntico byte a byte a `V6` dentro del PR (#122); un paquete `entregas/SPD-37/` de otro trabajo, con épica en lugar de Change y dependencia de #164 (#143 `README.md:1`); un arreglo del listado dentro del PR de edición: «va en el PR que lo introdujo» (#143 `directory.go:127`).
- **Borrador viejo que revierte trabajo.** `07f6d08` revirtió 50 líneas de la base, entre ellas las tareas 3.3b, 3.3d, 3.9, 5.3d, 6.5c, 7.3b (#133 `tasks.md:90`); la descripción del PR cita un commit que ya no está en la rama (#131 `tasks.md:124`).
- **Lo diferido sin tarea.** «Lo que tu respuesta dejó para otro PR no tiene tarea» (#132 `detail.go:223`, `openapi:9608`); OTP, auditoría de la invitación y vencimiento sin tarea (#136 `tasks.md:179`, #137 `tasks.md:216,255`); «dos veces 7.2» (#143 `tasks.md:330`); una decisión de seguridad suelta en `notes/` en lugar de `design.md` con quién la aceptó (#142).
- **Contradicciones internas.** `1.4b` contradice `1.4c` y D1b; el backfill y el comentario de `V6` quedaron obsoletos (#173 `tasks.md:56,57`, `spec.md:38,49`, de `pnadal`, y CodeRabbit en `tasks.md:57`).
- **Tarea descrita como presente cuando ya se retiró.** `fn_activate_membership` borrada en V6:62 (#137 `tasks.md:255`).

**Cómo se comprueba antes de subir.**

```
git diff --stat origin/main...                                   # ¿hay algo que no es de esta tarea?
git diff --name-only origin/main... | grep -E 'entregas/|\.fixed|\.orig'
git cat-file -t <sha-citado-en-la-descripcion>                    # ¿existe en esta rama?
grep -nE '^\s*- \[x\]' openspec/changes/*/tasks.md | …            # por cada [x]: ¿lo hace el diff?
```

Y la pregunta: **si alguien lee solo `tasks.md`, ¿ve lo que falta y lo que ya no aplica?**

**El arreglo.** Sacar lo ajeno; restaurar la base y reaplicar solo lo propio; abrir tarea por cada diferido; superseder explícitamente lo que cambió de decisión; actualizar la descripción con los commits actuales.
