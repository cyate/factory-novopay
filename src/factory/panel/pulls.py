"""Pull requests del repositorio: estado de revisión, tiempos y alertas.

Los datos se leen con el CLI `gh` (solo consultas) y viven en memoria del proceso del
panel: esta sección no escribe ningún archivo ni ejecuta operaciones de escritura sobre
GitHub. Sin `gh`, sin sesión o sin red, la sección queda vacía con el motivo en `error`.
"""

from __future__ import annotations

import json
import statistics
import subprocess
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

FIELDS = (
    "number",
    "title",
    "url",
    "author",
    "isDraft",
    "createdAt",
    "updatedAt",
    "mergedAt",
    "reviewDecision",
    "reviewRequests",
    "latestReviews",
    "additions",
    "deletions",
    "changedFiles",
    "files",
    "statusCheckRollup",
    "comments",
    "headRefName",
    "mergeable",
)
AUTHOR = "autor"
REVIEWER = "revisor"
OPEN_LIMIT = 30
MERGED_LIMIT = 10
TIMEOUT_S = 20
# Umbrales de alerta: los dos últimos son el límite de tamaño de PR de `CLAUDE.md`,
# que cuenta solo código y tests (la documentación no tiene límite).
STALE_H = 24.0
MAX_FILES = 10
MAX_LINES = 500
DOC_DIRS = ("openspec/", "docs/", "notes/", "entregas/", "testdata/", "diagramas/")
CODERABBIT = "@coderabbitai review"
CODERABBIT_BOT = "coderabbitai"
TEAM = "cifra"
MERGED = "fusionado"
# Vocabulario cerrado: la página pinta una etiqueta por cada uno, y un test lo comprueba.
STATES = ("sin_revisar", "en_revision", "cambios_pedidos", "aprobado", "borrador", MERGED)
ALERTS = (
    "checks_fallando",
    "cambios_pedidos",
    "conflictos",
    "sin_revisor",
    "parado",
    "sin_coderabbit",
    "sin_cifra",
    "demasiado_grande",
)
# Un escáner que responde en segundos no es una revisión: ni cuenta como revisor humano ni
# entra en el tiempo hasta la primera revisión. `gh` no marca los bots en estos campos.
BOTS = (CODERABBIT_BOT, "orca-security-us", "makeplane", "github-actions", "dependabot", "renovate")

# El orden importa: la consulta de autor va primera, así un PR que también tenga revisión
# pedida al usuario se queda con el rol `autor`.
QUERIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (AUTHOR, ("--state", "open", "--author", "@me", "--limit", str(OPEN_LIMIT))),
    (
        REVIEWER,
        ("--state", "open", "--search", "review-requested:@me", "--limit", str(OPEN_LIMIT)),
    ),
    (AUTHOR, ("--state", "merged", "--author", "@me", "--limit", str(MERGED_LIMIT))),
)
DECISIONS = {
    "APPROVED": "aprobado",
    "CHANGES_REQUESTED": "cambios_pedidos",
    "REVIEW_REQUIRED": "pendiente",
}
FAILED_CHECKS = {"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE", "ERROR"}
# Un check run trae `status`; una integración clásica (StatusContext) solo trae `state`.
PENDING_CHECKS = {"PENDING", "EXPECTED", "QUEUED", "IN_PROGRESS", "WAITING", "REQUESTED"}

Runner = Callable[[Sequence[str], Path], "subprocess.CompletedProcess[str]"]


class PullsError(RuntimeError):
    """No se pudieron leer los pull requests (sin `gh`, sin sesión, sin red o respuesta rara)."""


def _run(args: Sequence[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args], cwd=root, capture_output=True, text=True, timeout=TIMEOUT_S
    )


def _query(args: Sequence[str], root: Path, runner: Runner) -> list[dict[str, Any]]:
    command = ["pr", "list", "--json", ",".join(FIELDS), *args]
    try:
        proc = runner(command, root)
    except FileNotFoundError as exc:
        raise PullsError("no se encontró el CLI `gh`; instálalo o usa --no-pulls") from exc
    except subprocess.TimeoutExpired as exc:
        raise PullsError(f"`gh` no respondió en {TIMEOUT_S} s") from exc
    except OSError as exc:
        raise PullsError(f"no se pudo ejecutar `gh` ({exc})") from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise PullsError(f"`gh` falló ({proc.returncode}): {detail[0] if detail else 'sin salida'}")
    try:
        data = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise PullsError(f"`gh` devolvió algo que no es JSON ({exc})") from exc
    return [row for row in data if isinstance(row, dict)] if isinstance(data, list) else []


def _parse(ts: Any) -> datetime | None:
    try:
        moment = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def _hours(start: Any, end: Any) -> float | None:
    """Horas entre dos marcas ISO, o `None` si falta alguna o no se entiende."""
    begin, finish = _parse(start), _parse(end)
    if begin is None or finish is None:
        return None
    return round(max((finish - begin).total_seconds(), 0.0) / 3600, 1)


