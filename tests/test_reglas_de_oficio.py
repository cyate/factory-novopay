"""Las reglas de oficio y la puerta previa al PR viven en el contrato de cada rol
(`add-reglas-de-oficio`, `add-puerta-pre-pr`)."""

import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

CHECKER_LOOP = REPO / "prompts" / "checker.md"
CHECKER_AGENTE = REPO / ".claude" / "agents" / "checker.md"
MAKER = REPO / "prompts" / "maker.md"
INTAKE = REPO / "prompts" / "intake.md"
CEREBROS = REPO / "docs" / "harness" / "cerebros.md"
CIERRE = REPO / "docs" / "harness" / "clean-state-checklist.md"
AGENTES_DIR = REPO / ".claude" / "agents"
CLAUDE_MD = REPO / "CLAUDE.md"
PUERTA = REPO / "scripts" / "pre-pr.sh"
CODERABBIT = REPO / ".coderabbit.yaml"
ROLES = REPO / "docs" / "harness" / "roles.md"
REC = REPO / "docs" / "harness" / "recomendaciones.md"
PLANTILLAS = REPO / "src" / "factory" / "templates" / "prompts"

# Todos los roles del equipo consultan a los expertos antes de proponer, menos el checker:
# juzga solo con los criterios, el diff y la verificación (docs/harness/cerebros.md).
QUIEN_CONSULTA = sorted(set(AGENTES_DIR.glob("*.md")) - {CHECKER_AGENTE})
QUIEN_CONSULTA += [MAKER, INTAKE]

LOS_DOS_CHECKERS = (CHECKER_LOOP, CHECKER_AGENTE)
# Cada prompt gobierna solo si se lee entero; un prompt que crece deja de leerse.
MAX_LINEAS_PROMPT = 70


def _texto(path: Path) -> str:
    assert path.is_file(), f"falta {path.relative_to(REPO)}"
    return path.read_text(encoding="utf-8").lower()


def _contiene(path: Path, *fragmentos: str) -> None:
    """Cada fragmento debe aparecer; se anclan palabras estables, no frases enteras."""
    texto = _texto(path)
    faltan = [f for f in fragmentos if f.lower() not in texto]
    assert not faltan, f"{path.relative_to(REPO)}: no menciona {faltan}"


# El campo donde cada checker cita el test que defiende el arreglo.
CAMPO_EVIDENCIA = {CHECKER_LOOP: "`evidence`", CHECKER_AGENTE: "`evidencia`"}


@pytest.mark.parametrize("path", LOS_DOS_CHECKERS, ids=lambda p: p.name)
def test_mutacion_cierra_el_hallazgo(path: Path) -> None:
    """Un arreglo sin prueba que falle al revertirlo es una opinión con commit."""
    _contiene(path, "mutación", "revertir", "sigue abierto", CAMPO_EVIDENCIA[path])


@pytest.mark.parametrize("path", LOS_DOS_CHECKERS, ids=lambda p: p.name)
def test_revision_de_lo_que_el_diff_no_muestra(path: Path) -> None:
    """Un archivo que el cambio dejó mintiendo es un hallazgo aunque no esté en el diff."""
    _contiene(path, "no muestra", "aunque no aparezca en el diff")


def test_maker_comprueba_contra_origin_main() -> None:
    """Un 'esto no existe' dicho desde un checkout viejo manda a construir lo ya construido."""
    _contiene(MAKER, "origin/main", "self_check")


def test_intake_separa_lo_contado_de_lo_supuesto() -> None:
    """La regla la lleva la cláusula, no la palabra: 'por supuesto' aparece por casualidad."""
    _contiene(INTAKE, "nunca un hecho", "se cita con su ruta")


def test_precedencia_entre_cerebros_y_documentacion() -> None:
    """La precedencia tiene dirección y deja rastro; sin eso, el texto podría decir lo contrario."""
    _contiene(CEREBROS, "precedencia", "mandan los documentos", "progress.md")


def test_cierre_comprueba_lo_que_quedo_mintiendo() -> None:
    _contiene(CIERRE, "mintiendo")


@pytest.mark.parametrize("path", sorted((REPO / "prompts").glob("*.md")), ids=lambda p: p.name)
def test_los_prompts_siguen_siendo_cortos(path: Path) -> None:
    lineas = len(path.read_text(encoding="utf-8").splitlines())
    assert lineas <= MAX_LINEAS_PROMPT, f"{path.name}: {lineas} líneas"


@pytest.mark.parametrize("path", QUIEN_CONSULTA, ids=lambda p: p.name)
def test_consulta_a_los_expertos_antes_de_proponer(path: Path) -> None:
    """Elegir enfoque sin mirar la biblioteca repite un error ya escrito en un libro."""
    _contiene(path, "expertos", "cap.", "pp.")


