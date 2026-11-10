# Cerebros de conocimiento

factory usa dos "cerebros" en Markdown, compatibles con cualquier LLM, más un **mapa** de la biblioteca. Todo se puede abrir en Obsidian o leer con `cat` y `grep`.

| | Cerebro principal | Mapa de la biblioteca | Cerebro diario |
|---|---|---|---|
| Qué es | tu biblioteca técnica: los libros convertidos a notas atómicas | el índice de esa biblioteca: libros, capítulos, secciones, páginas y keywords, **sin texto** | lo que aprendes en el día a día, con tus palabras |
| Ruta (`[brain]` en `factory.toml`) | `principal_dir = "brain-principal"` | `map_dir = "brain-mapa"` | `daily_dir = "brain-diario"` |
| Git | **nunca** se versiona (libros de terceros) | se versiona: viaja con cada clon | se versiona: viaja con cada clon |
| Quién escribe | solo `factory brain import` | solo `factory brain import` | `factory brain learn` |
| Los loops | solo lectura | solo lectura (ruta prohibida en todo objetivo) | solo lectura (ruta prohibida en todo objetivo) |

**Qué trae un clon del repo.** Trae el mapa (una búsqueda devuelve citas del tipo *Defending APIs* · cap. 9 · pp. 259–260) y tus fichas del cerebro diario. El texto de los libros solo está en los equipos donde importas tu copia: muévela tú entre tus computadores y ejecuta `factory brain import <ruta>` en cada uno.

Solo se trabaja con archivos **`.md`** y con los índices que los describen (`_catalog.jsonl`, `_books.json`, `llms.txt`). Los PDF nunca se importan y `.gitignore` los descarta (`*.pdf`).

## Cerebro principal

```bash
.venv/bin/factory brain import /ruta/redPDF/book/obsidian-vault   # copia solo .md + índices
.venv/bin/factory brain status                                    # origen, fecha, notas, libros, tokens
```

- **Copia filtrada.** Se copian las notas `.md`, `_catalog.jsonl`, `_books.json`, `llms.txt` y las guías (`AGENTS.md`, `CLAUDE.md`, `Index.md`). Se excluyen `.obsidian/`, `_build/`, los PDF y cualquier otro archivo. El origen no se modifica nunca.
- **Validación.** Cada ruta de `_catalog.jsonl` debe existir. Si falta alguna, la importación falla y la copia anterior queda intacta.
- **Refresco atómico.** Tras regenerar el vault (por ejemplo con `vault_builder.py`), basta con repetir `import`: la copia nueva se construye aparte y sustituye a la anterior de golpe, y las notas eliminadas desaparecen. Si la importación se interrumpe, se conserva la copia anterior.
- **Registro.** `brain-principal/.factory-import.json` guarda el origen, la fecha, el número de notas y libros, los tokens y la huella del catálogo.
- **Fuera de git.** Si el destino está dentro del repo, `import` lo añade a `.gitignore`. `factory doctor` falla (crítica) si algún archivo del cerebro principal llega al índice de git.
- **Integridad.** factory guarda una huella del cerebro y la compara al terminar cada ejecución de loop. Si un agente lo modificara, la ejecución lo avisa en `decision.md` y en la bandeja.

## Mapa de la biblioteca

Cada `factory brain import` regenera `brain-mapa/` desde el catálogo importado:

- `_catalog.jsonl`: una línea por nota con `path, book_id, type, title, chapter, chapter_title, section_path, pages, tokens, keywords`;
- `_books.json`: `slug, title, authors, domains, pages, chapters, notes, words, tokens`;
- `_map.json` (huella del catálogo de origen), `llms.txt`, `AGENTS.md` y un `.gitignore` propio, escritos por factory. El `.gitignore` hace que `.DS_Store` u `.obsidian/` nunca se versionen.

- **Sin texto de los libros.** Cada línea se construye desde una lista blanca de campos con formatos estrictos (keywords e identificadores sin espacios), así que nunca entra un `abstract`, un subtítulo, un cuerpo de nota ni las guías del vault. Un título de más de 20 palabras se recorta. `factory doctor` falla (crítica) si el texto de algún archivo del mapa no es exactamente el que generaría factory: un campo de más, un valor fuera de formato, una clave repetida, una guía editada o un archivo de más o de menos. Los títulos de hasta 20 palabras se aceptan como encabezados. Comprobado con el vault real: no aparece ninguno de sus 10.822 resúmenes, ni ninguno de los 45.011 fragmentos de 8 palabras de una muestra de 1.500 notas.
- **Determinista.** Reimportar el mismo vault no cambia ni un byte. Si cambió, `import` lo indica y avisa hasta que hagas `factory brain commit`.
- **Uso.** Si `brain-principal/` no está importado, la búsqueda usa el mapa. Las notas salen solo como cita y ruta ("texto no disponible en este equipo"). Si el principal está importado, el mapa se ignora y no hay resultados duplicados. Sin `abstract`, la puntuación pierde ese peso, pero los resultados principales coinciden.

## Consulta obligatoria antes de proponer

La biblioteca no está para leerla al final, cuando el código ya está escrito: está para decidir el
enfoque. Es una regla de `AGENTS.md`, y la llevan en su contrato el maker y los diez
jugadores del equipo (el `checker` no: juzga solo con los criterios, el diff y la verificación).

- **Qué se contrasta**: un enfoque, un arreglo o un hallazgo que no sea evidente desde el código.
  Un cambio mecánico —renombrar, mover un archivo, corregir una errata— no necesita cita.