def _is_bot(name: str) -> bool:
    return name in BOTS or name.endswith(("[bot]", "-bot"))


def _review_logins(raw: dict[str, Any]) -> list[str]:
    """Login en minúsculas de quien ya dejó una revisión."""
    logins = []
    for review in raw.get("latestReviews") or []:
        if isinstance(review, dict):
            login = str((review.get("author") or {}).get("login", "")).lower()
            if login:
                logins.append(login)
    return logins


def _reviewers(raw: dict[str, Any]) -> list[str]:
    """Logins y equipos con revisión pedida, más quien ya revisó (en minúsculas)."""
    names = list(_review_logins(raw))
    for request in raw.get("reviewRequests") or []:
        if isinstance(request, dict):
            # Un equipo viene con `slug` completo (`novopayment/cifra`) y `name` corto.
            name = request.get("login") or request.get("slug") or request.get("name") or ""
            if name:
                names.append(str(name).lower())
    return sorted(set(names))


def _checks(rollup: Any) -> str:
    """`fallando`, `pendiente`, `ok`, o vacío si el PR no tiene checks."""
    if not isinstance(rollup, list) or not rollup:
        return ""
    pending = False
    for check in rollup:
        if not isinstance(check, dict):
            continue
        result = str(check.get("conclusion") or check.get("state") or "").upper()
        if result in FAILED_CHECKS:
            return "fallando"
        estado = str(check.get("status") or "").upper()
        if not result or result in PENDING_CHECKS or estado not in ("", "COMPLETED"):
            pending = True
    return "pendiente" if pending else "ok"


def _coderabbit(raw: dict[str, Any]) -> bool:
    """Si se pidió la revisión del bot con el comentario de `CLAUDE.md`, o si ya la hizo."""
    if CODERABBIT_BOT in _review_logins(raw):
        return True
    for comment in raw.get("comments") or []:
        if not isinstance(comment, dict):
            continue
        if CODERABBIT in str(comment.get("body", "")).lower():
            return True
        if str((comment.get("author") or {}).get("login", "")).lower() == CODERABBIT_BOT:
            return True
    return False


def _first_review(raw: dict[str, Any]) -> str:
    """Primera revisión humana que `gh` devuelve (guarda la última de cada revisor)."""
    stamps = [
        str(review.get("submittedAt"))
        for review in raw.get("latestReviews") or []
        if isinstance(review, dict)
        and review.get("submittedAt")
        and not _is_bot(str((review.get("author") or {}).get("login", "")).lower())
    ]
    return min(stamps) if stamps else ""


def _humans(reviewers: list[str]) -> list[str]:
    return [name for name in reviewers if not _is_bot(name)]


def _team_asked(reviewers: list[str]) -> bool:
    """El equipo revisor llega como `cifra` o con la organización delante."""
    return any(name == TEAM or name.endswith(f"/{TEAM}") for name in reviewers)


def _es_documentacion(path: str) -> bool:
    """Misma clasificación que `es_documentacion()` de `scripts/pre-pr.sh`."""
    if path.endswith((".md", ".txt", ".http", ".openapi.yaml", ".openapi.yml")):
        return True
    if path.startswith(DOC_DIRS) or "postman" in path:
        return True
    return "openapi" in path and path.endswith((".yaml", ".yml"))


def _size(raw: dict[str, Any]) -> dict[str, Any]:
    """Archivos y líneas de código y de documentación; sin lista fiable, el total sin separar.

    `gh` pide a GitHub como mucho 100 archivos: si la lista viene vacía o más corta que
    `changedFiles`, no se inventa el reparto y la cifra de código es el total.
    """
    total_files = int(raw.get("changedFiles") or 0)
    total_lines = int(raw.get("additions") or 0) + int(raw.get("deletions") or 0)
    files = [f for f in raw.get("files") or [] if isinstance(f, dict)]
    if not files or len(files) < total_files:
        return {
            "archivos_codigo": total_files,
            "lineas_codigo": total_lines,
            "archivos_doc": 0,
            "lineas_doc": 0,
            "tamano_separado": False,
        }
    size = {"archivos_codigo": 0, "lineas_codigo": 0, "archivos_doc": 0, "lineas_doc": 0}
    for item in files:
        kind = "doc" if _es_documentacion(str(item.get("path", ""))) else "codigo"
        size[f"archivos_{kind}"] += 1
        size[f"lineas_{kind}"] += int(item.get("additions") or 0) + int(item.get("deletions") or 0)
    return {**size, "tamano_separado": True}


def _state(entry: dict[str, Any]) -> str:
    if entry["fusionado"]:
        return MERGED
    if entry["borrador"]:
        return "borrador"
    if entry["revision"] in ("cambios_pedidos", "aprobado"):
        return entry["revision"]
    if entry["horas_primera_revision"] is not None or _humans(entry["revisores"]):
        return "en_revision"
    return "sin_revisar"


