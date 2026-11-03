## ADDED Requirements

### Requirement: El cierre de sesión comprueba lo que el cambio dejó mintiendo

La lista de cierre de sesión (`docs/harness/clean-state-checklist.md`) SHALL incluir una comprobación de los documentos, specs y decisiones escritas que el trabajo de la sesión volvió falsos, aunque no aparezcan en el diff. Archivar un cambio, mover una ruta o renombrar un comando MUST disparar esa comprobación.

#### Scenario: Se archiva un cambio citado en la documentación

- **WHEN** una sesión archiva un cambio de OpenSpec que algún documento del repositorio cita por su ruta en `openspec/changes/`
- **THEN** la lista de cierre pide actualizar esa cita antes de dar la sesión por cerrada
