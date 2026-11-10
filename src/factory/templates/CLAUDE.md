@AGENTS.md

## Notas para Claude Code

- Antes de declarar terminada una feature, pide una revisión independiente (un subagente de solo lectura) pasándole el diff y los criterios, no tu razonamiento. Dos rondas como máximo: si siguen abiertos hallazgos, pregunta al usuario.
- Para trabajo largo o desatendido usa `factory goal run` en lugar de encadenar prompts a mano.

<!-- Generado por factory. Adaptado de walkinglabs/learn-harness-engineering (MIT). -->
