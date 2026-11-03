## Why

Cuando se aprueba el PR de una API, el trabajo no termina: lo revisa una persona de QA que no ha leído el código y que necesita probar que el flujo hace lo que la historia de usuario dice. Hoy eso se resuelve a mano y dos veces — alguien rehace los requests en Postman o en la terminal, y alguien escribe desde cero el contexto que Cowork design necesita para redactar el plan de desarrollo (qué hace cada API, reglas de negocio, mensajes de error, tablas afectadas, qué se puede y qué no, concurrencia y seguridad).

Las dos cosas salen del mismo material: la HU, el diff aprobado y el código. El equipo ya tiene quien juzga el diseño de la frontera (`arquitecto-api`, #10) y quien audita la cobertura dentro del partido (`qa`, #2), pero nadie prepara la **entrega** a un humano de fuera.

## What Changes

- **Nuevo jugador `entrega-qa` (#7, extremo derecho)**, constructor con `model: sonnet` y un terreno acotado: solo escribe dentro de `entregas/<TICKET>/`.
- **Un paquete de entrega con forma fija**: `<TICKET>.md` (el briefing que lee Cowork design), `escenarios.py` (los requests, solo con la stdlib, ejecutables por el QA sin instalar nada) y `README.md` (cómo correrlo). El plan de desarrollo, `plan-desarrollo.md`, lo escribe Cowork en esa misma carpeta: el briefing y el plan son archivos distintos para que iterar el documento no destruya el prompt que lo genera.
- **Requisito nuevo en `team-match`**: qué contiene el paquete, qué no puede contener (secretos, endpoints inventados, afirmaciones sin `archivo:línea`) y cómo se verifica de forma determinista.

No cambia ningún comportamiento ejecutable de `src/factory/`.

## Impact

- Specs: `team-match` (un requisito añadido).
- Código: ninguno.
- Archivos: `.claude/agents/entrega-qa.md` (nuevo), `tests/test_team_entrega_qa.py` (nuevo), y las cuatro superficies de la plantilla: `README.md`, `docs/harness/equipo.md`, `.claude/skills/equipo/SKILL.md` y `docs/harness/roles.md`.
- Coste: una invocación de sonnet cuando el técnico lo convoque; su convocatoria (`entregas/**`) lo deja fuera de los partidos que no preparan una entrega.
