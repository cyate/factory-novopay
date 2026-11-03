## ADDED Requirements

### Requirement: Paquete de entrega al QA humano
Cuando el PR de una API se aprueba y la revisa una persona de QA, el equipo SHALL poder producir un paquete de entrega bajo `entregas/<TICKET>/`, escrito por el jugador `entrega-qa` (#7) y por nadie más. El paquete SHALL contener:
- `<TICKET>.md`: el briefing que lee Cowork design, con la historia de usuario, qué hace cada API, el contrato por endpoint, las reglas de negocio, los mensajes de error, las tablas afectadas, los límites del alcance, la concurrencia, la seguridad, las rutas del proyecto y las preguntas abiertas;
- `escenarios.py`: los requests por escenario, con la biblioteca estándar de Python y sin dependencias, con `--list`, `--only` y `--base-url`, salida legible con esperado frente a obtenido, y código de salida 0 o 1;
- `README.md`: cómo lo corre la persona de QA.

El plan de desarrollo (`plan-desarrollo.md`) lo escribe Cowork design en esa misma carpeta: el briefing y el plan MUST ser archivos distintos, para que reescribir el plan no destruya el prompt que lo genera.

El paquete MUST NOT contener secretos ni datos reales de personas o de tarjetas, ni endpoints, campos o códigos de error que no estén en el código o en la historia de usuario: lo que no se pueda anclar en `archivo:línea` va a "Preguntas abiertas". `entrega-qa` MUST NOT escribir fuera de `entregas/<TICKET>/`.

#### Scenario: Entrega preparada tras aprobarse el PR
- **WHEN** el técnico convoca a `entrega-qa` con un ticket, su historia de usuario y la rama aprobada
- **THEN** la carpeta `entregas/<TICKET>/` queda con el briefing, los escenarios y el README, y ningún archivo fuera de ella cambia

#### Scenario: Regla que no está en el código
- **WHEN** la historia de usuario menciona una regla que no aparece en el código de la rama
- **THEN** esa regla se registra en "Preguntas abiertas" del briefing y no se escribe como afirmación ni como escenario

#### Scenario: Verificación determinista del paquete
- **WHEN** el técnico ejecuta `python entregas/<TICKET>/escenarios.py --list`
- **THEN** se listan los escenarios con el criterio de la historia de usuario que prueba cada uno, sin lanzar ninguna petición
