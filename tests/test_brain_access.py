"""Acceso de lectura a los cerebros (`--add-dir`), denegaciones de escritura e integridad."""

import subprocess

import pytest
from conftest import make_loop_repo, write_goal

import factory.engine as engine_module
from factory.agents.claude_code import build_argv
from factory.agents.fake import FakeRunner, FakeStep, maker_done
from factory.brain.daily import DailyBrain
from factory.brain.importer import import_vault
from factory.config import LoopConfig, load_config
from factory.engine import LoopEngine
from factory.goal import GoalError, load_goal, parse_goal_text
from factory.inbox import Inbox
from factory.state import RunStore


def _repo(tmp_path, vault, toml=""):
    """Repo de loop con el cerebro principal importado y una nota en el diario."""
    root = make_loop_repo(tmp_path)
    if toml:
        (root / "factory.toml").write_text(toml)
    import_vault(vault, root / "brain-principal", root)
    DailyBrain(root / "brain-diario").add(
        "El rate limiting por usuario se configura en el gateway", kind="decision", day="2026-10-28"
    )
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "cerebros"], cwd=root, check=True)
    return root


def _run(root, runner=None, extra=""):
    runner = runner or FakeRunner(maker=[maker_done("creé a", **{"a.txt": "1"})])
    config = load_config(root)
    goal = load_goal(write_goal(root, extra=extra), config.loop)
    state = LoopEngine(config, goal, runner, echo=lambda _: None).run()
    return config, state, runner


def test_peticion_del_maker_con_acceso_a_los_cerebros(tmp_path, vault):
    root = _repo(tmp_path, vault, toml='[roles.maker]\ndenied_tools = ["Bash(git push:*)"]\n')
    config, _, runner = _run(root)
    brains = [config.principal_path, config.daily_path]
    for request in runner.calls:  # maker y checker
        assert request.add_dirs == brains
        for brain in brains:
            absolute = "//" + brain.as_posix().lstrip("/")
            assert f"Edit({absolute}/**)" in request.denied_tools
            assert f"Write({absolute}/**)" in request.denied_tools
        argv = build_argv(request)
        for brain in brains:
            i = argv.index(str(brain))
            assert argv[i - 1] == "--add-dir"


def test_sin_cerebros_no_hay_add_dir(tmp_path):
    root = make_loop_repo(tmp_path)
    _, state, runner = _run(root)
    request = runner.calls_for("maker")[0]
    assert request.add_dirs == [] and "--add-dir" not in build_argv(request)
    assert state.status == "completed"
    principal = load_config(root).principal_path  # la regla no necesita que la ruta exista
    assert f"Edit(//{principal.as_posix().lstrip('/')}/**)" in request.denied_tools


def test_override_de_goal_md_no_quita_las_denegaciones(tmp_path, vault):
    root = _repo(tmp_path, vault)
    extra = 'roles:\n  maker: {denied_tools: ["Bash(git push:*)"]}\n'
    config, _, runner = _run(root, extra=extra)
    request = runner.calls_for("maker")[0]
    assert "Bash(git push:*)" in request.denied_tools
    for brain in (config.principal_path, config.daily_path):
        assert f"Write(//{brain.as_posix().lstrip('/')}/**)" in request.denied_tools


def test_ruta_absoluta_con_enlace_se_resuelve(tmp_path):
    real = tmp_path / "real-brain"
    real.mkdir()
    (tmp_path / "enlace").symlink_to(real)
    root = tmp_path / "repo"
    root.mkdir()
    (root / "factory.toml").write_text(f'[brain]\nprincipal_dir = "{tmp_path / "enlace"}"\n')
    config = load_config(root)
    assert config.principal_path == real.resolve()  # misma ruta en --add-dir y en Edit(//…)


