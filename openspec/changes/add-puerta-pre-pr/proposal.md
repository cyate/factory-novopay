## Why

Los nueve pull requests de SPD-80 abiertos el 30 de octubre de 2026 en
`cifra-spend-corporate-api-go` acumularon 23 hilos de CodeRabbit, 16 de ellos todavía sin
contestar cuando la rama ya había avanzado a otro ticket. Ninguno necesitaba al bot para
encontrarse: tres eran el mismo defecto —un efecto externo irreversible ejecutado antes de la
comprobación de autorización— visto desde tres sitios, y nueve no eran código sino notas y
contrato que el propio PR dejó falsos.

Dos huecos del harness lo explican. El primero: el CLI de CodeRabbit está instalado y
autenticado en la máquina donde se construye, y nada lo llamaba; la fábrica solo lo conocía
*después* de abrir el PR, por `factory feedback` y el panel. El segundo: la biblioteca técnica
—82 libros, 11.245 notas— no estaba importada en el repositorio, así que la inyección de
conocimiento entregaba citas sin texto, y ningún contrato de rol obligaba a mirarla antes de
decidir el enfoque.

Una corrección que llega desde fuera del lazo hace oscilar al sistema en vez de asentarlo
(*The Software Architect Elevator* · cap. 10 · pp. 100–101). La forma de no tener que arreglar
un defecto es no introducirlo (*Defending APIs* · cap. 8 · p. 212), y una revisión se empieza en
local, con el diff contra la rama base, no en el editor web del pull request
(*Web Application Security* · cap. 25 · pp. 326–327).

## What Changes

- **`scripts/pre-pr.sh`**: puerta previa a abrir un pull request. Comprueba que el árbol esté
  limpio y que haya commits sobre la base, corre `./scripts/check.sh`, mide el tamaño del PR,
  exige un umbral de complejidad ciclomática y termina con `coderabbit review --base <base>
  --gate major`. Termina distinto de 0 cuando el PR no debería abrirse.
- **`.coderabbit.yaml`**: las reglas de la casa con las que el bot revisa este repositorio
  —perfil `chill`, revisión de borradores, cerebros excluidos e instrucciones por ruta—, para
  que no vuelva a abrir hilos que `AGENTS.md` ya decide.
- **Consulta obligatoria a la biblioteca**: el maker, `ingeniero-software` y `seguridad`
  contrastan su propuesta contra el cerebro principal y la citan (`Libro · cap. N · pp. A–B`).
  El `checker` queda fuera a propósito: juzga con los criterios, el diff y la verificación.
- **Dos vueltas como máximo** en un pull request: a partir de ahí el defecto está en el corte
  del PR o en una instrucción que falta en `.coderabbit.yaml`, no en el hilo.

## Impact

- Specs: `pre-pr-gate` (capacidad nueva) y `brain-retrieval` (un requisito nuevo).
- Código: ninguno. `scripts/pre-pr.sh` y `.coderabbit.yaml` son archivos nuevos del harness.
- Contratos de rol: `prompts/maker.md`, `prompts/checker.md`, sus dos plantillas de `src/factory/templates/prompts/` y los agentes de `.claude/agents/`.
- Tests: `tests/test_reglas_de_oficio.py`.
- Documentación: `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/harness/cerebros.md`,
  `docs/harness/recomendaciones.md`, `docs/harness/roles.md` y `docs/harness/revision.md`.
- Red: la puerta ejecuta una revisión de CodeRabbit por invocación, con la sesión del usuario.
  Sin el CLI instalado, o si la revisión no llega a completarse, el paso avisa y sigue, y `PRE_PR_STRICT=1` lo convierte en fallo.
