## ADDED Requirements

### Requirement: Un supuesto es una decisión, nunca un hecho

El prompt del intake (`prompts/intake.md`) SHALL exigir que todo dato comprobable en un archivo del repositorio se lea y se cite con su ruta, en lugar de estimarse. Solo SHALL llamarse supuesto a aquello que nadie ha decidido todavía.

La decisión del intake SHALL separar lo contado de lo supuesto: lo contado lleva la ruta de donde salió; lo supuesto se nombra como decisión pendiente, nunca como dato.

#### Scenario: Dato que vive en un archivo

- **WHEN** la petición depende de un número, un nombre de columna, una versión o una ruta que existe en el repositorio
- **THEN** el intake lo lee del archivo y lo cita con su ruta, en lugar de estimarlo

#### Scenario: Decisión que nadie ha tomado

- **WHEN** un dato necesario no está decidido en ninguna parte
- **THEN** el intake lo registra como supuesto explícito, con la decisión que haría falta, o pregunta con `NEEDS-INFO`
