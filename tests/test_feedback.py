"""`factory feedback`: recomendaciones de los revisores de un pull request."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from factory import feedback
from factory.cli import main

ROOT = Path("/repo")
URL = "https://github.com/org/repo/pull/120"


def hilo(
    revisor: str = "sam-pc-novo",
    *,
    resuelto: bool = False,
    respuestas: Sequence[str] = (),
    body: str = "**Hallazgo.** Propuesta: arreglarlo.",
    identificador: int = 4428418574,
) -> dict[str, Any]:
    comentarios = [
        {
            "databaseId": identificador,
            "author": {"login": revisor},
            "body": body,
            "url": f"{URL}#discussion_r{identificador}",
        }
    ]
    comentarios += [{"databaseId": 0, "author": {"login": r}, "body": "ok"} for r in respuestas]
    return {
        "isResolved": resuelto,
        "isOutdated": False,
        "path": "specs/spec.md",
        "line": 58,
        "originalLine": 40,
        "comments": {"nodes": comentarios},
    }


def respuesta(hilos: Sequence[dict[str, Any]], revisiones: Sequence[dict[str, Any]] = ()) -> Any:
    return {
        "data": {
            "repository": {
                "pullRequest": {
                    "title": "docs: cambio",
                    "url": URL,
                    "reviews": {"nodes": list(revisiones)},
                    "reviewThreads": {"nodes": list(hilos)},
                }
            }
        }
    }


class FakeGh:
    """Una respuesta por llamada y memoria de los comandos ejecutados."""

    def __init__(self, *respuestas: Any) -> None:
        self.respuestas = list(respuestas)
        self.comandos: list[list[str]] = []

    def __call__(self, args: Sequence[str], root: Path) -> subprocess.CompletedProcess[str]:
        self.comandos.append(list(args))
        salida = self.respuestas[min(len(self.comandos) - 1, len(self.respuestas) - 1)]
        if isinstance(salida, Exception):
            raise salida
        if isinstance(salida, subprocess.CompletedProcess):
            return salida
        return subprocess.CompletedProcess(args, 0, json.dumps(salida), "")


def test_la_url_trae_repositorio_y_numero_sin_preguntar_a_gh():
    gh = FakeGh(respuesta([hilo()]))
    informe = feedback.recoger(URL, ROOT, runner=gh)
    assert (informe.repo, informe.numero) == ("org/repo", 120)
    assert [c[0] for c in gh.comandos] == ["api"]
    assert "owner=org" in gh.comandos[0] and "number=120" in gh.comandos[0]


def test_un_numero_suelto_deduce_el_repositorio_del_directorio():
    gh = FakeGh({"nameWithOwner": "org/repo"}, respuesta([hilo()]))
    informe = feedback.recoger("120", ROOT, runner=gh)
    assert informe.repo == "org/repo"
    assert gh.comandos[0][:2] == ["repo", "view"]


def test_un_numero_con_repo_no_consulta_el_directorio():
    gh = FakeGh(respuesta([hilo()]))
    assert feedback.recoger("120", ROOT, repo="org/repo", runner=gh).repo == "org/repo"


def test_una_referencia_que_no_es_numero_ni_url_falla():
    with pytest.raises(feedback.FeedbackError):
        feedback.recoger("rama-x", ROOT, runner=FakeGh())


def test_los_hilos_resueltos_se_ocultan_y_se_cuentan():
    gh = FakeGh(respuesta([hilo(), hilo(resuelto=True, identificador=2)]))
    informe = feedback.recoger(URL, ROOT, runner=gh)
    assert len(informe.hilos) == 1 and informe.ocultos == 1

    todos = feedback.recoger(URL, ROOT, resueltos=True, runner=FakeGh(gh.respuestas[0]))
    assert len(todos.hilos) == 2 and todos.ocultos == 0


def test_el_filtro_de_revisor_acepta_un_trozo_del_login():
    datos = respuesta(
        [hilo("sam-pc-novo"), hilo("coderabbitai", identificador=3)],
        [
            {
                "author": {"login": "coderabbitai"},
                "state": "COMMENTED",
                "body": "resumen",
                "url": URL,
            }
        ],
    )
    informe = feedback.recoger(URL, ROOT, revisores=["sam"], runner=FakeGh(datos))
    assert [h.revisor for h in informe.hilos] == ["sam-pc-novo"]
    assert informe.revisiones == []


def test_el_hilo_guarda_quien_respondio_y_donde_cae():
    gh = FakeGh(respuesta([hilo(respuestas=["cyate"])]))
    [hilo_leido] = feedback.recoger(URL, ROOT, runner=gh).hilos
    assert hilo_leido.path == "specs/spec.md" and hilo_leido.line == 58
    assert hilo_leido.respuestas == ["cyate"]
    assert hilo_leido.comentario_id == 4428418574


def test_un_hilo_sin_linea_vigente_cae_en_la_original():
    nodo = hilo()
    nodo["line"] = None
    [hilo_leido] = feedback.recoger(URL, ROOT, runner=FakeGh(respuesta([nodo]))).hilos
    assert hilo_leido.line == 40


def test_los_cuerpos_largos_se_recortan():
    nodo = hilo(body="x" * (feedback.LIMITE_HILO + 500))
    [hilo_leido] = feedback.recoger(URL, ROOT, runner=FakeGh(respuesta([nodo]))).hilos
    assert hilo_leido.body.endswith("…(recortado)")
    assert len(hilo_leido.body) <= feedback.LIMITE_HILO + len("\n…(recortado)")


def test_las_revisiones_sin_cuerpo_no_entran():
    datos = respuesta(
        [],
        [
            {"author": {"login": "mrpalma19"}, "state": "COMMENTED", "body": "Blocker", "url": URL},
            {"author": {"login": "cyate"}, "state": "COMMENTED", "body": "  ", "url": URL},
        ],
    )
    informe = feedback.recoger(URL, ROOT, runner=FakeGh(datos))
    assert [r.revisor for r in informe.revisiones] == ["mrpalma19"]


def test_render_trae_el_comando_para_responder_cada_hilo():
    informe = feedback.recoger(URL, ROOT, runner=FakeGh(respuesta([hilo()])))
    texto = feedback.render(informe)
    assert "## sam-pc-novo" in texto
    assert "specs/spec.md:58 — sin_resolver" in texto
    assert "gh api repos/org/repo/pulls/120/comments/4428418574/replies" in texto


def test_un_pull_request_que_no_existe_falla_con_motivo():
    with pytest.raises(feedback.FeedbackError, match="#120"):
        feedback.recoger(URL, ROOT, runner=FakeGh({"data": {"repository": {"pullRequest": None}}}))


@pytest.mark.parametrize(
    "salida",
    [
        FileNotFoundError("gh"),
        subprocess.TimeoutExpired("gh", 30),
        subprocess.CompletedProcess(["gh"], 1, "", "gh: Not Found"),
        subprocess.CompletedProcess(["gh"], 0, "{no es json", ""),
    ],
)
def test_los_fallos_de_gh_se_cuentan_como_error_de_feedback(salida: Any):
    with pytest.raises(feedback.FeedbackError):
        feedback.recoger(URL, ROOT, runner=FakeGh(salida))


def test_el_filtro_alcanza_a_quien_responde_en_un_hilo_ajeno():
    """Una recomendación de sam dentro de un hilo de CodeRabbit sigue siendo de sam."""
    datos = respuesta([hilo("coderabbitai", respuestas=["sam-pc-novo"])])
    informe = feedback.recoger(URL, ROOT, revisores=["sam"], runner=FakeGh(datos))
    assert [h.revisor for h in informe.hilos] == ["coderabbitai"]
    # La cabecera es de quien abrió el hilo, así que el título dice quién más participa.
    assert "también sam-pc-novo" in feedback.render(informe)


def test_un_filtro_con_espacio_no_casa_a_caballo_entre_dos_logins():
    datos = respuesta([hilo("coderabbitai", respuestas=["sam-pc-novo"])])
    informe = feedback.recoger(URL, ROOT, revisores=["ai sam"], runner=FakeGh(datos))
    assert informe.hilos == []


def test_un_directorio_que_no_existe_no_se_confunde_con_gh_sin_instalar():
    fallo = FileNotFoundError(2, "No such file or directory")
    fallo.filename = "/no/existe"
    with pytest.raises(feedback.FeedbackError, match="/no/existe"):
        feedback.recoger(URL, ROOT, runner=FakeGh(fallo))


def test_el_cli_imprime_el_informe_en_json(capsys, monkeypatch):
    monkeypatch.setattr(feedback, "_run", FakeGh(respuesta([hilo()])))
    assert main(["feedback", URL, "--revisor", "sam", "--json"]) == 0
    datos = json.loads(capsys.readouterr().out)
    assert datos["repo"] == "org/repo" and len(datos["hilos"]) == 1


def test_el_cli_pasa_sus_opciones_a_recoger(monkeypatch):
    vistos: dict[str, Any] = {}

    def falso(pr: str, root: Path, **kwargs: Any) -> feedback.Informe:
        vistos.update({"pr": pr, "root": root, **kwargs})
        return feedback.Informe(repo="org/repo", numero=120, titulo="t", url=URL)

    monkeypatch.setattr(feedback, "recoger", falso)
    assert main(["feedback", "120", "--repo", "org/repo", "--revisor", "sam", "--resueltos"]) == 0
    assert vistos["repo"] == "org/repo"
    assert vistos["revisores"] == ["sam"] and vistos["resueltos"] is True


def test_el_cli_termina_en_2_con_el_motivo_en_stderr(capsys, monkeypatch):
    monkeypatch.setattr(
        feedback, "_run", FakeGh(subprocess.CompletedProcess(["gh"], 1, "", "gh: Not Found"))
    )
    assert main(["feedback", URL]) == 2
    assert "error:" in capsys.readouterr().err
