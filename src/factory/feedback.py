"""Recomendaciones de los revisores de un pull request: hilos en línea y revisiones generales.

Se leen con `gh api graphql` (solo consultas) y se imprimen agrupadas por revisor, con el
comando exacto para responder cada hilo. Este módulo no escribe nada: ni en el repositorio
ni en GitHub. El ciclo completo —comprobar, arreglar y responder— lo dirige la skill
`recomendaciones` (docs/harness/recomendaciones.md).
"""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

TIMEOUT_S = 30
# Recortes: un hilo es la recomendación accionable y se da entero; el cuerpo de una revisión
# de bot llega a decenas de miles de caracteres y solo sirve de contexto.
LIMITE_HILO = 4000
LIMITE_REVISION = 1500
# Paginación: las últimas 100 conversaciones y 50 revisiones, sin paginar. Un PR que se pase
# de ahí no existe todavía; si aparece, la paginación va aquí.
QUERY = """
query($owner:String!,$name:String!,$number:Int!){
  repository(owner:$owner,name:$name){
    pullRequest(number:$number){
      title
      url
      reviews(last:50){nodes{author{login} state url body}}
      reviewThreads(last:100){nodes{
        isResolved
        isOutdated
        path
        line
        originalLine
        comments(first:20){nodes{databaseId author{login} body url}}
      }}
    }
  }
}
"""
PR_URL_RE = re.compile(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)")

Runner = Callable[[Sequence[str], Path], "subprocess.CompletedProcess[str]"]


class FeedbackError(RuntimeError):
    """No se pudieron leer las recomendaciones: sin `gh`, sin sesión, sin red o PR inexistente."""


@dataclass
class Hilo:
    """Una conversación en línea: la recomendación, dónde cae y quién respondió."""

    revisor: str
    path: str
    line: int | None
    url: str
    comentario_id: int
    body: str
    resuelto: bool = False
    obsoleto: bool = False
    respuestas: list[str] = field(default_factory=list)


@dataclass
class Revision:
    """El cuerpo de una revisión: el resumen del revisor, sin sitio al que responder."""

    revisor: str
    estado: str
    url: str
    body: str


@dataclass
class Informe:
    repo: str
    numero: int
    titulo: str
    url: str
    hilos: list[Hilo] = field(default_factory=list)
    revisiones: list[Revision] = field(default_factory=list)
    ocultos: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _run(args: Sequence[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args], cwd=root, capture_output=True, text=True, timeout=TIMEOUT_S
    )


