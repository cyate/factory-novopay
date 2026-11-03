## Context

Las cinco reglas vienen de `/yate`, una skill de fábrica para servicios Go del mismo autor. Allí viven dentro de un flujo de cinco fases; aquí no hay fases: hay roles (`maker`, `checker`, `intake`), un equipo de sub-agentes y una lista de cierre de sesión. Traerlas no es copiar texto, es decidir en qué contrato de rol entra cada una.

El harness ya tiene dos árbitros con el mismo nombre y texto distinto: `prompts/checker.md`, que usa el motor de loops, y `.claude/agents/checker.md`, que se invoca desde una sesión interactiva y es el que exige `CLAUDE.md` antes de dar una feature por terminada. Hoy no comparten una sola línea. Cualquier regla sobre cómo revisa el checker tiene que entrar en los dos o no sirve.

El repositorio ya verifica contratos escritos en Markdown leyendo el archivo y afirmando sobre su contenido: `tests/test_team_revisores.py` comprueba así el formato de los revisores del equipo, y `tests/test_protected_config.py` las rutas protegidas. Ese es el patrón a seguir, y es la razón por la que estas reglas se pueden verificar sin tocar código de producción.

## Goals / Non-Goals

**Goals:**

- Que las cinco reglas queden en el contrato del rol al que le tocan, no en un documento aparte que nadie lee en el momento de decidir.
- Que cada regla tenga un test que falle si alguien la borra del prompt.
- Que el texto nuevo quepa en los prompts sin inflarlos: hoy miden 55, 46 y 44 líneas, y un prompt que nadie termina de leer no gobierna nada.

**Non-Goals:**

- No se cambia el esquema JSON del veredicto. Añadir un campo obligaría a tocar `src/factory/verdict.py` y sus tests, y la prueba de mutación cabe en `evidence`.
- No se tocan los revisores del equipo (`qa`, `revisor-pr`, `seguridad`, `producto`, `metricas`). Su reglamento ya declara al `checker` árbitro obligatorio, así que la regla les llega por ahí. Si después se quiere en cada jugador, es otro cambio.
- No se automatiza la detección de documentos que el cambio dejó mintiendo. Eso es la idea 3 de la lista (`factory lessons`) y es un cambio propio.
- No se toca `scripts/check.sh` ni la configuración de ruff o pytest.

## Decisions

**1. Una sola fuente para las dos copias del checker.** Las reglas se escriben en `prompts/checker.md` y se referencian desde `.claude/agents/checker.md`, que es el que ya tiene formato propio de salida. Alternativa descartada: un archivo común incluido por los dos. No existe mecanismo de inclusión en ninguno de los dos formatos, así que el "include" sería duplicación con otro nombre. El test comprueba que la regla está en ambos, que es lo que de verdad importa.

**2. La prueba de mutación se cita, no se ejecuta.** El checker es de solo lectura: no puede romper el arreglo y correr los tests. Lo que sí puede es exigir que el test exista y nombrarlo. Alternativa descartada: que el orquestador ejecute una mutación real; eso es `mutmut` o equivalente, una dependencia nueva y un cambio de las reglas de verificación.

**3. "Lo que el diff no muestra" entra como entrada de checklist, no como fase nueva.** El checker ya tiene un checklist de siete puntos; esta es la octava. Una fase aparte multiplicaría las rondas, y el hallazgo de esta semana (`docs/harness/panel.md` apuntando a un directorio archivado) lo habría cazado igual desde el checklist.

**4. `origin/main` se exige al maker, no al checker.** Es el maker quien decide construir; el checker juzga un diff que ya existe. Poner la regla en el checker llegaría una ronda tarde.

**5. La precedencia se escribe en `docs/harness/cerebros.md`, no en los prompts.** No es una instrucción de ejecución, es una regla de desempate que se consulta cuando aparece la contradicción. Los prompts solo la enlazan.

## Risks / Trade-offs

- **Prompts más largos → menos leídos.** → Cada regla entra en una o dos líneas dentro de una sección que ya existe, y se mide: ningún prompt debe pasar de 70 líneas tras el cambio.
- **Tests que comprueban texto se rompen al reescribir una frase.** → Los tests afirman sobre el concepto anclado a una palabra estable (`origin/main`, `mutación`, `supuesto`), no sobre la frase entera.
- **La regla de la mutación puede alargar las rondas**, porque un hallazgo cerrado sin test vuelve a abrirse. → Es el coste buscado: hoy un arreglo sin prueba pasa y se rompe en la siguiente sesión. Si resulta excesivo, se baja a `minor` y queda la evidencia igual.
- **Duplicación entre las dos copias del checker.** → El test que exige la regla en ambos archivos es lo que impide que se separen en silencio.

## Open Questions

- ¿La prueba de mutación aplica también a los `minor` corregidos, o solo a `critical` y `medium`? La propuesta dice `critical` y `medium`; si en la práctica los `minor` también se cierran sin test, se amplía.
- ¿`factory doctor` debería comprobar estas reglas, además de los tests? Hoy doctor audita estructura del harness, no contenido de los prompts. Queda fuera de este cambio.
