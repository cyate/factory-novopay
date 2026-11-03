# Tasks

> Todo el cambio es una sola feature de `feature_list.json`, con WIP=1:
> 1. `factory features start reglas-de-oficio`;
> 2. los grupos 2 a 4;
> 3. `factory features verify reglas-de-oficio`.
>
> Los tests leen los archivos del repositorio y afirman sobre su contenido, como `tests/test_team_revisores.py`. No se toca el código de `src/factory/`, ni `scripts/check.sh`, ni la configuración de ruff o pytest. Los prompts sí viajan duplicados en `src/factory/templates/prompts/`: cualquier cambio en `prompts/` obliga a sincronizarlos (tarea 3.4).

## 1. Preparación

- [x] 1.1 Añadir a `feature_list.json` la feature `reglas-de-oficio` (prioridad 27), en `not_started`, con `evidence: []` y su comando de verificación (`python -m pytest -q tests/test_reglas_de_oficio.py`). No editar a mano `status` ni `evidence`.
- [x] 1.2 Crear `tests/test_reglas_de_oficio.py` con el esqueleto y las rutas de los archivos gobernados (`prompts/checker.md`, `prompts/maker.md`, `prompts/intake.md`, `.claude/agents/checker.md`, `docs/harness/cerebros.md`, `docs/harness/clean-state-checklist.md`). Verificar que falla antes de escribir las reglas.

## 2. El árbitro: mutación y lo que el diff no muestra

- [x] 2.1 Añadir a `prompts/checker.md` la regla de la prueba de mutación: un hallazgo `critical` o `medium` dado por corregido necesita un test que falle al revertir el arreglo, y el checker cita ese test en `evidence`. Sin él, el hallazgo sigue abierto.
- [x] 2.2 Añadir al checklist de `prompts/checker.md` la entrada de lo que el diff no muestra: documentación, specs, decisiones escritas o rutas citadas que el cambio volvió falsas, y caminos que quedaron inalcanzables. Un archivo que miente es un hallazgo aunque no esté en el diff; si no hay ninguno, se dice en el `summary`.
- [x] 2.3 Llevar las dos reglas a `.claude/agents/checker.md`, respetando su formato de salida propio (`## Veredicto`, `## Hallazgos`, `## Verificación recibida`).
- [x] 2.4 Tests en `tests/test_reglas_de_oficio.py`: las dos reglas están en los dos archivos del checker, ancladas a palabras estables (`mutación`, `revertir`, `no muestra`). Verificar con `python -m pytest -q tests/test_reglas_de_oficio.py`.

## 3. El maker y el intake

- [x] 3.1 Añadir a `prompts/maker.md` la regla de `origin/main`: toda afirmación sobre lo que no existe se comprueba contra el remoto y se cita el comando; sin acceso al remoto, la afirmación es un supuesto y se dice.
- [x] 3.2 Añadir a `prompts/intake.md` la regla del supuesto: lo que se puede leer en un archivo se lee y se cita con su ruta; solo es supuesto lo que nadie ha decidido, y se nombra como decisión pendiente.
- [x] 3.4 Sincronizar `src/factory/templates/prompts/{maker,checker,intake}.md` con las copias de `prompts/`. `tests/test_templates.py::test_prompts_empaquetados_iguales_a_los_del_repo` exige igualdad byte a byte y es la prueba que falla si alguien revierte una de las dos copias.
- [x] 3.3 Tests: las dos reglas están en sus prompts, y ningún prompt pasa de 70 líneas (`prompts/*.md`). Verificar con `python -m pytest -q tests/test_reglas_de_oficio.py`.

## 4. Documentación y precedencia

- [x] 4.1 Escribir en `docs/harness/cerebros.md` la regla de precedencia: los documentos del repositorio revisados con el código mandan sobre los cerebros en contrato, alcance y verificación; los cerebros mandan sobre la documentación general y las skills externas en experiencia de uso. Toda contradicción se registra en `progress.md` o como nota del cerebro diario.
- [x] 4.2 Añadir a `docs/harness/clean-state-checklist.md` la comprobación de lo que el trabajo dejó mintiendo, con el archivado de un cambio de OpenSpec como caso que la dispara.
- [x] 4.3 Recoger las cinco reglas en `docs/harness/revision.md` y `docs/harness/roles.md`, enlazando a los prompts en lugar de repetir el texto.
- [x] 4.4 Tests: la precedencia está en `docs/harness/cerebros.md` y la entrada nueva en la lista de cierre. Verificar con `python -m pytest -q tests/test_reglas_de_oficio.py`.

## 5. Integración

- [x] 5.1 Ejecutar `./scripts/check.sh` (código 0) y `openspec validate add-reglas-de-oficio --strict` (válido). Ejecutar `factory features verify reglas-de-oficio` hasta `passing`.
- [x] 5.2 Pasar el `checker` sobre el diff completo del cambio, que es además la primera prueba real de las reglas nuevas: debe aplicarse a sí mismo la mutación y el checklist de lo que el diff no muestra. Registrar en `progress.md` si se aplicó las reglas o las ignoró — eso dice si el texto gobierna de verdad.
- [x] 5.3 Archivar con `/opsx:archive add-reglas-de-oficio` y sincronizar las specs.

## Workflow follow-up

- Corregir los hallazgos `critical` y `medium` del `checker` y volver a pedir revisión hasta que no quede ninguno abierto.
- Decidir las preguntas abiertas de `design.md`: si la prueba de mutación alcanza a los `minor`, y si `factory doctor` debería auditar estas reglas.