def test_cambio_en_el_cerebro_principal_durante_una_ejecucion(tmp_path, vault):
    root = _repo(tmp_path, vault)
    note = load_config(root).principal_path / "apisec" / "03-rate-limiting" / "02-token-bucket.md"

    def tamper(_request):
        note.write_text(note.read_text() + "\nEditado durante el loop.\n")

    runner = FakeRunner(
        maker=[
            FakeStep(output={"status": "done", "summary": "x"}, edits={"a.txt": "1"}, action=tamper)
        ]
    )
    config, state, _ = _run(root, runner)
    [warning] = [b for b in state.blockers if "integridad" in b]
    assert "cerebro principal" in warning and "factory brain import" in warning
    decision = (RunStore(config.state_path).run_dir(state.run_id) / "decision.md").read_text()
    assert "integridad" in decision
    [entry] = Inbox(config.state_path).pending()
    assert "integridad" in entry.body


def test_sin_cambios_no_hay_aviso_de_integridad(tmp_path, vault):
    root = _repo(tmp_path, vault)
    _, state, _ = _run(root)
    assert not any("integridad" in b for b in state.blockers)


def test_archivos_ocultos_no_dan_falsos_avisos(tmp_path, vault):
    root = _repo(tmp_path, vault)
    principal = load_config(root).principal_path

    def finder(_request):  # macOS y Obsidian escriben estos archivos solos
        (principal / ".DS_Store").write_bytes(b"x")
        (principal / ".obsidian").mkdir(exist_ok=True)
        (principal / ".obsidian" / "workspace.json").write_text("{}")

    step = FakeStep(output={"status": "done", "summary": "x"}, edits={"a.txt": "1"}, action=finder)
    _, state, _ = _run(root, FakeRunner(maker=[step]))
    assert not any("integridad" in b for b in state.blockers)


def test_cerebro_que_aparece_durante_la_ejecucion(tmp_path):
    root = make_loop_repo(tmp_path)
    daily = load_config(root).daily_path

    def create(_request):
        DailyBrain(daily).add("Nota creada a mitad de ejecución", day="2026-10-28")

    step = FakeStep(output={"status": "done", "summary": "x"}, edits={"a.txt": "1"}, action=create)
    _, state, _ = _run(root, FakeRunner(maker=[step]))
    [warning] = [b for b in state.blockers if "integridad" in b]
    assert "cerebro diario" in warning


def test_huella_inicial_fallida_no_da_falso_aviso(tmp_path, vault, monkeypatch):
    root = _repo(tmp_path, vault)
    calls = {"n": 0}
    real = engine_module.fingerprint

    def flaky(path):
        calls["n"] += 1
        if calls["n"] == 1:  # falla solo la huella inicial del principal
            raise OSError("disco ocupado")
        return real(path)

    monkeypatch.setattr(engine_module, "fingerprint", flaky)
    _, state, _ = _run(root)
    assert any("no se pudo calcular la huella" in b for b in state.blockers)
    assert not any("integridad" in b for b in state.blockers)


def _goal_con_knowledge(bloque: str):
    text = (
        '---\nid: g\nobjective: x\nacceptance:\n  - name: t\n    run: "true"\n'
        f"knowledge:\n{bloque}---\ncuerpo\n"
    )
    return parse_goal_text(text, LoopConfig())


def test_knowledge_valido_se_acepta_aunque_no_tenga_efecto():
    goal = _goal_con_knowledge('  queries: ["rate limiting"]\n  enabled: false\n')
    assert goal.knowledge_queries == ["rate limiting"]
    assert goal.knowledge_enabled is False


def test_knowledge_con_claves_ajenas_es_un_error():
    with pytest.raises(GoalError, match="`knowledge` admite solo"):
        _goal_con_knowledge("  otro: 1\n")


def test_knowledge_enabled_no_booleano_es_un_error():
    with pytest.raises(GoalError, match="knowledge.enabled debe ser true o false"):
        _goal_con_knowledge('  enabled: "no"\n')
