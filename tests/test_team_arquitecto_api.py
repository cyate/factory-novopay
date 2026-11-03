"""Contrato del jugador `arquitecto-api` (#10): frontmatter D2/D8, secciones y especialidad."""

from __future__ import annotations

from pathlib import Path

import yaml

from factory.globs import matches

REPO = Path(__file__).resolve().parents[1]
AGENTE = REPO / ".claude" / "agents" / "arquitecto-api.md"
EQUIPO = REPO / "docs" / "harness" / "equipo.md"
REGLAMENTO = REPO / ".claude" / "skills" / "equipo" / "SKILL.md"
README = REPO / "README.md"
ROLES = REPO / "docs" / "harness" / "roles.md"
SOLO_LECTURA = {"Read", "Grep", "Glob"}
CONVOCATORIA = (
    "src/factory/panel/**, src/factory/agents/**, src/factory/engine.py, "
    "src/factory/tick.py, src/factory/gitops.py, **/*.go, **/*.java, **/*.tf, "
    "**/*.sql, **/openapi*.yaml, **/openapi*.yml"
)


def _frontmatter(path: Path) -> tuple[dict, str]:
    texto = path.read_text(encoding="utf-8")
    vacio, cabecera, cuerpo = texto.split("---", 2)
    assert vacio == "", "el archivo debe empezar por el frontmatter"
    return yaml.safe_load(cabecera), cuerpo


def _cuerpo() -> str:
    return _frontmatter(AGENTE)[1]


def test_frontmatter_del_jugador():
    datos, _ = _frontmatter(AGENTE)
    assert list(datos) == [
        "name",
        "description",
        "tools",
        "model",
        "dorsal",
        "tipo",
        "convocatoria",
    ]
    assert datos["name"] == AGENTE.stem == "arquitecto-api"
    assert datos["dorsal"] == 10 and type(datos["dorsal"]) is int
    assert datos["tipo"] == "revisor"
    assert datos["model"] == "opus"
    assert datos["convocatoria"] == CONVOCATORIA


def test_revisor_de_solo_lectura():
    datos, _ = _frontmatter(AGENTE)
    assert isinstance(datos["tools"], str)
    herramientas = {t.strip() for t in datos["tools"].split(",")}
    assert herramientas <= SOLO_LECTURA
    reglas = _cuerpo().split("## Reglas", 1)[1].split("## Checklist", 1)[0]
    assert "solo lectura" in reglas
    assert "no ejecutes comandos" in reglas


def test_descripcion_en_una_linea_y_sin_truncar():
    descripcion = _frontmatter(AGENTE)[0]["description"]
    assert "\n" not in descripcion
    for clave in ("(#10)", "API", "concurrencia", "AWS", "Solo lectura"):
        assert clave in descripcion


def test_secciones_obligatorias():
    cuerpo = _cuerpo()
    for seccion in (
        "## Qué recibes",
        "## Reglas",
        "## Checklist",
        "## Gravedad",
        "## Biblioteca",
        "## Formato de salida",
        "## Jugador: arquitecto-api (#10)",
        "## Veredicto",
        "## Hallazgos",
        "## needs_validation",
        "## Verificación recibida",
    ):
        assert seccion in cuerpo, seccion
    assert "mediapunta" in cuerpo


def test_las_cuatro_areas_de_la_especialidad():
    checklist = _cuerpo().split("## Checklist", 1)[1].split("## Gravedad", 1)[0]
    for area in (
        "### 1. Contrato de la API",
        "### 2. Seguridad de la frontera",
        "### 3. Concurrencia e integraciones",
        "### 4. AWS y plataforma",
    ):
        assert area in checklist, area
    for tema in ("timeout", "idempotencia", "pool", "saga", "KMS", "permisos mínimos"):
        assert tema in checklist.lower() or tema in checklist, tema


def test_no_duplica_al_portero():
    cuerpo = _cuerpo()
    assert "`seguridad` (#1)" in cuerpo
    assert "diseño" in cuerpo.split("## Qué recibes", 1)[0]


