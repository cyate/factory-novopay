"""Integridad de la copia literal de `security-audit` (ver su `UPSTREAM.md`)."""

import hashlib
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SKILL = RAIZ / ".claude" / "skills" / "security-audit"
UPSTREAM = SKILL / "UPSTREAM.md"

COMMIT = "c1c8a8c1471069fb0e188eeaff69b8e8db6564a8"
FECHA_DE_COPIA = "2026-10-28"
REPOSITORIO = "https://github.com/cloudflare/security-audit-skill"
ARCHIVOS_CLAVE = [
    "SKILL.md",
    "ATTACK-CLASSES.md",
    "HUNTING.md",
    "VALIDATION-AND-REPORTING.md",
    "RECONNAISSANCE.md",
    "report-schema.json",
    "LICENSE",
]
# 20 archivos de `skills/security-audit/` en c1c8a8c más el LICENSE de la raíz.
ARCHIVOS_COPIADOS = 21
FILA_SHA256 = re.compile(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$", re.MULTILINE)
# Ancla fuera de la copia: editar un archivo y su fila de UPSTREAM.md a la vez no basta,
# también habría que cambiar este test. Se recalcula al resincronizar (ver UPSTREAM.md).
HUELLA_DE_LA_TABLA = "5ed508f8acc5e07788631e4218e6347bc17fb626f72615c61e190586bd425f6c"
# Archivos que crea el sistema operativo al abrir la carpeta (Finder) y que nunca se versionan.
RUIDO_DEL_SO = {".DS_Store"}


def _tabla_sha256() -> list[tuple[str, str]]:
    return FILA_SHA256.findall(UPSTREAM.read_text(encoding="utf-8"))


def _huella(filas: list[tuple[str, str]]) -> str:
    return hashlib.sha256("\n".join(f"{n} {s}" for n, s in sorted(filas)).encode()).hexdigest()


def test_copia_con_archivos_clave_y_licencia():
    for nombre in ARCHIVOS_CLAVE:
        assert (SKILL / nombre).is_file(), f"falta {nombre} en la copia"
    licencia = (SKILL / "LICENSE").read_text(encoding="utf-8")
    assert "MIT License" in licencia
    assert "Cloudflare" in licencia


def test_upstream_cita_origen_commit_y_politica():
    texto = UPSTREAM.read_text(encoding="utf-8")
    assert REPOSITORIO in texto
    assert f"`{COMMIT}`" in texto
    assert FECHA_DE_COPIA in texto
    assert "MIT" in texto and "Cloudflare, Inc." in texto


def test_integridad_de_la_copia():
    """Cada archivo copiado coincide con su sha256 de UPSTREAM.md y no hay archivos extra."""
    filas = _tabla_sha256()
    esperados = dict(filas)
    assert len(filas) == len(esperados), "UPSTREAM.md repite archivos en la tabla de sha256"
    assert len(esperados) == ARCHIVOS_COPIADOS, f"la tabla lista {len(esperados)} archivos"
    assert "UPSTREAM.md" not in esperados
    assert _huella(filas) == HUELLA_DE_LA_TABLA, (
        "la tabla de sha256 de UPSTREAM.md cambió; si es una resincronización, actualiza "
        f"HUELLA_DE_LA_TABLA a {_huella(filas)}"
    )

    presentes = {
        ruta.relative_to(SKILL).as_posix()
        for ruta in SKILL.rglob("*")
        if ruta.is_file() and ruta.name not in RUIDO_DEL_SO
    } - {"UPSTREAM.md"}
    assert presentes == set(esperados), (
        f"sin listar: {sorted(presentes - set(esperados))}; "
        f"ausentes: {sorted(set(esperados) - presentes)}"
    )

    distintos = [
        nombre
        for nombre, sha in esperados.items()
        if hashlib.sha256((SKILL / nombre).read_bytes()).hexdigest() != sha
    ]
    assert not distintos, f"la copia literal se ha editado: {distintos}"