def _gh(args: Sequence[str], root: Path, runner: Runner) -> Any:
    try:
        proc = runner(args, root)
    except FileNotFoundError as exc:
        # `subprocess` lanza lo mismo si falta el binario que si no existe el directorio de trabajo.
        if exc.filename and Path(exc.filename) != Path("gh"):
            raise FeedbackError(f"no existe el directorio {exc.filename}") from exc
        raise FeedbackError(
            "no se encontró el CLI `gh`; instálalo y ejecuta `gh auth login`"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise FeedbackError(f"`gh` no respondió en {TIMEOUT_S} s") from exc
    except OSError as exc:
        raise FeedbackError(f"no se pudo ejecutar `gh` ({exc})") from exc
    if proc.returncode != 0:
        detalle = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise FeedbackError(
            f"`gh` falló ({proc.returncode}): {detalle[0] if detalle else 'sin salida'}"
        )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise FeedbackError(f"`gh` devolvió algo que no es JSON ({exc})") from exc


def referencia(pr: str, repo: str | None, root: Path, runner: Runner) -> tuple[str, int]:
    """Repositorio y número a partir de una URL de pull request o de un número suelto."""
    encontrado = PR_URL_RE.search(pr)
    if encontrado:
        owner, name, numero = encontrado.groups()
        return f"{owner}/{name}", int(numero)
    if not pr.isdigit():
        raise FeedbackError(f"no se entiende el pull request: {pr!r} (número o URL)")
    if repo:
        return repo, int(pr)
    datos = _gh(["repo", "view", "--json", "nameWithOwner"], root, runner)
    nombre = str(datos.get("nameWithOwner", "")) if isinstance(datos, dict) else ""
    if not nombre:
        raise FeedbackError("no se pudo deducir el repositorio; usa --repo owner/name")
    return nombre, int(pr)


def _recorta(texto: str, limite: int) -> str:
    texto = texto.strip()
    return texto if len(texto) <= limite else f"{texto[:limite].rstrip()}\n…(recortado)"


def _coincide(logins: Sequence[str], filtros: Sequence[str]) -> bool:
    """Sin filtros pasa todo. Con filtros basta un trozo del login: `sam` vale por `sam-pc-novo`.

    Cuenta cualquiera que participe en el hilo, no solo quien lo abrió: una recomendación de
    `sam` dentro de un hilo de CodeRabbit sigue siendo de `sam`.
    """
    if not filtros:
        return True
    return any(f.lower() in login.lower() for login in logins for f in filtros)


def _hilo(nodo: dict[str, Any]) -> Hilo | None:
    comentarios = [
        c for c in (nodo.get("comments") or {}).get("nodes") or [] if isinstance(c, dict)
    ]
    if not comentarios:
        return None
    primero = comentarios[0]
    return Hilo(
        revisor=str((primero.get("author") or {}).get("login", "")),
        path=str(nodo.get("path", "")),
        line=nodo.get("line") or nodo.get("originalLine"),
        url=str(primero.get("url", "")),
        comentario_id=int(primero.get("databaseId") or 0),
        body=_recorta(str(primero.get("body", "")), LIMITE_HILO),
        resuelto=bool(nodo.get("isResolved")),
        obsoleto=bool(nodo.get("isOutdated")),
        respuestas=[str((c.get("author") or {}).get("login", "")) for c in comentarios[1:]],
    )


def recoger(
    pr: str,
    root: Path,
    repo: str | None = None,
    revisores: Sequence[str] = (),
    resueltos: bool = False,
    runner: Runner | None = None,
) -> Informe:
    """Las recomendaciones del pull request, filtradas por revisor y sin las resueltas."""
    runner = runner or _run
    nombre, numero = referencia(pr, repo, root, runner)
    owner, _, name = nombre.partition("/")
    datos = _gh(
        [
            "api",
            "graphql",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-F",
            f"number={numero}",
            "-f",
            f"query={QUERY}",
        ],
        root,
        runner,
    )
    bruto = ((datos or {}).get("data") or {}).get("repository") or {}
    pull = bruto.get("pullRequest")
    if not isinstance(pull, dict):
        raise FeedbackError(f"{nombre} no tiene el pull request #{numero}")
    informe = Informe(
        repo=nombre,
        numero=numero,
        titulo=str(pull.get("title", "")),
        url=str(pull.get("url", "")),
    )
    for nodo in (pull.get("reviewThreads") or {}).get("nodes") or []:
        hilo = _hilo(nodo) if isinstance(nodo, dict) else None
        if hilo is None or not _coincide([hilo.revisor, *hilo.respuestas], revisores):
            continue
        if hilo.resuelto and not resueltos:
            informe.ocultos += 1
            continue
        informe.hilos.append(hilo)
    for nodo in (pull.get("reviews") or {}).get("nodes") or []:
        if not isinstance(nodo, dict) or not str(nodo.get("body", "")).strip():
            continue
        revisor = str((nodo.get("author") or {}).get("login", ""))
        if not _coincide([revisor], revisores):
            continue
        informe.revisiones.append(
            Revision(
                revisor=revisor,
                estado=str(nodo.get("state", "")),
                url=str(nodo.get("url", "")),
                body=_recorta(str(nodo.get("body", "")), LIMITE_REVISION),
            )
        )
    return informe


def _estado(hilo: Hilo) -> str:
    marcas = ["resuelto" if hilo.resuelto else "sin_resolver"]
    if hilo.obsoleto:
        marcas.append("obsoleto")
    return " · ".join(marcas)


def render(informe: Informe) -> str:
    """El informe en Markdown, con el comando de respuesta de cada hilo."""
    lineas = [f"# PR #{informe.numero} · {informe.titulo}", "", f"{informe.url}", ""]
    revisores = sorted({h.revisor for h in informe.hilos})
    resumen = f"{len(informe.hilos)} recomendación(es) en línea"
    if revisores:
        resumen += f" de {', '.join(revisores)}, quien abrió cada hilo"
    if informe.ocultos:
        resumen += f"; {informe.ocultos} resuelta(s) oculta(s) (--resueltos)"
    lineas += [resumen, ""]
    for revisor in revisores:
        lineas += [f"## {revisor}", ""]
        for hilo in [h for h in informe.hilos if h.revisor == revisor]:
            sitio = f"{hilo.path}:{hilo.line}" if hilo.line else hilo.path or "(sin archivo)"
            gente = ", ".join(sorted(set(hilo.respuestas)))
            tambien = f" · también {gente}" if gente else ""
            lineas += [f"### {sitio} — {_estado(hilo)}{tambien}", "", hilo.body, "", hilo.url, ""]
            if hilo.comentario_id:
                lineas += [
                    "Responder:",
                    "",
                    "```bash",
                    f"gh api repos/{informe.repo}/pulls/{informe.numero}"
                    f"/comments/{hilo.comentario_id}/replies -f body='…'",
                    "```",
                    "",
                ]
    if informe.revisiones:
        lineas += ["## Revisiones generales (contexto, sin hilo al que responder)", ""]
        for revision in informe.revisiones:
            lineas += [
                f"### {revision.revisor} — {revision.estado}",
                "",
                revision.body,
                "",
                revision.url,
                "",
            ]
    return "\n".join(lineas).rstrip() + "\n"
