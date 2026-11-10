# Handoff de sesión

> Plantilla de entrega compacta. Se sobrescribe en cada handoff; el historial vive en `progress.md` y en git.

Última actualización: sesión 024 — 2026-11-10, rama `chore/borrar-ceremonia` (sin integrar en `main`).

## Verificado ahora

- Se borraron los subsistemas sin uso real: panel, `status`, `tick`, `land`, `schedule`, `intake`, `inbox`, `team`, capturas del cerebro y su inyección. El CLI queda en `init`, `features`, `goal`, `brain`, `feedback`, `complexity` y `doctor`.
- `./scripts/check.sh` → 0 y `./scripts/pre-pr.sh <commit anterior>` → «Puerta abierta» en cada commit.

## Estado y siguiente paso

- El detalle (commits, qué se conserva congelado y por qué, decisiones pendientes) está en `progress.md`, sesión 024.
- Mejor próximo paso: decidir sobre la rama (integrarla es decisión humana) y las decisiones 9–10 de `progress.md`.

## Comandos

- Arranque: `./init.sh`
- Verificación: `./scripts/check.sh`
- Features: `.venv/bin/factory features list`; auditoría: `.venv/bin/factory doctor`
