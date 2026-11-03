"""Instantánea: `{generated, repo, tokens, reviews, tasks, pulls, warnings}` (solo lectura)."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from factory.panel import pulls, reviews, state_dir, tasks, tokens, unreadable
from factory.state import RunState, RunStore
from factory.util import now_iso

SECTIONS = ("tokens", "reviews", "tasks", "pulls")


def load_runs(state: Path, warnings: list[str]) -> list[RunState]:
    """Como `RunStore.list_runs`, pero avisa de cada `state.json` que no se puede leer."""
    runs = []
    for path in sorted(RunStore(state).runs_dir.glob("*/state.json")):
        try:
            runs.append(RunState.from_dict(json.loads(path.read_text(encoding="utf-8"))))
        except OSError as exc:
            unreadable(path, exc, warnings)
        except Exception as exc:  # un state.json raro no debe tumbar el panel
            warnings.append(f"{path}: no se pudo leer ({type(exc).__name__}: {exc})")
    return sorted(runs, key=lambda run: run.started, reverse=True)


def _section(name: str, build: Callable[[], Any], empty: Any, warnings: list[str]) -> Any:
    """Cada sección se construye por separado: un fallo deja esa sección vacía con aviso."""
    try:
        return build()
    except Exception as exc:
        warnings.append(f"{name}: {type(exc).__name__}: {exc}")
        return empty


def build(
    root: Path,
    projects: Path,
    reader: tokens.TranscriptReader | None = None,
    pull_requests: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """`pull_requests` lo trae quien consultó a GitHub (el servidor o `--json`); sin él, vacía."""
    warnings: list[str] = []
    state = state_dir(root, warnings)
    runs = load_runs(state, warnings)
    return {
        "generated": now_iso(),
        "repo": str(root),
        "state_dir": str(state),
        "tokens": _section(
            "tokens", lambda: tokens.usage(state, projects, root, reader, warnings), {}, warnings
        ),
        "reviews": _section(
            "reviews", lambda: reviews.review_feed(state, runs, warnings=warnings), [], warnings
        ),
        "tasks": _section(
            "tasks", lambda: tasks.collect(root, state, runs, warnings), {}, warnings
        ),
        "pulls": pull_requests if pull_requests is not None else pulls.empty(),
        "warnings": warnings,
    }


def to_json(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, ensure_ascii=False, indent=2)
