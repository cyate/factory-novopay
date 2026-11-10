"""`scripts/pre-pr.sh` ejecutado de verdad: el paso de CodeRabbit y el árbol con `entregas/`."""

import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import init_git_repo

REPO = Path(__file__).resolve().parents[1]


def _repo(tmp_path: Path) -> Path:
    root = init_git_repo(tmp_path / "r")
    subprocess.run(["git", "branch", "base"], cwd=root, check=True)
    for ruta in ("scripts/check.sh", ".venv/bin/factory"):
        stub = root / ruta
        stub.parent.mkdir(parents=True, exist_ok=True)
        stub.write_text("#!/bin/sh\nexit 0\n")
        stub.chmod(0o755)
    shutil.copy(REPO / "scripts" / "pre-pr.sh", root / "scripts" / "pre-pr.sh")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "cambio"], cwd=root, check=True)
    return root


def _correr(root: Path, tmp_path: Path, coderabbit: int | None, strict: bool = False):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    for cmd in ("git", "bash", "dirname"):
        (bin_dir / cmd).symlink_to(shutil.which(cmd))
    if coderabbit is not None:
        fake = bin_dir / "coderabbit"
        fake.write_text(f"#!/bin/sh\nexit {coderabbit}\n")
        fake.chmod(0o755)
    env = {"PATH": str(bin_dir), "HOME": str(tmp_path)}
    if strict:
        env["PRE_PR_STRICT"] = "1"
    return subprocess.run(
        ["bash", "scripts/pre-pr.sh", "base"], cwd=root, env=env, capture_output=True, text=True
    )


@pytest.mark.parametrize(
    ("coderabbit", "strict", "abre", "aviso"),
    [
        (0, False, True, False),
        (2, False, False, False),
        (1, False, True, True),
        (1, True, False, False),
        (None, False, True, True),
        (None, True, False, False),
    ],
)
def test_la_puerta_ante_coderabbit(tmp_path, coderabbit, strict, abre, aviso):
    r = _correr(_repo(tmp_path), tmp_path, coderabbit, strict)
    assert (r.returncode == 0) is abre, r.stderr
    assert ("AVISO" in r.stderr and "SIN la revisión" in r.stderr) is aviso


def test_entregas_sin_trackear_no_cierra_la_puerta(tmp_path):
    root = _repo(tmp_path)
    (root / "entregas").mkdir()
    (root / "entregas" / "x.md").write_text("qa\n")
    assert _correr(root, tmp_path, 0).returncode == 0


def _commit(root: Path, msg: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", msg], cwd=root, check=True)


def test_borrar_un_archivo_grande_entero_no_suma_lineas(tmp_path):
    root = init_git_repo(tmp_path / "r")
    (root / "grande.py").write_text("x = 1\n" * 600)
    _commit(root, "grande")
    root = _repo_sobre(root, tmp_path)
    (root / "grande.py").unlink()
    _commit(root, "borra")
    r = _correr(root, tmp_path, 0)
    assert r.returncode == 0, r.stderr
    assert "1 archivos, 0 líneas" in r.stdout
    assert "borrados enteros: 1" in r.stdout


def test_editar_600_lineas_cierra_la_puerta(tmp_path):
    root = init_git_repo(tmp_path / "r")
    (root / "grande.py").write_text("x = 1\n" * 600)
    _commit(root, "grande")
    root = _repo_sobre(root, tmp_path)
    (root / "grande.py").write_text("y = 2\n" * 600)
    _commit(root, "edita")
    r = _correr(root, tmp_path, 0)
    assert r.returncode == 1
    assert "se pasa del límite" in r.stderr


def _repo_sobre(root: Path, tmp_path: Path) -> Path:
    """Como `_repo`, pero la rama `base` queda en el commit actual y los stubs ya están dentro."""
    for ruta in ("scripts/check.sh", ".venv/bin/factory"):
        stub = root / ruta
        stub.parent.mkdir(parents=True, exist_ok=True)
        stub.write_text("#!/bin/sh\nexit 0\n")
        stub.chmod(0o755)
    shutil.copy(REPO / "scripts" / "pre-pr.sh", root / "scripts" / "pre-pr.sh")
    _commit(root, "stubs")
    subprocess.run(["git", "branch", "base"], cwd=root, check=True)
    return root
