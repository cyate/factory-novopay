## ADDED Requirements

### Requirement: Precedencia entre los cerebros y la documentación del harness

`docs/harness/cerebros.md` SHALL fijar qué fuente manda cuando dos se contradicen, en este orden: los documentos del propio repositorio que se revisan con el código (`AGENTS.md`, `docs/harness/`, las specs de `openspec/specs/`) mandan sobre los cerebros en todo lo que sea contrato, alcance o verificación de este repositorio; los cerebros mandan sobre la documentación general y sobre las skills externas en todo lo que sea experiencia de uso: trampas observadas, costes medidos y errores ya cometidos.

Quien encuentre una contradicción SHALL dejarla registrada —en `progress.md` o como nota del cerebro diario— en lugar de elegir una fuente en silencio.

#### Scenario: El cerebro contradice una spec del repositorio

- **WHEN** una nota del cerebro describe un comportamiento distinto del que fija una spec de `openspec/specs/`
- **THEN** manda la spec, y la contradicción queda registrada para corregir la nota

#### Scenario: El cerebro contradice a una skill externa

- **WHEN** una nota del cerebro registra una trampa observada que contradice lo que afirma una skill o un documento general
- **THEN** manda el cerebro, y la decisión se dice donde vive el trabajo, no solo en el chat
