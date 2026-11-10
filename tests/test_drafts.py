"""Escenarios de `request-intake`: los borradores no se ejecutan y la promoción es explícita."""

import pytest
from conftest import make_loop_repo

import factory.cli as cli
from factory.agents.fake import FakeRunner
from factory.cli import main
from factory.config import load_config
from factory.engine import LoopEngine
from factory.goal import GoalError, load_goal

DRAFT = """---
id: {id}
objective: Crear el marcador
mode: {mode}
status: draft
request: {request}
risk: low
surfaces: []
acceptance:
  - name: marca
    run: touch marcador-ejecutado
  - name: inexistente
    run: herramienta-que-no-existe --check
---
Cuerpo del borrador.
"""


def _draft(root, goal_id="x", mode="finite", request=""):
    path = root / "goals" / "drafts" / f"{goal_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DRAFT.format(id=goal_id, mode=mode, request=request))
    return path


def _no_runner(_config):
    raise AssertionError("un borrador no debe invocar agentes")


def test_ejecutar_un_borrador_con_goal_run(tmp_path, monkeypatch, capsys):
    root = make_loop_repo(tmp_path)
    monkeypatch.setattr(cli, "make_runner", _no_runner)
    assert main(["--root", str(root), "goal", "run", str(_draft(root))]) == 2
    assert "quítale la línea `status: draft`" in capsys.readouterr().err
    assert not (root / "marcador-ejecutado").exists()


def test_el_motor_tambien_rechaza_borradores(tmp_path):
    root = make_loop_repo(tmp_path)
    config = load_config(root)
    goal = load_goal(_draft(root), config.loop)
    with pytest.raises(GoalError, match="BORRADOR"):
        LoopEngine(config, goal, FakeRunner(), echo=lambda _: None).run()
    assert not (root / "marcador-ejecutado").exists()
