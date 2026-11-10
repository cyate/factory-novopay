# Tasks

> No se tocan `scripts/check.sh` ni la configuración de ruff o pytest. La puerta es un script
> aparte: no entra en la ruta de verificación del repositorio.

## 1. La puerta (`pre-pr-gate`)

- [x] 1.1 `scripts/pre-pr.sh`: base válida, árbol limpio, commits sobre la base, `check.sh`,
      tamaño del PR, `factory complexity --base --max` y `coderabbit review --gate major`.
- [x] 1.2 Salto documentado sin el CLI instalado y `PRE_PR_STRICT=1` para convertirlo en fallo.
- [x] 1.3 `.coderabbit.yaml`: perfil `chill`, `auto_review.drafts`, cerebros excluidos e
      instrucciones por ruta para `**/*.py`, `prompts/**/*.md` y `.claude/agents/**/*.md`.
- [x] 1.4 `AGENTS.md` (comando y definición de terminado) y `CLAUDE.md` (puerta y dos vueltas).
- [x] 1.5 `docs/harness/recomendaciones.md`: la puerta, por qué antes y no después, con las citas.

## 2. La consulta a la biblioteca (`brain-retrieval`)

- [x] 2.1 `prompts/maker.md` y `prompts/intake.md`, con sus plantillas de `src/factory/templates/`.
- [x] 2.2 Los agentes de `.claude/agents/`, con la variante que cabe en sus herramientas.
- [x] 2.3 `prompts/checker.md` y `.claude/agents/checker.md`: "lo que abriría un hilo en el PR".
- [x] 2.4 `AGENTS.md` (restricción dura) y `docs/harness/cerebros.md` (consulta obligatoria).
- [x] 2.5 `docs/harness/roles.md` y `revision.md`: las reglas de oficio dejan de ser cinco.

## 3. Verificación

- [x] 3.1 `tests/test_reglas_de_oficio.py` y `tests/test_pre_pr.py`: existencia y contenido de la
      puerta, su comportamiento con CodeRabbit (0, 2, 1, ausente, `PRE_PR_STRICT`), claves de
      `.coderabbit.yaml` y encaje entre la orden de búsqueda y las herramientas del rol. Los tests
      de frases en Markdown se retiraron por decisión del usuario.
- [x] 3.2 `./scripts/check.sh` en 0.
