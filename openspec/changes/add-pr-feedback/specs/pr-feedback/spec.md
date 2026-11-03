## ADDED Requirements

### Requirement: Recomendaciones de los revisores de un pull request
El comando `factory feedback` SHALL reunir, mediante el CLI `gh` sobre el pull request indicado, los hilos de revisión en línea y los cuerpos de las revisiones. Cada hilo MUST llevar el login de quien lo abrió, su `archivo:línea`, el comentario, su URL, si está resuelto u obsoleto, quién respondió y el identificador con el que se le puede contestar. El pull request MUST poder indicarse por número o por URL, y con número suelto el repositorio MUST deducirse del directorio actual salvo que se dé `--repo`.

El comando MUST ser de solo lectura: no escribe en GitHub ni en el repositorio.

#### Scenario: Hilos sin resolver de un pull request
- **WHEN** se pide `factory feedback` de un pull request con hilos sin resolver
- **THEN** el informe los trae agrupados por revisor, cada uno con su `archivo:línea` y el comando `gh` para responderlo

#### Scenario: Pull request indicado por URL
- **WHEN** el argumento es la URL de un pull request de otro repositorio
- **THEN** el repositorio y el número salen de la URL, sin consultar el directorio actual

#### Scenario: Hilo ya respondido
- **WHEN** un hilo tiene respuestas además del comentario inicial
- **THEN** el informe nombra a quien respondió, y el hilo sigue apareciendo mientras no esté resuelto

### Requirement: Filtro por revisor y hilos resueltos
El comando SHALL aceptar uno o varios `--revisor` y quedarse con los hilos en los que esa persona participa, comparando por subcadena del login. Los hilos resueltos MUST quedar fuera por defecto y contarse aparte, y `--resueltos` MUST incluirlos.

#### Scenario: Un trozo del login basta
- **WHEN** se pasa `--revisor sam` y el revisor es `sam-pc-novo`
- **THEN** sus hilos entran en el informe

#### Scenario: Recomendación dentro de un hilo ajeno
- **WHEN** `sam-pc-novo` responde en un hilo que abrió otro revisor
- **THEN** ese hilo entra con `--revisor sam`

#### Scenario: Resueltos ocultos
- **WHEN** el pull request tiene hilos resueltos y no se pasa `--resueltos`
- **THEN** no aparecen en el informe y su número figura en `ocultos`

### Requirement: Degradación sin GitHub
Cuando falte el CLI `gh`, no haya sesión iniciada, no haya red, el directorio de trabajo no exista o el pull request no exista, el comando SHALL terminar con código 2 y el motivo en `stderr`, sin escribir nada.

#### Scenario: Sin sesión de gh
- **WHEN** `gh` responde con error de autenticación
- **THEN** el comando termina en 2 y `stderr` nombra el fallo de `gh`

#### Scenario: Pull request inexistente
- **WHEN** el repositorio no tiene ese número de pull request
- **THEN** el comando termina en 2 diciendo qué repositorio y qué número buscó
