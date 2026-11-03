# observability-panel Specification

## Purpose
TBD - created by archiving change add-panel. Update Purpose after archive.
## Requirements
### Requirement: Instantánea del estado
`factory panel --json` SHALL imprimir en stdout una instantánea JSON con las secciones `tokens`, `reviews`, `tasks` y `pulls`, y terminar con código 0. El servidor MUST devolver la misma instantánea en `GET /api/snapshot`. Un archivo de estado ausente MUST dejar su parte de la sección vacía sin aviso, porque un repo sin ejecuciones ni hooks es normal. Uno ilegible MUST dejarla vacía con un aviso en `warnings` que nombre el archivo.

La sección `pulls` MUST quedar vacía, con el motivo en su campo `error`, cuando `gh` no esté instalado, no haya sesión iniciada, no haya red o se pida `factory panel --no-pulls`; ese caso MUST NOT impedir que el resto de la instantánea se genere ni cambiar el código de salida.

#### Scenario: Repo sin ejecuciones
- **WHEN** se ejecuta `factory panel --json` en un repo sin `.factory/`
- **THEN** termina con código 0 y la instantánea tiene las cuatro secciones, con listas vacías donde no hay datos
- **AND** `warnings` está vacío

#### Scenario: Lista de features corrupta
- **WHEN** `feature_list.json` no es JSON válido
- **THEN** la instantánea sigue generándose y `warnings` nombra el archivo

#### Scenario: Sin gh instalado
- **WHEN** se ejecuta `factory panel --json` en una máquina sin el CLI `gh`
- **THEN** termina con código 0, `pulls.pulls` está vacío y `pulls.error` dice que no se encontró `gh`

### Requirement: Servidor local
`factory panel` SHALL servir la página y la API en `127.0.0.1` (puerto configurable con `--port`, 8765 por defecto) hasta que se interrumpa. MUST rechazar con 403 las peticiones cuya cabecera `Host` no sea `127.0.0.1`, `localhost` o `[::1]` y responder 405 a cualquier método distinto de `GET` o `HEAD`.

#### Scenario: Página principal
- **WHEN** se pide `GET /` con `Host: 127.0.0.1:8765`
- **THEN** responde 200 con la página HTML del panel

#### Scenario: Host ajeno
- **WHEN** se pide `GET /api/snapshot` con `Host: atacante.example`
- **THEN** responde 403 sin datos

#### Scenario: Escritura
- **WHEN** se envía `POST /api/snapshot`
- **THEN** responde 405

### Requirement: Actualización en vivo
`GET /api/stream` SHALL mantener una conexión de *server-sent events* y enviar un evento `change` con las secciones afectadas cuando cambie algún archivo vigilado: `feature_list.json`, los `tasks.md` de los cambios activos, el estado y los eventos de `.factory/` y las transcripciones del proyecto. La página MUST refrescar la instantánea al recibirlo.

Mientras el servidor corre, un sondeador SHALL consultar los pull requests cada 60 segundos y enviar un evento `change` con la sección `pulls` **solo cuando el resultado cambie**, para que un sondeo sin novedad no repinte la página.

#### Scenario: Revisión que termina
- **WHEN** se añade una línea a `.factory/hooks/events.jsonl` con el panel abierto
- **THEN** el stream envía un evento `change` que incluye `reviews`

#### Scenario: Feature promovida
- **WHEN** `factory features verify` cambia `feature_list.json`
- **THEN** el stream envía un evento `change` que incluye `tasks`

#### Scenario: Sondeo sin novedad
- **WHEN** dos sondeos seguidos de pull requests devuelven lo mismo
- **THEN** el stream no envía ningún evento `change` por el segundo

### Requirement: Estado de implementación
La sección `tasks` SHALL incluir cada feature con su estado, prioridad, comandos de verificación y última evidencia, y cada cambio OpenSpec activo con sus tareas hechas y totales por grupo. Un grupo cuyo título nombre un id de feature entre comillas invertidas MUST enlazarse con esa feature.

#### Scenario: Grupo enlazado
- **WHEN** `tasks.md` tiene el grupo "## 2. Plantilla y convocatoria (`team-roster`)" con 1 de 4 tareas marcadas y existe la feature `team-roster`
- **THEN** la feature `team-roster` muestra 1/4 tareas de ese grupo

### Requirement: Ejecuciones y bandeja
La sección `tasks` SHALL incluir las ejecuciones de factory con su estado, ronda actual, criterios superados, último veredicto, coste acumulado y si su proceso sigue vivo, además del número de entradas pendientes de la bandeja.

#### Scenario: Ejecución huérfana
- **WHEN** una ejecución figura como `running` pero su `pid` ya no existe
- **THEN** la instantánea la marca como no viva

### Requirement: Página gráfica
La página SHALL funcionar sin red: HTML, CSS, JS y gráficos en línea, sin recursos externos. Debe mostrar el consumo de tokens con gráficos, el feed de revisiones, el estado de implementación con una vista de detalle por feature y una pestaña de pull requests, y adaptarse a tema claro u oscuro y a pantallas estrechas.

