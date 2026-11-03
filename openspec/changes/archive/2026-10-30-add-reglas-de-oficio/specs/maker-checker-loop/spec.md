## ADDED Requirements

### Requirement: Un hallazgo corregido se cierra con una prueba de mutación

El prompt del checker (`prompts/checker.md`) y el subagente `checker` (`.claude/agents/checker.md`) SHALL exigir que todo hallazgo `critical` o `medium` que se declare corregido quede defendido por una prueba que falla si el arreglo se revierte. Mientras esa prueba no exista, el hallazgo MUST seguir contándose como abierto, aunque el código ya no tenga el defecto.

El checker SHALL nombrar en su veredicto, dentro del campo `evidence`, el test concreto que defiende cada hallazgo que da por cerrado. El esquema JSON del veredicto no cambia: la prueba se cita en los campos existentes.

#### Scenario: Arreglo sin prueba que lo defienda

- **WHEN** una ronda corrige un hallazgo `medium` y no añade ni modifica ningún test que falle al revertir el arreglo
- **THEN** el checker mantiene el hallazgo abierto y su veredicto es `fail`, con una `suggestion` que pide la prueba

#### Scenario: Arreglo con su prueba

- **WHEN** una ronda corrige un hallazgo y añade un test que falla si se revierte el arreglo
- **THEN** el checker puede darlo por cerrado y cita en `evidence` el archivo y el nombre de ese test

### Requirement: La revisión cubre lo que el diff no muestra

El prompt del checker y el subagente `checker` SHALL incluir, dentro de su checklist, una comprobación explícita de lo que el diff no enseña: documentación, specs, decisiones escritas o rutas citadas que el cambio volvió falsas, y caminos de código que quedaron inalcanzables.

Un archivo que el cambio dejó mintiendo SHALL tratarse como hallazgo, con la misma escala de gravedad que el resto, aunque ese archivo no aparezca en el diff.

#### Scenario: Documento que el cambio dejó mintiendo

- **WHEN** un cambio mueve o elimina una ruta que un documento del repositorio cita como existente, y ese documento no está en el diff
- **THEN** el checker lo reporta como hallazgo, con la ubicación del documento y la ruta que ya no existe

#### Scenario: Nada quedó desactualizado

- **WHEN** el diff no invalida ninguna documentación, spec ni decisión escrita
- **THEN** el checker lo dice explícitamente en su `summary`, porque esa superficie se miró

### Requirement: Comprobar contra `origin/main` antes de afirmar que algo no existe

El prompt del maker (`prompts/maker.md`) SHALL exigir que toda afirmación sobre la ausencia de código, de un módulo, de una migración o de un documento se compruebe contra `origin/main`, y no contra el árbol de trabajo. El maker MUST citar el comando con el que lo comprobó.

Cuando el worktree no tenga acceso al remoto, el maker SHALL decirlo y tratar su afirmación como supuesto, no como hecho.

#### Scenario: Afirmación sobre algo que no existe

- **WHEN** el maker va a construir algo porque concluye que no está construido
- **THEN** antes lo comprueba contra `origin/main` y deja constancia del comando y su resultado

#### Scenario: Sin acceso al remoto

- **WHEN** el worktree no puede consultar `origin/main`
- **THEN** el maker registra la limitación y marca la afirmación como supuesto
