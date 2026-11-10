# brain-retrieval Specification

## Purpose

Permite que personas y agentes consulten el cerebro principal y el diario. Cubre la búsqueda local y el acceso de lectura de maker y checker a las rutas de los cerebros. El contenido de los cerebros se trata siempre como dato y nunca como instrucciones.
## Requirements
### Requirement: Búsqueda en los cerebros
`factory brain search "<consulta>"` SHALL buscar por palabras clave en los catálogos del cerebro principal y del diario, sin servicios externos. Si el principal no está importado, MUST usar en su lugar el catálogo del mapa de la biblioteca. Cada resultado MUST incluir la ruta de la nota, su título, una cita (libro, capítulo y páginas, o fecha y origen para el diario) y sus tokens. `--brain`, `--limit` y `--json` acotan la búsqueda y la salida.

#### Scenario: Consulta con resultados
- **WHEN** se busca "rate limiting" con el cerebro principal importado
- **THEN** se listan las notas más relevantes con su ruta, título, cita del libro y capítulo con páginas, y tokens, ordenadas por relevancia

#### Scenario: Consulta sin resultados
- **WHEN** ninguna nota coincide con la consulta
- **THEN** el comando informa que no hay resultados, sugiere usar términos en inglés para el cerebro principal y termina con código cero

#### Scenario: Cerebro no configurado o vacío
- **WHEN** se busca sin haber importado el cerebro principal y sin mapa de la biblioteca
- **THEN** la búsqueda usa solo el cerebro diario e indica que el principal no está disponible y cómo importarlo

#### Scenario: Solo el mapa disponible
- **WHEN** se busca sin haber importado el cerebro principal, pero con el mapa de la biblioteca en el repo
- **THEN** los resultados del principal salen del mapa, con su cita, y la salida indica que el texto no está en este equipo y cómo importarlo

### Requirement: El bloque `knowledge` de un objetivo se acepta y se ignora
Un `goal.md` MAY llevar un bloque `knowledge` (`queries`, `enabled`); se valida y se acepta pero no tiene efecto: el orquestador no inyecta conocimiento en ningún prompt. El maker consulta los cerebros por sí mismo con las herramientas de lectura que recibe. Una clave ajena dentro de `knowledge` MUST ser un error del objetivo.

#### Scenario: Clave ajena en `knowledge`
- **WHEN** un objetivo declara `knowledge: {otro: 1}`
- **THEN** la carga del objetivo falla con un error que menciona `knowledge`

### Requirement: Acceso de lectura seguro a los cerebros
Las invocaciones de maker y checker SHALL recibir acceso de lectura a las rutas absolutas de ambos cerebros (`--add-dir`). Para cada una MUST añadirse una denegación obligatoria de edición y escritura que ninguna configuración ni objetivo puede quitar.

#### Scenario: Petición del maker con acceso a los cerebros
- **WHEN** se construye la invocación del maker con ambos cerebros configurados
- **THEN** los argumentos incluyen `--add-dir` con las rutas absolutas de ambos cerebros y las herramientas denegadas incluyen la edición y la escritura sobre ellas

### Requirement: Precedencia entre los cerebros y la documentación del harness

`docs/harness/cerebros.md` SHALL fijar qué fuente manda cuando dos se contradicen, en este orden: los documentos del propio repositorio que se revisan con el código (`AGENTS.md`, `docs/harness/`, las specs de `openspec/specs/`) mandan sobre los cerebros en todo lo que sea contrato, alcance o verificación de este repositorio; los cerebros mandan sobre la documentación general y sobre las skills externas en todo lo que sea experiencia de uso: trampas observadas, costes medidos y errores ya cometidos.

Quien encuentre una contradicción SHALL dejarla registrada —en `progress.md` o como nota del cerebro diario— en lugar de elegir una fuente en silencio.

#### Scenario: El cerebro contradice una spec del repositorio

- **WHEN** una nota del cerebro describe un comportamiento distinto del que fija una spec de `openspec/specs/`
- **THEN** manda la spec, y la contradicción queda registrada para corregir la nota

#### Scenario: El cerebro contradice a una skill externa

- **WHEN** una nota del cerebro registra una trampa observada que contradice lo que afirma una skill o un documento general
- **THEN** manda el cerebro, y la decisión se dice donde vive el trabajo, no solo en el chat

