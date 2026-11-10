"""Los agentes interactivos de `.claude/agents/`: frontmatter válido y revisores de solo lectura."""

import re
from pathlib import Path

import pytest
import yaml

AGENTES = Path(__file__).resolve().parents[1] / ".claude" / "agents"
SOLO_LECTURA = {"Read", "Grep", "Glob"}
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _frontmatter(path: Path) -> dict:
    coincidencia = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    assert coincidencia, f"{path.name}: falta el frontmatter"
    return yaml.safe_load(coincidencia.group(1))


def test_quedan_los_tres_agentes():
    assert {p.stem for p in AGENTES.glob("*.md")} == {"checker", "ingeniero-software", "seguridad"}


@pytest.mark.parametrize("path", sorted(AGENTES.glob("*.md")), ids=lambda p: p.stem)
def test_frontmatter_completo(path: Path):
    datos = _frontmatter(path)
    assert datos["name"] == path.stem
    assert datos.get("description") and datos.get("tools") and datos.get("model")


def test_el_constructor_no_delega():
    herramientas = _frontmatter(AGENTES / "ingeniero-software.md")["tools"]
    assert "Agent" not in {h.strip() for h in herramientas.split(",")}


@pytest.mark.parametrize("nombre", ["checker", "seguridad"])
def test_los_revisores_son_de_solo_lectura(nombre: str):
    herramientas = {h.strip() for h in _frontmatter(AGENTES / f"{nombre}.md")["tools"].split(",")}
    assert herramientas <= SOLO_LECTURA