@pytest.mark.parametrize("path", LOS_DOS_CHECKERS, ids=lambda p: p.name)
def test_el_checker_no_recibe_conocimiento(path: Path) -> None:
    """La regla del checker es juzgar el diff; una cita de libro le daría de qué opinar."""
    assert "expertos" not in _texto(path)


@pytest.mark.parametrize("path", LOS_DOS_CHECKERS, ids=lambda p: p.name)
def test_lo_que_abriria_un_hilo_en_el_pr(path: Path) -> None:
    """Lo que el revisor externo abriría como hilo se decide aquí, una vuelta antes."""
    _contiene(path, "abriría un hilo en el pr", "`medium`")


def test_la_puerta_previa_al_pull_request_existe_y_se_exige() -> None:
    """Una puerta que no se ejecuta no es una puerta: el contrato la nombra y el script corre."""
    ejecutable = PUERTA.is_file() and os.access(PUERTA, os.X_OK)
    assert ejecutable, "scripts/pre-pr.sh falta o no es ejecutable"
    assert CODERABBIT.is_file(), (
        "falta .coderabbit.yaml: el bot revisaría con sus valores por defecto"
    )
    _contiene(
        PUERTA,
        "--gate major",  # sin esto CodeRabbit informa pero no cierra
        "./scripts/check.sh",
        "--max",  # sin umbral el informe de complejidad termina siempre en 0
        "PRE_PR_MAX_COMPLEJIDAD",
        "git status --porcelain",  # con el árbol sucio no hay nada que medir
        "rev-list --count",  # ni sin commits sobre la base
        "PRE_PR_STRICT",
    )
    _contiene(CLAUDE_MD, "pre-pr.sh", "dos vueltas como máximo", ".coderabbit.yaml")


@pytest.mark.parametrize("nombre", ["maker.md", "checker.md", "intake.md"], ids=lambda n: n)
def test_las_plantillas_repiten_el_prompt_vigente(nombre: str) -> None:
    """Un repo nuevo nace con estos prompts; si se quedan atrás, nace sin las reglas."""
    vigente = (REPO / "prompts" / nombre).read_text(encoding="utf-8")
    plantilla = (PLANTILLAS / nombre).read_text(encoding="utf-8")
    assert vigente == plantilla, (
        f"src/factory/templates/prompts/{nombre} no coincide con prompts/{nombre}"
    )


def test_el_archivo_del_bot_lleva_las_reglas_de_la_casa() -> None:
    """Vaciarlo devuelve al bot a sus valores por defecto: justo lo que dice resolver."""
    import yaml

    cfg = yaml.safe_load(CODERABBIT.read_text(encoding="utf-8"))
    revisiones = cfg["reviews"]
    assert revisiones["profile"] == "chill"
    assert revisiones["auto_review"]["drafts"] is True
    excluidos = set(revisiones["path_filters"])
    assert {"!brain-principal/**", "!brain-mapa/**", "!brain-diario/**"} <= excluidos
    rutas = {i["path"] for i in revisiones["path_instructions"]}
    assert {"**/*.py", "prompts/**/*.md", ".claude/agents/**/*.md"} <= rutas


@pytest.mark.parametrize("path", QUIEN_CONSULTA, ids=lambda p: p.name)
def test_la_busqueda_cabe_en_las_herramientas_del_rol(path: Path) -> None:
    """Una orden que el rol no puede ejecutar deja la regla en un gesto."""
    texto = _texto(path)
    if "factory brain search" not in texto:
        return
    if path.parent.name == "agents":
        cabecera = path.read_text(encoding="utf-8").split("---")[1]
        assert "bash" in cabecera.lower(), (
            f"{path.name}: manda ejecutar un comando y no declara Bash"
        )
        return
    # maker e intake no declaran herramientas aquí: las fija default_roles().
    from factory.config import default_roles

    permitidas = " ".join(default_roles()[path.stem].allowed_tools)
    assert "factory" in permitidas, (
        f"{path.name}: manda ejecutar `factory brain search` y el rol no lo tiene permitido"
    )


def test_las_reglas_de_oficio_estan_listadas_donde_se_buscan() -> None:
    """roles.md es el registro canónico; una regla que no está ahí no existe para quien lo lea."""
    _contiene(ROLES, "expertos", "abriría un hilo en el pull request")
    assert "cinco reglas" not in _texto(ROLES), "roles.md vuelve a contar cinco reglas"


def test_la_puerta_documentada_es_la_puerta_que_hay() -> None:
    """Un documento que describe la versión anterior del script manda a buscar lo que no existe."""
    _contiene(REC, "PRE_PR_STRICT", "PRE_PR_MAX_COMPLEJIDAD", "sin commitear")
