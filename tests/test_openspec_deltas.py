"""Comprobaciones sobre los deltas de OpenSpec que `openspec validate` no hace."""

from __future__ import annotations

import re
from pathlib import Path

CABECERA = "## MODIFIED Requirements"
TITULOS = re.compile(r"^### Requirement: (.+)$", re.MULTILINE)


def test_cada_requisito_modificado_existe_en_la_spec_base() -> None:
    """`openspec validate` valida la forma del delta, no que el requisito exista.

    Un `MODIFIED` cuyo encabezado no case con la spec base, al archivar, duplica el
    requisito en vez de sustituirlo. Pasó con `Servidor local del panel`.
    """
    raiz = Path(__file__).resolve().parent.parent / "openspec"
    for delta in (raiz / "changes").glob("*/specs/*/spec.md"):
        texto = delta.read_text(encoding="utf-8")
        if CABECERA not in texto:  # la cabecera exacta, no la palabra suelta en prosa
            continue
        base = raiz / "specs" / delta.parent.name / "spec.md"
        if not base.exists():  # capacidad nueva: no hay nada que modificar
            continue
        existentes = set(TITULOS.findall(base.read_text(encoding="utf-8")))
        bloque = texto.split(CABECERA, 1)[1]
        for siguiente in ("## ADDED Requirements", "## REMOVED Requirements", "## RENAMED"):
            bloque = bloque.split(siguiente)[0]
        faltan = set(TITULOS.findall(bloque)) - existentes
        assert not faltan, f"{delta}: MODIFIED sin correspondencia en {base}: {sorted(faltan)}"