- **Cómo se busca**: `factory brain search "<consulta en inglés>"` si el rol tiene `Bash` sin
  restringir; con Grep sobre `brain-principal/` si no lo tiene. Sin el cerebro principal importado
  queda `brain-mapa/`, que da la cita y la ruta pero no el texto.
- **El maker del loop no busca**: su `Bash` está restringido a cuatro patrones y no incluye
  `factory`; el orquestador ya no le inyecta conocimiento.
- **Cómo se cita**: `Libro · cap. N · pp. A–B`, junto a la recomendación. **Citar, no copiar**: el
  texto de los libros no entra en un informe, en un commit ni en un hilo de revisión.
- **Si no hay nada aplicable**: se dice. Que se buscó queda dicho, y la siguiente sesión no repite
  la búsqueda.

**Importar el cerebro no es opcional en la máquina donde se construye.** Sin
`factory brain import <ruta-del-vault>`, los agentes reciben citas sin texto y la consulta se queda
en un gesto. `factory brain status` dice en qué estado está.

## Precedencia: qué manda cuando dos fuentes no coinciden

- **Contrato, alcance y verificación de este repositorio**: mandan los documentos que se revisan junto al código — `AGENTS.md`, `docs/harness/` y las specs de `openspec/specs/`. Una nota del cerebro que los contradiga está desactualizada, por buena que suene.
- **Experiencia de uso**: mandan los cerebros — trampas observadas, costes medidos, errores ya cometidos. Una skill o un documento general describe el estándar como se pensó; el cerebro, lo que pasó al ejecutarlo.
- **La contradicción se registra, no se resuelve en silencio.** Déjala en `progress.md` o como nota del cerebro diario (`factory brain learn`), con las dos fuentes citadas. Elegir una y callar hace que la siguiente sesión repita la discusión.

## Cerebro diario

```bash
.venv/bin/factory brain learn "En macOS no existe timeout; usar el de la herramienta" --kind gotcha --tags macos,shell
.venv/bin/factory brain learn --file aprendizaje.md --kind decision --title "Por qué worktrees fuera del repo"
.venv/bin/factory brain reindex              # tras editar notas a mano
.venv/bin/factory brain commit -m "notas"    # commit SOLO de brain-diario/ (sin push)
```

- **Formato.** Cada aprendizaje es `brain-diario/AAAA/MM/AAAA-MM-DD-<slug>.md`. Su frontmatter lleva `id`, `type` (`learning`, `decision`, `gotcha` o `pattern`), `title`, `date`, `tags`, `keywords`, `abstract`, `source` (`manual` u otra etiqueta de origen) y `tokens`, con el mismo formato que el principal.
- **Índices.** factory regenera `_catalog.jsonl`, `AGENTS.md` y `llms.txt` en cada alta. `reindex` los reconstruye tras editar notas a mano e informa de las que tienen el frontmatter roto.
- **Protegido de los loops.** `brain-diario/**` es una ruta prohibida en **todo** objetivo: si una ronda crea, modifica o borra algo ahí, se revierte. Ni `factory.toml` ni `goal.md` pueden levantar la prohibición.
- **Fichas propias.** Es la base de conocimiento que compartes: escribe con tus palabras patrones, decisiones y checklists, también lo que saques de un libro, citándolo por capítulo y página en vez de copiar su texto. Viene sembrado con algunos aprendizajes de la construcción de factory (macOS, zsh, `claude -p`, búsqueda).
- **Commit explícito.** Nada se commitea solo. `factory brain commit` hace un commit únicamente de `brain-diario/` y `brain-mapa/` y deja intactos el resto de cambios.

## Búsqueda

```bash
.venv/bin/factory brain search "rate limiting"                    # ambos cerebros
.venv/bin/factory brain search "token bucket" --brain principal --limit 5 --json
```

La búsqueda es local y por palabras clave sobre los catálogos (título, keywords, sección, resumen y libro), sin acentos ni palabras vacías. Cada resultado trae ruta, título, cita (`Libro · cap. N · pp. A–B` o `Cerebro diario · fecha · origen`) y tokens. **El cerebro principal está en inglés**: busca en inglés.

### Acceso de lectura seguro

Maker y checker reciben `--add-dir <ruta absoluta>` por cada cerebro existente, y siempre (exista o no) las denegaciones `Edit(//<ruta>/**)` y `Write(//<ruta>/**)`. Se añaden en cada invocación, así que ni `factory.toml` ni `goal.md` pueden quitarlas. Como las listas de herramientas no son un sandbox, factory además compara la huella de ambos cerebros (notas `.md` e índices, sin archivos ocultos como `.DS_Store` u `.obsidian/`) al empezar y al terminar cada ejecución: si cambian o aparece uno nuevo, `decision.md` y la bandeja muestran un **AVISO de integridad** (en el principal, reimporta con `factory brain import`).

Comprobado con `claude -p` real (Claude Code, `acceptEdits`): un `Write` nuevo y un `Edit` sobre una nota existente del cerebro quedan en `permission_denials` sin tocar nada, y la lectura sí funciona. El `CLAUDE.md` o `AGENTS.md` de un cerebro **no** se carga en el contexto por estar en `--add-dir`: el agente solo lo ve si lo abre. Las rutas se resuelven (enlaces incluidos) para que `--add-dir` y las denegaciones usen exactamente la misma.

---
Requisitos en `openspec/specs/{main-brain,daily-brain,brain-retrieval,library-map}/`; diseño en `openspec/changes/archive/2026-10-28-add-knowledge-brains/` y, para el mapa, en `openspec/changes/archive/2026-10-29-add-library-map/`.