def _alerts(entry: dict[str, Any]) -> list[str]:
    """Lo que el usuario puede accionar hoy; un PR ya fusionado no espera nada de nadie."""
    if entry["estado"] == MERGED:
        return []
    reglas = [
        ("checks_fallando", entry["checks"] == "fallando"),
        ("cambios_pedidos", entry["revision"] == "cambios_pedidos"),
        ("conflictos", entry["conflictos"]),
        ("sin_revisor", not _humans(entry["revisores"]) and not entry["borrador"]),
        ("parado", (entry["horas_sin_actividad"] or 0) > STALE_H),
    ]
    if entry["rol"] == AUTHOR:  # reglas de oficio que solo el autor puede cumplir
        reglas += [
            ("sin_coderabbit", not entry["coderabbit"]),
            ("sin_cifra", not _team_asked(entry["revisores"])),
            (
                "demasiado_grande",
                entry["archivos_codigo"] > MAX_FILES or entry["lineas_codigo"] > MAX_LINES,
            ),
        ]
    return [codigo for codigo, aplica in reglas if aplica]


def _entry(raw: dict[str, Any], role: str, now: datetime) -> dict[str, Any]:
    merged = raw.get("mergedAt") or ""
    created = raw.get("createdAt", "")
    updated = raw.get("updatedAt", "")
    stamp = now.isoformat(timespec="seconds")
    entry = {
        "numero": raw.get("number") if isinstance(raw.get("number"), int) else 0,
        "titulo": str(raw.get("title", "")),
        "url": str(raw.get("url", "")),
        "rama": str(raw.get("headRefName", "")),
        "autor": str((raw.get("author") or {}).get("login", "")),
        "rol": role,
        "borrador": bool(raw.get("isDraft")),
        "revision": DECISIONS.get(str(raw.get("reviewDecision") or ""), "pendiente"),
        "checks": _checks(raw.get("statusCheckRollup")),
        "conflictos": raw.get("mergeable") == "CONFLICTING",
        "revisores": _reviewers(raw),
        "coderabbit": _coderabbit(raw),
        "archivos": int(raw.get("changedFiles") or 0),
        "lineas": int(raw.get("additions") or 0) + int(raw.get("deletions") or 0),
        **_size(raw),
        "creado": str(created),
        "actualizado": str(updated),
        "fusionado": str(merged),
        "horas_abierto": _hours(created, merged or stamp),
        "horas_sin_actividad": None if merged else _hours(updated, stamp),
        "horas_primera_revision": _hours(created, _first_review(raw)),
        "horas_ciclo": _hours(created, merged),
    }
    entry["estado"] = _state(entry)
    entry["alertas"] = _alerts(entry)
    return entry


def _median(values: list[float | None]) -> float | None:
    numbers = [v for v in values if isinstance(v, int | float)]
    return round(statistics.median(numbers), 1) if numbers else None


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    open_rows = [r for r in rows if r["estado"] != MERGED]
    merged_rows = [r for r in rows if r["estado"] == MERGED]
    return {
        "abiertos": len(open_rows),
        "mios": len([r for r in open_rows if r["rol"] == AUTHOR]),
        "por_revisar": len([r for r in open_rows if r["rol"] == REVIEWER]),
        "con_alerta": len([r for r in open_rows if r["alertas"]]),
        # Los fusionados también cuentan aquí: son los que tienen el dato completo.
        "mediana_primera_revision_h": _median([r["horas_primera_revision"] for r in rows]),
        "mediana_ciclo_h": _median([r["horas_ciclo"] for r in merged_rows]),
    }


def _order(row: dict[str, Any]) -> tuple:
    """Primero lo abierto, dentro lo que más alertas tiene y lleva más tiempo parado."""
    return (row["estado"] == MERGED, -len(row["alertas"]), -(row["horas_sin_actividad"] or 0))


def empty(error: str = "", now: datetime | None = None) -> dict[str, Any]:
    """Sección sin datos: el panel la pinta vacía y dice por qué."""
    now = now or datetime.now(UTC)
    return {
        "updated": now.isoformat(timespec="seconds"),
        "pulls": [],
        "resumen": _summary([]),
        "error": error,
    }


def collect(
    root: Path, runner: Runner | None = None, now: datetime | None = None
) -> dict[str, Any]:
    """Pull requests propios y con revisión pedida, con sus tiempos y alertas."""
    runner = runner or _run
    now = now or datetime.now(UTC)
    rows: dict[int, dict[str, Any]] = {}
    try:
        for role, args in QUERIES:
            for raw in _query(args, root, runner):
                entry = _entry(raw, role, now)
                rows.setdefault(entry["numero"], entry)
    except PullsError as exc:
        return empty(str(exc), now)
    except Exception as exc:  # una respuesta de `gh` con otra forma no tumba `--json`
        return empty(f"respuesta inesperada de `gh` ({type(exc).__name__}: {exc})", now)
    ordered = sorted(rows.values(), key=_order)
    return {
        "updated": now.isoformat(timespec="seconds"),
        "pulls": ordered,
        "resumen": _summary(ordered),
        "error": "",
    }