def test_hallazgo_sin_ubicacion_o_evidencia_no_cuenta():
    reglas = _cuerpo().split("## Reglas", 1)[1].split("## Checklist", 1)[0]
    assert "`archivo:línea`" in reglas
    assert "no lo reportes" in reglas
    # Reglas de oficio: supuestos declarados y superficie invisible al diff.
    assert "nunca un hecho" in reglas
    assert "no esté en el diff" in reglas


def test_biblioteca_cita_el_cerebro_sin_copiarlo():
    biblioteca = _cuerpo().split("## Biblioteca", 1)[1].split("## Formato de salida", 1)[0]
    assert "cerebro principal" in biblioteca
    assert "Cítalas, no las copies" in biblioteca
    for libro in (
        "Mastering API Architecture",
        "Defending APIs",
        "Building Microservices",
        "Security and Microservice Architecture on AWS",
        "Foundations of Scalable Systems",
    ):
        assert libro in biblioteca, libro


def test_gravedad_y_criterios_del_veredicto():
    cuerpo = _cuerpo()
    gravedad = cuerpo.split("## Gravedad", 1)[1].split("## Biblioteca", 1)[0]
    assert "`critical`:" in gravedad and "`medium`:" in gravedad and "`minor`:" in gravedad
    assert "no cambia el veredicto" in gravedad
    assert "`fail`: hay algún hallazgo `critical` o `medium`" in cuerpo
    assert "`pass_with_minor`: solo hay hallazgos `minor`" in cuerpo
    assert "`pass`: no hay hallazgos" in cuerpo


def test_formato_empieza_por_la_cabecera_del_jugador():
    formato = _cuerpo().split("## Formato de salida", 1)[1]
    bloque = formato.split("```", 2)[1]
    assert bloque.strip().startswith("## Jugador: arquitecto-api (#10)")
    assert "empieza exactamente por `## Jugador: arquitecto-api (#10)`" in formato
    assert "Superficie invisible al diff revisada" in bloque


def test_el_documento_del_equipo_lo_ficha_en_la_mediapunta():
    texto = EQUIPO.read_text(encoding="utf-8")
    fila = next(linea for linea in texto.splitlines() if linea.startswith("| 10 |"))
    assert "`arquitecto-api`" in fila and "revisor" in fila and "opus" in fila
    assert CONVOCATORIA in fila, "la tabla y el frontmatter divergen en la convocatoria"
    assert "10 arquitecto-api" in texto
    # La lista cambia con cada fichaje; lo que no puede volver es el 10 como vacante.
    libres = next(linea for linea in texto.splitlines() if "están libres" in linea)
    assert "10" not in libres
    assert "`arquitecto-api` y el técnico usan opus" in texto


def test_la_convocatoria_casa_un_contrato_anidado():
    """Los globs de OpenAPI valen a cualquier profundidad, no solo en la raíz."""
    patrones = [p.strip() for p in CONVOCATORIA.split(",")]
    assert matches("services/pagos/openapi.yaml", patrones)
    assert matches("docs/api/openapi-v2.yml", patrones)
    assert matches("src/factory/panel/server.py", patrones)
    assert not matches("src/factory/cli.py", patrones)


def test_el_reglamento_lo_conoce():
    reglamento = REGLAMENTO.read_text(encoding="utf-8")
    assert "vacantes (8 y 11)" in reglamento
    coste = reglamento.split("## Coste", 1)[1]
    assert "`arquitecto-api`, opus" in coste
    amplia = next(
        linea for linea in reglamento.splitlines() if "amplía con `arquitecto-api`" in linea
    )
    assert "AWS" in amplia and "concurrencia" in amplia


def test_el_readme_y_los_roles_lo_fichan():
    readme = README.read_text(encoding="utf-8")
    assert "| 10 | `arquitecto-api` |" in readme
    vacantes = next(linea for linea in readme.splitlines() if "están vacantes" in linea)
    assert "10" not in vacantes
    roles = ROLES.read_text(encoding="utf-8")
    assert "`producto` y `arquitecto-api`)" in roles


def test_exactamente_una_linea_de_veredicto():
    formato = _cuerpo().split("## Formato de salida", 1)[1]
    assert "exactamente una línea de veredicto" in formato
    assert "no copies la línea de la plantilla" in formato
