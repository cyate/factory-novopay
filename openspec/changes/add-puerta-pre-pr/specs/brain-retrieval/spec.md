## ADDED Requirements

### Requirement: Consulta obligatoria a la biblioteca antes de proponer
Todo rol que proponga o implemente SHALL contrastar contra la biblioteca técnica un enfoque, un
arreglo o un hallazgo que no sea evidente desde el código, y MUST citarlo como
`Libro · cap. N · pp. A–B` junto a su recomendación, sin copiar el texto de la nota. Cuando no
encuentre nada aplicable, MUST decirlo.

La instrucción que recibe cada rol MUST caber en las herramientas que ese rol declara: un rol sin
`Bash` no puede ejecutar `factory brain search` y MUST recibir en su lugar la variante de lectura
sobre las rutas de los cerebros.

El `checker` queda **fuera** de este requisito: juzga solo con los criterios de aceptación, el
diff y la verificación determinista.

Cuando una nota contradiga `AGENTS.md`, `docs/harness/` o una spec de `openspec/specs/`, SHALL
mandar la documentación del repositorio, y la contradicción MUST quedar anotada.

#### Scenario: Enfoque sin precedente en la biblioteca
- **WHEN** un rol busca y no encuentra ninguna nota aplicable
- **THEN** lo dice en su informe, para que la siguiente sesión no repita la búsqueda

#### Scenario: Rol sin Bash
- **WHEN** el contrato de un rol manda ejecutar `factory brain search` y el rol no declara `Bash`
- **THEN** es un defecto del contrato: la orden acabaría en `permission_denials`
