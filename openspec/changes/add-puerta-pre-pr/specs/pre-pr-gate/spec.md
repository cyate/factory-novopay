## ADDED Requirements

### Requirement: Puerta previa a un pull request
El script `scripts/pre-pr.sh` SHALL correr contra el diff, antes de abrir un pull request, las
mismas comprobaciones que correrá el revisor. MUST terminar en 0 solo cuando el pull request se
puede abrir, y MUST decir cuál comprobación lo impide en cualquier otro caso.

La puerta MUST rechazar la ejecución cuando no hay nada que medir: con el árbol de trabajo sucio
—lo que no está en un commit no llega al pull request— o sin ningún commit por encima de la rama
base. MUST exigir un umbral de complejidad ciclomática, porque sin umbral el informe termina
siempre en 0. MUST ejecutar `coderabbit review --base <base> --gate major`, que termina en 2
cuando queda algún hallazgo de severidad `major` o peor.

Sin el CLI `coderabbit` instalado, la puerta MUST decir que se abre **sin** esa revisión, y con
`PRE_PR_STRICT=1` MUST tratar esa ausencia como fallo.

#### Scenario: El árbol tiene cambios sin commitear
- **WHEN** se ejecuta `./scripts/pre-pr.sh` con `git status --porcelain` no vacío
- **THEN** termina distinto de 0 y dice que lo que no está en un commit no llega al pull request

#### Scenario: No hay ningún commit sobre la base
- **WHEN** se ejecuta `./scripts/pre-pr.sh <base>` y no hay commits entre `<base>` y `HEAD`
- **THEN** termina distinto de 0 y dice que no hay pull request que medir

#### Scenario: CodeRabbit deja un hallazgo major
- **WHEN** `coderabbit review --base <base> --gate major` termina en 2
- **THEN** la puerta termina distinto de 0 y dice que ese hallazgo se arregla aquí, no en el pull request

### Requirement: Reglas de revisión del repositorio
El repositorio SHALL declarar en `.coderabbit.yaml` las reglas con las que el bot revisa sus
pull requests. El archivo MUST fijar el perfil de revisión, MUST revisar también los pull
requests en borrador, MUST excluir de la revisión las rutas de los cerebros y MUST llevar
instrucciones por ruta para el código, los contratos de rol de `prompts/` y la plantilla del
equipo de `.claude/agents/`.

Un hilo de revisión que repite algo que las reglas de la casa ya deciden MUST tratarse como una
instrucción que falta en ese archivo, no como una corrección del código.

#### Scenario: Un hilo repite una regla de la casa
- **WHEN** el bot abre un hilo sobre algo que `AGENTS.md` ya decide
- **THEN** la corrección es añadir esa instrucción a `.coderabbit.yaml`

### Requirement: Dos vueltas como máximo en un pull request
Un pull request SHALL cerrarse en como mucho dos vueltas de revisión automática. A partir de la
segunda, el contrato MUST tratar el problema como un defecto del corte del pull request o de
`.coderabbit.yaml`, y no como un hilo más que contestar.

#### Scenario: Tercera vuelta de hilos
- **WHEN** tras la segunda vuelta el bot sigue abriendo hilos
- **THEN** se para, se corrige el corte o las reglas y se deja la nota en el cerebro diario
