"""Contrato del jugador `entrega-qa` (#7): frontmatter D2/D8, paquete de entrega y superficies."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
AGENTE = REPO / ".claude" / "agents" / "entrega-qa.md"
EQUIPO = REPO / "docs" / "harness" / "equipo.md"
REGLAMENTO = REPO / ".claude" / "skills" / "equipo" / "SKILL.md"
README = REPO / "README.md"
ROLES = REPO / "docs" / "harness" / "roles.md"
CONVOCATORIA = "entregas/**"
CONSTRUCTOR = {"Read", "Edit", "Write", "Glob", "Grep"}


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
    assert datos["name"] == AGENTE.stem == "entrega-qa"
    assert datos["dorsal"] == 7 and type(datos["dorsal"]) is int
    assert datos["tipo"] == "constructor"
    assert datos["model"] == "sonnet"
    assert datos["convocatoria"] == CONVOCATORIA


def test_constructor_sin_agent_ni_bash():
    """Un constructor edita, pero no invoca a otros agentes ni ejecuta comandos (D8)."""
    datos, _ = _frontmatter(AGENTE)
    herramientas = {t.strip() for t in datos["tools"].split(",")}
    assert herramientas == CONSTRUCTOR
    assert "Agent" not in herramientas and "Bash" not in herramientas
    reglas = _cuerpo().split("## Reglas", 1)[1].split("## Qué escribes", 1)[0]
    assert "No ejecutas comandos" in reglas
    assert "python entregas/<TICKET>/escenarios.py --list" in reglas


def test_descripcion_en_una_linea_y_sin_truncar():
    descripcion = _frontmatter(AGENTE)[0]["description"]
    assert "\n" not in descripcion
    for clave in ("(#7)", "QA", "Cowork design", "entregas/<TICKET>/"):
        assert clave in descripcion


def test_solo_escribe_dentro_de_la_carpeta_del_ticket():
    reglas = _cuerpo().split("## Reglas", 1)[1].split("## Qué escribes", 1)[0]
    assert "Solo escribes dentro de `entregas/<TICKET>/`" in reglas
    assert "ni tests del repositorio" in reglas
    # Lo que ve mal fuera de su terreno lo reporta, no lo arregla.
    assert "no lo arregles" in reglas


def test_el_paquete_tiene_los_cuatro_archivos():
    paquete = _cuerpo().split("## Qué escribes", 1)[1].split("## Formato de salida", 1)[0]
    for archivo in ("<TICKET>.md", "escenarios.py", "README.md", "plan-desarrollo.md"):
        assert archivo in paquete, archivo
    # El plan lo escribe Cowork design, no el jugador.
    assert "tú no lo creas ni lo tocas" in paquete
    assert "iterar el documento no puede destruir el prompt que lo genera" in paquete.lower()


def test_el_briefing_pide_lo_que_el_plan_necesita():
    briefing = _cuerpo().split("### 1. `<TICKET>.md`", 1)[1].split("### 2.", 1)[0]
    for seccion in (
        "historia de usuario",
        "Qué hace cada API",
        "Reglas de negocio",
        "Mensajes de error",
        "Tablas afectadas",
        "Qué se puede hacer y qué no",
        "Concurrencia",
        "Seguridad",
        "Rutas del proyecto",
        "Preguntas abiertas",
    ):
        assert seccion in briefing, seccion
    assert "Cowork design" in briefing


def test_los_escenarios_corren_sin_instalar_nada():
    escenarios = _cuerpo().split("### 2. `escenarios.py`", 1)[1].split("### 3.", 1)[0]
    assert "solo stdlib" in escenarios
    assert "urllib.request" in escenarios
    for flag in ("--list", "--only", "--base-url"):
        assert flag in escenarios, flag
    # Sirve a un humano y a una tubería: salida legible y código de salida.
    assert "esperado frente a obtenido" in escenarios
    assert "sale con 0 si todo pasa y con 1 si algo falla" in escenarios
    assert "qué criterio de la HU prueba" in escenarios
    # El paquete se versiona en este repo, así que `check.sh` también lo lint-ea.
    assert "ruff format --check" in escenarios and "100 caracteres" in escenarios


def test_sin_secretos_ni_invenciones():
    reglas = _cuerpo().split("## Reglas", 1)[1].split("## Qué escribes", 1)[0]
    assert "Nunca escribes un secreto" in reglas
    assert "variables de entorno" in reglas
    assert "No inventas endpoints" in reglas
    assert "`archivo:línea`" in reglas
    assert "nunca un hecho" in reglas


def test_no_se_pisa_con_qa_ni_con_arquitecto_api():
    cabecera = _cuerpo().split("## Qué recibes", 1)[0]
    assert "`qa` (#2)" in cabecera and "`arquitecto-api` (#10)" in cabecera


def test_formato_empieza_por_la_cabecera_del_jugador():
    formato = _cuerpo().split("## Formato de salida", 1)[1]
    bloque = formato.split("```", 2)[1]
    assert bloque.strip().startswith("## Jugador: entrega-qa (#7)")
    assert "exactamente con la línea `## Jugador: entrega-qa (#7)`" in formato
    secciones = ("## Paquete escrito", "## Anclajes", "## Preguntas abiertas")
    for seccion in (*secciones, "## Fuera de mi alcance"):
        assert seccion in bloque, seccion


def test_las_cuatro_superficies_lo_fichan():
    equipo = EQUIPO.read_text(encoding="utf-8")
    fila = next(linea for linea in equipo.splitlines() if linea.startswith("| 7 |"))
    assert "`entrega-qa`" in fila and "constructor" in fila and "sonnet" in fila
    assert CONVOCATORIA in fila, "la tabla y el frontmatter divergen en la convocatoria"
    assert "7 entrega-qa" in equipo
    assert "`entrega-qa`, sonnet" in equipo
    # La lista de vacantes la comprueba `test_team_tecnico.py` desde VACANTES; aquí solo
    # importa que el 7 no vuelva a aparecer como libre.
    libres = next(linea for linea in equipo.splitlines() if "están libres" in linea)
    assert "7" not in libres

    reglamento = REGLAMENTO.read_text(encoding="utf-8")
    assert "`entrega-qa`) usan sonnet" in reglamento.split("## Coste", 1)[1]
    assert any("amplía con `entrega-qa`" in linea for linea in reglamento.splitlines())

    readme = README.read_text(encoding="utf-8")
    assert "| 7 | `entrega-qa` |" in readme
    vacantes = next(linea for linea in readme.splitlines() if "están vacantes" in linea)
    assert "7" not in vacantes

    roles = ROLES.read_text(encoding="utf-8")
    assert "`documentador` y `entrega-qa`)" in roles
    # La tabla de permisos por tipo nombra el terreno de cada constructor.
    tabla = next(linea for linea in roles.splitlines() if linea.startswith("| Constructores"))
    assert "`entrega-qa`: solo `entregas/<TICKET>/`" in tabla


def test_el_partido_sabe_donde_juega():
    """Fases 3 y 4: construye tras el constructor y el técnico lista sus escenarios."""
    reglamento = REGLAMENTO.read_text(encoding="utf-8")
    construccion = reglamento.split("## 3. Construcción", 1)[1].split("## 4.", 1)[0]
    assert "`entrega-qa`" in construccion and "entregas/<TICKET>/" in construccion
    verificacion = reglamento.split("## 4. Verificación", 1)[1].split("## 5.", 1)[0]
    assert "python entregas/<TICKET>/escenarios.py --list" in verificacion
    assert "no lanza ninguna petición" in verificacion

    fases = EQUIPO.read_text(encoding="utf-8")
    fila_3 = next(linea for linea in fases.splitlines() if linea.startswith("| 3. Construcción"))
    fila_4 = next(linea for linea in fases.splitlines() if linea.startswith("| 4. Verificación"))
    assert "`entrega-qa`" in fila_3
    assert "escenarios.py --list" in fila_4


def test_las_entregas_estan_en_los_mapas_de_rutas():
    """`entregas/` se versiona: por eso el paquete no puede llevar secretos."""
    readme = README.read_text(encoding="utf-8")
    fila = next(
        linea for linea in readme.splitlines() if linea.startswith("| `entregas/<TICKET>/`")
    )
    assert "versionan" in fila and "secretos" in fila
    agentes = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    linea = next(x for x in agentes.splitlines() if x.startswith("- `entregas/<TICKET>/`"))
    assert "entrega-qa" in linea and "secretos" in linea


def test_la_prueba_real_distingue_revisor_de_constructor():
    """`dontAsk` deniega los Write: un constructor se prueba con `acceptEdits` (sesión 011)."""
    paso = (
        EQUIPO.read_text(encoding="utf-8")
        .split("## Cómo fichar", 1)[1]
        .split("## El partido", 1)[0]
    )
    assert "--permission-mode acceptEdits" in paso
    assert "permission_denials" in paso
    assert "solo muestra rutas de su terreno" in paso
    # Los costes del mismo documento tienen que decir los dos topes.
    costes = EQUIPO.read_text(encoding="utf-8").split("## Costes", 1)[1]
    assert "`--max-budget-usd 0.05` para un revisor" in costes and "`0.10`" in costes


def test_el_paquete_no_entra_en_el_diff_de_los_revisores():
    """Fase 5: su verificación es el `--list` de la fase 4, no una tanda de revisores."""
    revision = REGLAMENTO.read_text(encoding="utf-8").split("## 5. Revisión", 1)[1]
    lista = revision.split("2.", 1)[0]
    assert "Excluye `entregas/**`" in lista
    assert "`--list` de la fase 4" in lista
