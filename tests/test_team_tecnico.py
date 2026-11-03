"""Escenarios de `team-match` para el técnico, el reglamento (`/equipo`) y `equipo.md`."""

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
TECNICO = REPO / ".claude" / "agents" / "tecnico.md"
SKILL = REPO / ".claude" / "skills" / "equipo" / "SKILL.md"
EQUIPO = REPO / "docs" / "harness" / "equipo.md"

JUGADORES = [
    "seguridad",
    "qa",
    "documentador",
    "revisor-pr",
    "metricas",
    "producto",
    "ingeniero-software",
    "arquitecto-api",
    "entrega-qa",
]
VACANTES = {
    8: "bibliotecario",
    11: "experiencia-cli",
}


def _frontmatter(path: Path) -> dict:
    texto = path.read_text(encoding="utf-8")
    assert texto.startswith("---\n"), f"{path.name} no empieza con frontmatter"
    bloque, separador, _ = texto[4:].partition("\n---\n")
    assert separador, f"{path.name} no cierra el frontmatter"
    datos = yaml.safe_load(bloque)
    assert isinstance(datos, dict), f"el frontmatter de {path.name} no es un mapa"
    return datos


def _cuerpo(path: Path) -> str:
    return path.read_text(encoding="utf-8").partition("\n---\n")[2]


def _herramientas(valor) -> set[str]:
    if isinstance(valor, str):
        valor = valor.split(",")
    return {str(nombre).strip() for nombre in valor if str(nombre).strip()}


def _reglamento() -> str:
    return _cuerpo(SKILL)


# --- Técnico ---------------------------------------------------------------------------------


def test_tecnico_sin_escritura():
    datos = _frontmatter(TECNICO)
    assert datos["name"] == "tecnico"
    assert datos["tipo"] == "tecnico"
    assert "dorsal" not in datos
    assert "convocatoria" not in datos
    assert datos["model"] == "opus"
    assert isinstance(datos["description"], str) and datos["description"].strip()
    herramientas = _herramientas(datos["tools"])
    assert "Agent" in herramientas
    assert not herramientas & {"Edit", "Write", "NotebookEdit"}


def test_tecnico_remite_al_reglamento():
    cuerpo = _cuerpo(TECNICO)
    assert ".claude/skills/equipo/SKILL.md" in cuerpo
    assert "claude --agent tecnico" in cuerpo
    assert "/equipo" in cuerpo
    assert "3 vueltas" in cuerpo
    assert "checker" in cuerpo


# --- Reglamento ------------------------------------------------------------------------------


def test_reglamento_declara_la_skill_equipo():
    datos = _frontmatter(SKILL)
    assert datos["name"] == "equipo"
    descripcion = datos["description"]
    assert isinstance(descripcion, str)
    for disparador in ("/equipo", "convoca al equipo", "partido", "revisa esta rama con el equipo"):
        assert disparador in descripcion


def test_convocatoria_parcial_justificada():
    texto = _reglamento()
    assert "factory team lineup" in texto
    assert "Publica la alineación antes de invocar a nadie" in texto
    assert "| # | Posición | Jugador | ¿Convocado? | Motivo o ajuste |" in texto
    assert "vacantes nunca se convocan" in texto


def test_el_tecnico_amplia_la_sugerencia():
    texto = _reglamento()
    assert "justifica cada alta o baja frente a ella" in texto
    assert re.search(
        r"amplía con `seguridad` si la petición habla de autenticación, secretos", texto
    )


def test_pregunta_abierta_antes_de_construir():
    texto = _reglamento()
    assert "preguntas abiertas van al humano antes de construir" in texto
    assert "AskUserQuestion" in texto
    assert "No invoques a `ingeniero-software` hasta tener respuesta" in texto


def test_informe_de_complejidad_para_metricas():
    texto = _reglamento()
    assert "./scripts/check.sh" in texto
    assert "factory complexity --base" in texto
    assert "--json" in texto
    assert "metricas" in texto


def test_revision_sin_efectos():
    texto = _reglamento()
    assert "subagent_type" in texto
    assert "en un mismo mensaje" in texto
    assert re.search(r"git status --porcelain`\*\* antes", texto)
    assert re.search(r"git status --porcelain`\*\* después.{0,80}descarta", texto, re.DOTALL)


def test_hallazgo_sin_evidencia():
    texto = _reglamento()
    assert re.search(r"sin `archivo:línea` o sin evidencia no cuentan.{0,120}concrete\b", texto)