La pestaña de pull requests MUST mostrar, por cada uno, su estado, el rol del usuario, el tamaño, el resultado de los checks, sus tiempos y una etiqueta legible por cada alerta, y MUST permitir filtrar entre todos, los propios, los que el usuario tiene que revisar y los que tienen alguna alerta. El enlace a cada pull request se construye con el dato recibido en tiempo de ejecución, así que la página sigue sin incorporar ninguna URL externa.

#### Scenario: Sin recursos externos
- **WHEN** se inspecciona la página servida
- **THEN** no contiene ninguna URL `http://` ni `https://` a otro origen

#### Scenario: Vocabulario completo en la pestaña
- **WHEN** la sección `pulls` trae un pull request con cualquiera de los estados o de las alertas definidos
- **THEN** la página tiene una etiqueta legible para cada uno, sin mostrar el código interno

### Requirement: Panel de solo lectura
El panel SHALL limitarse a leer: ni el servidor ni `factory panel --json` crean, modifican o borran archivos del repo, de `.factory/` o de las transcripciones. La sección `pulls` MUST obtener sus datos con consultas de solo lectura de `gh` y guardarlas en memoria, sin escribir caché en disco, y MUST NOT ejecutar ninguna operación de escritura sobre GitHub: ni crear, ni comentar, ni revisar, ni fusionar un pull request.

#### Scenario: Instantánea sin efectos
- **WHEN** se pide `/api/snapshot` sobre un repo con ejecuciones, hooks y transcripciones
- **THEN** las fechas de modificación y los contenidos de todos esos archivos quedan iguales

#### Scenario: Sondeo sin escritura
- **WHEN** el sondeador de pull requests termina una vuelta
- **THEN** no ha creado ningún archivo nuevo en el repo ni en `.factory/`

### Requirement: Pull requests del repositorio
La sección `pulls` de la instantánea SHALL reunir, mediante el CLI `gh` sobre el repositorio del panel, los pull requests abiertos creados por el usuario autenticado, los abiertos en los que se le ha pedido revisión y sus últimos pull requests fusionados. Cada entrada MUST llevar su número, título, URL, rama, rol del usuario (`autor` o `revisor`), estado de revisión, resultado de los checks, tamaño en archivos y líneas, y los tiempos en horas: abierto, sin actividad, hasta la primera revisión **humana** y de ciclo hasta la fusión. Un pull request que aparezca en más de una consulta MUST figurar una sola vez, con el rol `autor` si el usuario lo creó.

Los datos MUST vivir solo en memoria del proceso del panel: la sección no escribe ningún archivo.

#### Scenario: PR propio esperando revisión
- **WHEN** el usuario tiene un pull request abierto que creó hace tres horas y nadie ha revisado
- **THEN** la sección `pulls` lo incluye con rol `autor`, estado `sin_revisar` y tres horas abierto

#### Scenario: PR que aparece en dos consultas
- **WHEN** un pull request lo creó el usuario y además se le pidió revisión en él
- **THEN** figura una sola vez en la sección, con rol `autor`

#### Scenario: Tiempo hasta la primera revisión
- **WHEN** un pull request creado a las 09:00 recibe su primera revisión a las 11:30
- **THEN** su tiempo hasta la primera revisión es de 2,5 horas

#### Scenario: Revisión de un bot
- **WHEN** un escáner automático revisa el pull request treinta segundos después de abrirse y una persona lo revisa dos horas y media más tarde
- **THEN** el tiempo hasta la primera revisión es de 2,5 horas, y el bot no cuenta como revisor humano

### Requirement: Alertas de pull request
Cada pull request de la sección `pulls` SHALL llevar la lista de alertas que le aplican, vacía si no hay ninguna: `checks_fallando`, `cambios_pedidos`, `conflictos`, `sin_revisor`, `sin_coderabbit`, `sin_cifra`, `parado` (más de 24 horas sin actividad) y `demasiado_grande` (más de 10 archivos o más de 600 líneas, según el límite de tamaño de pull request del repositorio).

Las alertas `sin_coderabbit`, `sin_cifra` y `demasiado_grande` MUST aplicarse solo a los pull requests cuyo rol es `autor`, porque son reglas que el autor puede cumplir.

#### Scenario: PR sin el comentario de CodeRabbit
- **WHEN** un pull request propio no tiene ningún comentario cuyo cuerpo sea `@coderabbitai review`
- **THEN** sus alertas incluyen `sin_coderabbit`

#### Scenario: PR pasado de tamaño
- **WHEN** un pull request propio cambia 14 archivos
- **THEN** sus alertas incluyen `demasiado_grande`

#### Scenario: PR ajeno sin reglas de autor
- **WHEN** el usuario solo es revisor de un pull request grande y sin el comentario de CodeRabbit
- **THEN** sus alertas no incluyen `demasiado_grande` ni `sin_coderabbit`

