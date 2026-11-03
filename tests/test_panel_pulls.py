"""Sección `pulls` del panel: consultas a `gh`, roles, estados, tiempos y alertas."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from factory.panel import pulls

AHORA = datetime(2026, 10, 30, 12, 0, tzinfo=UTC)
ROOT = Path("/repo")


def pr(numero: int = 1, **overrides: Any) -> dict[str, Any]:
    """Un pull request con la forma que devuelve `gh pr list --json`."""
    base = {
        "number": numero,
        "title": f"PR {numero}",
        "url": f"https://github.com/org/repo/pull/{numero}",
        "author": {"login": "cyate"},
        "isDraft": False,
        "createdAt": "2026-10-30T09:00:00Z",
        "updatedAt": "2026-10-30T11:00:00Z",
        "mergedAt": None,
        "reviewDecision": "REVIEW_REQUIRED",
        "reviewRequests": [{"__typename": "User", "login": "grosales-np"}],
        "latestReviews": [],
        "additions": 10,
        "deletions": 5,
        "changedFiles": 3,
        "statusCheckRollup": [{"conclusion": "SUCCESS", "status": "COMPLETED"}],
        "comments": [{"author": {"login": "cyate"}, "body": "@coderabbitai review"}],
        "headRefName": "feature/x",
        "mergeable": "MERGEABLE",
    }
    base.update(overrides)
    return base


class FakeGh:
    """Devuelve una respuesta por consulta y guarda los comandos ejecutados."""

    def __init__(self, *respuestas: list[dict[str, Any]] | Exception) -> None:
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


def collect(*respuestas: Any, now: datetime = AHORA) -> dict[str, Any]:
    return pulls.collect(ROOT, FakeGh(*respuestas), now)


def una(*respuestas: Any, now: datetime = AHORA) -> dict[str, Any]:
    """El primer (y único) pull request del resultado."""
    data = collect(*respuestas, now=now)
    assert data["error"] == "", data["error"]
    assert len(data["pulls"]) == 1
    return data["pulls"][0]


def test_las_tres_consultas_son_de_solo_lectura():
    gh = FakeGh([])
    pulls.collect(ROOT, gh, AHORA)
    assert len(gh.comandos) == 3
    for comando in gh.comandos:
        assert comando[:2] == ["pr", "list"], "la sección solo lista pull requests"
        assert "--json" in comando
    plano = [" ".join(c) for c in gh.comandos]
    assert "--author @me" in plano[0] and "--state open" in plano[0]
    assert "--search review-requested:@me" in plano[1]
    assert "--state merged" in plano[2] and "--author @me" in plano[2]


def test_ninguna_consulta_escribe_en_github():
    gh = FakeGh([])
    pulls.collect(ROOT, gh, AHORA)
    prohibidos = {"create", "merge", "review", "comment", "close", "edit", "ready"}
    for comando in gh.comandos:
        assert not prohibidos & set(comando)


def test_un_pr_en_dos_consultas_figura_una_vez_como_autor():
    data = collect([pr(7)], [pr(7)], [])
    assert [p["numero"] for p in data["pulls"]] == [7]
    assert data["pulls"][0]["rol"] == "autor"


def test_el_rol_revisor_sale_de_la_segunda_consulta():
    data = collect([], [pr(9, author={"login": "otra-persona"})], [])
    assert data["pulls"][0]["rol"] == "revisor"


def test_tiempos_de_un_pr_abierto():
    fila = una([pr(1)], [], [])
    assert fila["horas_abierto"] == 3.0  # 09:00 → 12:00
    assert fila["horas_sin_actividad"] == 1.0  # 11:00 → 12:00
    assert fila["horas_ciclo"] is None


def test_horas_hasta_la_primera_revision():
    revisiones = [{"author": {"login": "grosales-np"}, "submittedAt": "2026-10-30T11:30:00Z"}]
    fila = una([pr(1, latestReviews=revisiones)], [], [])
    assert fila["horas_primera_revision"] == 2.5  # 09:00 → 11:30


def test_la_revision_de_un_bot_no_cuenta_como_primera_revision():
    """Un escáner que responde en segundos falsearía el tiempo de revisión."""
    revisiones = [
        {"author": {"login": "orca-security-us"}, "submittedAt": "2026-10-30T09:00:30Z"},
        {"author": {"login": "grosales-np"}, "submittedAt": "2026-10-30T11:30:00Z"},
    ]
    fila = una([pr(1, latestReviews=revisiones)], [], [])
    assert fila["horas_primera_revision"] == 2.5


def test_un_pr_fusionado_trae_su_ciclo_y_ninguna_alerta():
    fusionado = pr(2, mergedAt="2026-10-30T15:00:00Z", changedFiles=40, comments=[])
    fila = una([], [], [fusionado])
    assert fila["estado"] == "fusionado"
    assert fila["horas_ciclo"] == 6.0  # 09:00 → 15:00
    assert fila["horas_sin_actividad"] is None
    assert fila["alertas"] == []


@pytest.mark.parametrize(
    ("overrides", "estado"),
    [
        ({"isDraft": True}, "borrador"),
        ({"reviewDecision": "APPROVED"}, "aprobado"),
        ({"reviewDecision": "CHANGES_REQUESTED"}, "cambios_pedidos"),
        ({"reviewRequests": []}, "sin_revisar"),
        ({}, "en_revision"),
    ],
)
def test_estados(overrides: dict[str, Any], estado: str):
    assert una([pr(1, **overrides)], [], [])["estado"] == estado


def test_un_revisor_bot_no_pone_el_pr_en_revision():
    peticiones = [{"__typename": "User", "login": "coderabbitai"}]
    assert una([pr(1, reviewRequests=peticiones)], [], [])["estado"] == "sin_revisar"


@pytest.mark.parametrize(
    ("overrides", "alerta"),
    [
        (
            {"statusCheckRollup": [{"conclusion": "FAILURE", "status": "COMPLETED"}]},
            "checks_fallando",
        ),
        ({"reviewDecision": "CHANGES_REQUESTED"}, "cambios_pedidos"),
        ({"mergeable": "CONFLICTING"}, "conflictos"),
        ({"reviewRequests": []}, "sin_revisor"),
        ({"updatedAt": "2026-10-28T09:00:00Z"}, "parado"),
        ({"comments": []}, "sin_coderabbit"),
        ({"changedFiles": 14}, "demasiado_grande"),
        ({"additions": 400, "deletions": 300}, "demasiado_grande"),
    ],
)
def test_cada_alerta(overrides: dict[str, Any], alerta: str):
    assert alerta in una([pr(1, **overrides)], [], [])["alertas"]


def test_un_pr_limpio_no_tiene_alertas():
    equipo = [{"__typename": "Team", "name": "cifra", "slug": "novopayment/cifra"}]
    peticiones = [{"__typename": "User", "login": "grosales-np"}, *equipo]
    assert una([pr(1, reviewRequests=peticiones)], [], [])["alertas"] == []


def test_el_equipo_revisor_vale_con_la_organizacion_delante():
    """`gh` devuelve el equipo como `novopayment/cifra`, no como `cifra`."""
    equipo = [{"__typename": "Team", "name": "cifra", "slug": "novopayment/cifra"}]
    assert "sin_cifra" not in una([pr(1, reviewRequests=equipo)], [], [])["alertas"]
    assert "sin_cifra" in una([pr(1)], [], [])["alertas"]


def test_coderabbit_cumple_si_el_bot_ya_reviso():
    """Importa que CodeRabbit haya mirado el PR, no con qué palabras se le llamó."""
    revisiones = [{"author": {"login": "coderabbitai"}, "submittedAt": "2026-10-30T10:00:00Z"}]
    fila = una([pr(1, comments=[], latestReviews=revisiones)], [], [])
    assert "sin_coderabbit" not in fila["alertas"]


def test_el_revisor_no_carga_con_las_reglas_del_autor():
    ajeno = pr(5, author={"login": "otra-persona"}, changedFiles=40, comments=[])
    fila = una([], [ajeno], [])
    assert fila["rol"] == "revisor"
    for regla in ("demasiado_grande", "sin_coderabbit", "sin_cifra"):
        assert regla not in fila["alertas"]


def test_un_borrador_no_alerta_por_falta_de_revisor():
    fila = una([pr(1, isDraft=True, reviewRequests=[])], [], [])
    assert "sin_revisor" not in fila["alertas"]


@pytest.mark.parametrize(
    "check",
    [
        {"status": "IN_PROGRESS", "conclusion": ""},  # check run
        {"state": "PENDING"},  # integración clásica: solo trae `state`
    ],
)
def test_los_checks_pendientes_no_son_un_fallo_ni_un_ok(check: dict[str, Any]):
    fila = una([pr(1, statusCheckRollup=[check])], [], [])
    assert fila["checks"] == "pendiente"
    assert "checks_fallando" not in fila["alertas"]


def test_resumen_y_medianas():
    revisiones = [{"author": {"login": "grosales-np"}, "submittedAt": "2026-10-30T11:30:00Z"}]
    abiertos = [pr(1, latestReviews=revisiones), pr(2, changedFiles=40)]
    ajeno = pr(3, author={"login": "otra-persona"})
    fusionados = [pr(4, mergedAt="2026-10-30T15:00:00Z")]
    resumen = collect(abiertos, [ajeno], fusionados)["resumen"]
    assert resumen["abiertos"] == 3
    assert resumen["mios"] == 2 and resumen["por_revisar"] == 1
    assert resumen["con_alerta"] == 2  # el 2 por tamaño, el 3 no tiene equipo ni reglas de autor
    assert resumen["mediana_primera_revision_h"] == 2.5
    assert resumen["mediana_ciclo_h"] == 6.0


def test_el_orden_pone_delante_lo_que_pide_accion():
    limpio = pr(1, reviewRequests=[{"__typename": "Team", "slug": "novopayment/cifra"}])
    conflictivo = pr(2, mergeable="CONFLICTING", comments=[])
    fusionado = pr(3, mergedAt="2026-10-30T15:00:00Z")
    data = collect([limpio, conflictivo], [], [fusionado])
    assert [p["numero"] for p in data["pulls"]] == [2, 1, 3]


def test_sin_gh_la_seccion_queda_vacia_con_el_motivo():
    data = collect(FileNotFoundError("gh"))
    assert data["pulls"] == []
    assert "gh" in data["error"]
    assert data["resumen"]["abiertos"] == 0


def test_sin_sesion_iniciada_el_motivo_es_el_de_gh():
    fallo = subprocess.CompletedProcess([], 4, "", "gh: no autenticado\nmás detalle")
    data = collect(fallo)
    assert data["pulls"] == []
    assert "no autenticado" in data["error"]


def test_una_respuesta_que_no_es_json_no_rompe_el_panel():
    rara = subprocess.CompletedProcess([], 0, "<html>", "")
    assert "JSON" in collect(rara)["error"]


def test_un_gh_que_se_cuelga_no_bloquea_el_panel():
    data = collect(subprocess.TimeoutExpired("gh", pulls.TIMEOUT_S))
    assert data["pulls"] == []
    assert "no respondió" in data["error"]


def test_la_seccion_vacia_tiene_la_misma_forma():
    vacia = pulls.empty("sin datos", AHORA)
    llena = collect([pr(1)], [], [])
    assert set(vacia) == set(llena)
    assert set(vacia["resumen"]) == set(llena["resumen"])


def test_un_pr_en_su_peor_momento_dispara_todas_las_alertas():
    """Si aparece una alerta nueva sin entrar en `ALERTS`, la página no sabría pintarla."""
    peor = pr(
        1,
        statusCheckRollup=[{"conclusion": "FAILURE", "status": "COMPLETED"}],
        reviewDecision="CHANGES_REQUESTED",
        mergeable="CONFLICTING",
        reviewRequests=[],
        updatedAt="2026-10-28T09:00:00Z",
        comments=[],
        changedFiles=40,
    )
    assert set(una([peor], [], [])["alertas"]) == set(pulls.ALERTS)


def test_la_pagina_sabe_pintar_cada_estado_y_cada_alerta():
    pagina = (Path(pulls.__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
    for codigo in (*pulls.STATES, *pulls.ALERTS):
        assert f"{codigo}:" in pagina, codigo


def test_la_pagina_filtra_por_rol_y_por_alerta():
    """Los cuatro filtros son un MUST de la spec: borrar uno tiene que ponerse rojo."""
    pagina = (Path(pulls.__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
    filtros = pagina.split("const PULL_FILTERS", 1)[1].split("\n", 1)[0]
    for valor in ("todos", pulls.AUTHOR, pulls.REVIEWER, "alerta"):
        assert f'"{valor}"' in filtros, valor


def test_la_mediana_de_la_primera_revision_cuenta_los_fusionados():
    """Un PR fusionado es el único con el dato completo: dejarlo fuera falsea la mediana."""
    revisiones = [{"author": {"login": "grosales-np"}, "submittedAt": "2026-10-30T12:00:00Z"}]
    fusionado = pr(2, mergedAt="2026-10-30T15:00:00Z", latestReviews=revisiones)
    assert collect([pr(1)], [], [fusionado])["resumen"]["mediana_primera_revision_h"] == 3.0


def test_una_respuesta_con_otra_forma_no_lanza_una_excepcion():
    """`factory panel --json` no tiene el `except` del sondeador: el fallo se absorbe aquí."""
    data = collect([{"number": 1, "author": "ya-no-es-un-objeto", "changedFiles": "muchos"}])
    assert data["pulls"] == []
    assert "inesperada" in data["error"]