def test_revision_de_una_rama_de_un_loop():
    texto = _reglamento()
    assert "factory/<run-id>" in texto
    assert "main...<rama>" in texto
    assert "git log main..<rama>" in texto
    assert "git diff --name-only main...<rama>" in texto
    assert "archivo completo" in texto
    # Mismos artefactos del loop que revisor-pr: criterios y verificación, nunca razonamiento.
    regla = next(linea for linea in texto.splitlines() if "**Ramas `factory/<run-id>`:**" in linea)
    pasan, nunca = regla.split("Nunca", 1)
    for artefacto in ("goal.md", "rounds/<n>/checks.md", "land/checks.md"):
        assert artefacto in pasan, artefacto
    prohibidos = ("decision.md", "loop-state.md", "rounds/<n>/maker.md", "rounds/<n>/review.md")
    for artefacto in prohibidos:
        assert artefacto in nunca and artefacto not in pasan, artefacto


def test_veredicto_ambiguo_cuenta_como_fail():
    texto = _reglamento()
    assert "ambiguo" in texto
    assert "exactamente una línea de veredicto" in texto
    assert re.search(r"ambiguo.{0,200}`fail`", texto, re.DOTALL)


def test_acta_con_un_hallazgo_medio():
    texto = _reglamento()
    assert "| Jugador | Veredicto | critical | medium | minor |" in texto
    assert re.search(r"`fail` si algún jugador tiene un `critical` o un `medium`", texto)
    assert "vuelven a construcción" in texto
    assert "Máximo 3 vueltas" in texto


def test_acta_en_verde_antes_de_terminar_la_feature():
    texto = _reglamento()
    assert "## 8. Árbitro" in texto
    assert re.search(r"antes de `factory features verify` falta invocar al `checker`", texto)


# --- Documento temático ----------------------------------------------------------------------


def test_documento_del_equipo_nombra_la_plantilla():
    texto = EQUIPO.read_text(encoding="utf-8")
    assert texto.startswith("# El equipo ideal\n")
    for nombre in [*JUGADORES, "tecnico", "checker"]:
        assert f"`{nombre}`" in texto, f"equipo.md no nombra a {nombre}"


def test_documento_del_equipo_lista_las_vacantes():
    texto = EQUIPO.read_text(encoding="utf-8")
    for dorsal, perfil in VACANTES.items():
        assert re.search(rf"\|\s*{dorsal}\s*\|[^\n]*vacante", texto), f"falta la vacante {dorsal}"
        assert f"`{perfil}`" in texto, f"falta el perfil sugerido {perfil}"


def test_como_fichar_nombra_las_superficies_y_el_cambio_openspec():
    """La spec `team-match` ("Fichajes posteriores") exige coherencia en cuatro superficies."""
    texto = EQUIPO.read_text(encoding="utf-8")
    pasos = texto.split("## Cómo fichar", 1)[1].split("## El partido", 1)[0]
    superficies = ("`README.md`", "`.claude/skills/equipo/SKILL.md`", "`docs/harness/roles.md`")
    for superficie in superficies:
        assert superficie in pasos, superficie
    assert "Coste" in pasos and "vacantes" in pasos
    # El cambio OpenSpec deja de ser opcional si el fichaje toca un requisito de `team-match`.
    assert "toca un requisito de `team-match`" in pasos
    assert "Solo es opcional cuando ningún requisito cambia." in pasos


def test_las_tres_superficies_dicen_las_mismas_vacantes():
    """Los dorsales que nombra cada superficie son los de VACANTES, sea cual sea la redacción."""
    repo = EQUIPO.parents[2]
    superficies = {
        "equipo.md": (EQUIPO.read_text(encoding="utf-8"), "están libres"),
        "README.md": ((repo / "README.md").read_text(encoding="utf-8"), "están vacantes"),
        "SKILL.md": (SKILL.read_text(encoding="utf-8"), "vacantes ("),
    }
    for nombre, (texto, marca) in superficies.items():
        linea = next(x for x in texto.splitlines() if marca in x)
        # Por conjunto de dorsales, no por frase literal: así el singular no rompe el test.
        assert {int(n) for n in re.findall(r"\d+", linea)} == set(VACANTES), nombre


def test_documento_del_equipo_sin_enlaces_a_agentes():
    texto = EQUIPO.read_text(encoding="utf-8")
    assert not re.search(r"\]\([^)]*\.claude/", texto)
