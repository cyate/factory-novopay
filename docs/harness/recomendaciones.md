# Recomendaciones de los revisores

Un pull request vuelve con hilos de CodeRabbit, de Orca, de un revisor humano y de un agente
revisor como `sam-pc-novo`. El panel ya dice **que** hay revisiones; esto dice **qué** piden y
deja el camino hecho para contestarlas.

Dos piezas:

- `factory feedback`: las lee y las ordena. Solo consultas, no escribe nada.
- la skill `recomendaciones` (`.claude/skills/recomendaciones/`): dirige el ciclo entero
  —comprobar, arreglar y responder— con tu aprobación en cada hallazgo.

## Antes del PR: la puerta local

Un hilo de CodeRabbit en un pull request abierto es el mismo hallazgo que el CLI encuentra en esta
máquina, pero varias horas más tarde y con una vuelta de por medio. `./scripts/pre-pr.sh [base]`
cierra ese hueco. Antes de medir nada comprueba que haya algo que medir: con el árbol sucio cierra
con «hay cambios sin commitear» —lo que no está en un commit no llega al pull request— y sin ningún
commit sobre la base, también.
Después corre contra el diff la verificación del repositorio, el tamaño del PR, la complejidad de
lo que cambió y `coderabbit review --base <base> --gate major`. Termina en 0 cuando pasa todo lo
que sabe comprobar.

```bash
./scripts/pre-pr.sh            # contra main
./scripts/pre-pr.sh develop    # contra otra base
```

`--gate major` termina en 2 si queda algún hallazgo de severidad `major` o peor: justo lo que
mañana sería un hilo.

| Variable | Qué hace |
|---|---|
| `PRE_PR_MAX_COMPLEJIDAD` | umbral de complejidad ciclomática; por defecto 20. Sin umbral el informe termina siempre en 0 y el paso no comprueba nada. |
| `PRE_PR_STRICT=1` | sin el CLI `coderabbit` instalado la puerta falla en vez de saltárselo. |

Dos cosas que **no** cierran la puerta, y conviene saberlo: sin `coderabbit` instalado (salvo con
`PRE_PR_STRICT=1`) dice «Puerta abierta SIN la revisión de CodeRabbit» y termina en 0; y pasarse de
10 archivos o 600 líneas solo avisa, porque los archivos estáticos pueden pasarse y contarlos
aparte todavía no está decidido.

**Dos vueltas como máximo** (`CLAUDE.md`). Si tras la segunda siguen abriéndose hilos, el problema
no está en el hilo: o el PR es demasiado grande para leerse de una vez, o falta una instrucción en
`.coderabbit.yaml`. Las reglas con las que el bot revisa este repositorio viven ahí; un hilo que
repite algo que las reglas de la casa ya deciden es una instrucción que falta en ese archivo.

Por qué antes y no después: el coste de un defecto crece con lo tarde que se encuentra, y la forma
de no tener que arreglarlo es no introducirlo —*Defending APIs* · cap. 8 · p. 212—. Una revisión se
empieza en local, con el diff contra la rama base, no en el editor web del PR —*Web Application
Security* · cap. 25 · pp. 326–327—. Y un lazo de control solo estabiliza dentro de su rango: si la
corrección llega desde fuera del lazo, el sistema oscila en vez de asentarse —*The Software
Architect Elevator* · cap. 10 · pp. 100–101—.

## `factory feedback`

```bash
factory feedback 120                                   # el PR 120 del repositorio del directorio actual
factory feedback https://github.com/org/repo/pull/120  # desde cualquier sitio, con la URL
factory feedback 120 --repo org/repo                   # número suelto, repositorio explícito
factory feedback 120 --revisor sam                     # solo sus hilos; basta un trozo del login
factory feedback 120 --resueltos                       # también los hilos ya resueltos
factory feedback 120 --json                            # el mismo informe, para máquina
```

**Qué devuelve** (una consulta a `gh api graphql`, de solo lectura):

| Parte | Qué trae |
|---|---|
| Hilos en línea | revisor, `archivo:línea`, el comentario entero, si está resuelto u obsoleto, quién respondió y el comando `gh` exacto para contestar |
| Revisiones generales | el cuerpo de cada revisión, recortado a 1.500 caracteres: contexto, sin hilo al que responder |
| `ocultos` | cuántos hilos resueltos se dejaron fuera |

Por defecto se ocultan los hilos resueltos. El cuerpo de un hilo se da entero hasta 4.000
caracteres; a partir de ahí se recorta y queda la URL.

**Límites conocidos:** las últimas 100 conversaciones y 50 revisiones del PR, sin paginar. Un
`--revisor` filtra por subcadena del login, así que `pal` vale para `mrpalma19`, y se queda con los
hilos donde esa persona participa, los abra ella o responda en uno ajeno.

**Si falla:** sin `gh`, sin `gh auth login`, sin red o con un PR que no existe, termina en 2 con
el motivo en `stderr`. No escribe nada en ningún caso.

## El ciclo con la skill

`/recomendaciones <pr> [revisor]`, desde el repositorio del PR y en su rama:

1. **Leer:** `factory feedback`.
2. **Comprobar** cada recomendación contra el código citado: `aceptada`, `rechazada` (con
   evidencia) o `pregunta` (decisión humana).
3. **Enseñar el triaje** y esperar tu aprobación.
4. **Arreglar** lo aceptado, con la verificación del repositorio del PR en verde.
5. **Responder** cada hilo, uno a uno y con tu aprobación, con el comando `gh` del informe.

Lo que la skill **no** hace: resolver hilos (es la señal del revisor), hacer push, fusionar ni
abrir pull requests. Esas siguen siendo decisiones humanas (AGENTS.md).
