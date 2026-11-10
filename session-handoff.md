# Handoff de sesión

> Plantilla de entrega compacta. Se sobrescribe en cada handoff; el historial vive en `progress.md` y en git.

Última actualización: sesión 025 — 2026-11-10, `main` con el árbol limpio (sin push).

## Verificado ahora

- La retro está aplicada entera en `main`:
  - reglas cortas: CLAUDE.md de 2,3 KB, cifra en `docs/harness/cifra.md`, checker con dos rondas como máximo;
  - guardrails: hook pre-commit con ruff, pre-push con `check.sh`, pytest en paralelo;
  - borrado lo que no se usaba: panel, tick, land, intake, team, strands e inyección. El motor `goal run` queda congelado;
  - 3 agentes: `ingeniero-software`, `checker` (ejes spec y estándares) y `seguridad`;
  - OpenSpec solo con los comandos `/opsx:*`.
- Un cambio pequeño (menos de 3 archivos y sin capacidad nueva) se cierra con `check.sh` en verde y commit.
- `./scripts/check.sh` → código 0, 431 tests en ~9 s.
- Último commit: `1a2213b`.

## Fuera del repositorio (configuración del usuario)

- `~/.claude/agents/`: `product-owner` y `entrega-qa`, los que sirven a cifra.
- `~/.claude/settings.json` y `~/.claude/CLAUDE.md` sin jbcontext. La búsqueda de código va floorplan → grep.
- La configuración global de OpenSpec está en `delivery: commands`.
- Las memorias de cifra están en el proyecto `cifra-spend-corporate-api-go`. Las notas sueltas de cifra, en `~/NOVOPAYMENT/cifra-spend/notas-desde-factory-novo/`.
- Respaldo del trabajo descartado (strands): ramas `respaldo/wip-2026-11-10` y `respaldo/wip-2026-11-10-b`.

## Estado y siguiente paso

- El detalle está en `progress.md`, sesión 025, y en `docs/historial/progress-sesiones.md`.
- Mejor próximo paso: usar el harness ligero en trabajo real y medir otra retro.
- Abierto, de baja prioridad: el paso «ajustes del bot» de `scripts/pre-pr.sh` no tiene test con `gh`. Las ramas de respaldo se pueden borrar cuando ya no hagan falta.

## Comandos

- Arranque: `.venv/bin/factory doctor` (`./init.sh` solo si falta `.venv` o el doctor falla)
- Verificación: `./scripts/check.sh`
- Antes de un PR: `./scripts/pre-pr.sh [base]`
- Features: `.venv/bin/factory features list`
- Mapa del código: `node floorplan/query.mjs find "<palabras>"`
