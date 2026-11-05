---
id: 2026/11/2026-11-05-puntos-de-control-antes-de-abrir-un-pr
type: pattern
title: Puntos de control antes de abrir un PR (lista corta, una línea por regla)
date: '2026-11-05'
tags:
- revision
- cifra-spend
- checklist
- pre-pr
keywords:
- lista
- puntos de control
- antes de abrir
- revision
- grep
abstract: Una línea por regla, con el grep o la pregunta que la comprueba, destilada de lo que grosal-np y CodeRabbit corrigieron en 16 PRs.
source: manual
tokens: 900
---

# Puntos de control antes de abrir un PR

> Lista para abrir con prisa. Cada línea enlaza la nota con la evidencia y el arreglo. `BASE` = `origin/main` o la rama de la que apilas.

1. **Base sin lógica.** `git diff -U0 BASE... -- '*.sql' | grep -niE 'GENERATED|CREATE (OR REPLACE )?(FUNCTION|TRIGGER|VIEW)|CHECK *\('` y `grep -nE 'vw_|fn_|trg_'` en el Go nuevo; cada `UPDATE` nuevo escribe `updated_at`. → [tablas, claves e índices](2026-11-03-en-la-base-solo-tablas-claves-e-indices.md)
2. **Comentarios de 3 líneas como máximo, sin `SPD-nnn`.** `git diff -U0 BASE... | awk '/^\+[ \t]*(\/\/|--)/{n++; if(n==4) print}{if(!/^\+[ \t]*(\/\/|--)/)n=0}'` y `grep -nE '^\+.*SPD-[0-9]+'`. → [comentarios](2026-11-05-comentarios-de-tres-lineas-y-sin-ids-de-ticket.md)
3. **Nada afirmado que no sea cierto hoy.** `git diff -U0 BASE... | grep -nEi '^\+.*(//|--).*\b(only|every|always|never|impossible|exactly|único|nunca)\b'`; ¿sigue cierto si el PR siguiente quita algo? → [doc falsa](2026-11-05-doc-falsa-afirmar-lo-que-el-codigo-no-hace.md)
4. **Contrato en el mismo PR.** Si el diff toca `handlers/`, `in_out.go` o `errorcodes.go`, también toca `openapi`/`notes`/`specs`; `curl … | jq 'keys'`: nunca `data.data`. → [contrato](2026-11-05-el-contrato-se-actualiza-en-el-mismo-pr.md)
5. **Plane gana.** `grep -rniE 'terminal|only through INVITED|never accepted' openspec notes internal`; ¿algún test fija lo contrario de un escenario del ticket? No se automatiza. → [Plane gana](2026-11-05-cuando-plane-y-openspec-chocan-gana-plane.md)
6. **Cada escenario del ticket tiene su test.** Por cada `Sc.` del ticket: `grep -rniE '<clave>' internal --include='*_test.go'`; lo que depende de otro PR queda abierto en `tasks.md`. → [escenarios](2026-11-05-los-escenarios-del-ticket-son-la-lista-de-comprobacion.md)
7. **El rechazo deja rastro, y cabe.** ¿Cada denegación nueva se audita? ¿Contexto desacoplado (`WithoutCancel`)? `grep -n VARCHAR migrations/` contra la longitud del header que escribes. → [auditoría](2026-11-05-la-auditoria-del-intento-y-del-rechazo.md)
8. **Cada rechazo con su `error.code`, `%w` y nunca 500.** `git diff -U0 BASE... -- '*.go' | grep -E '^\+.*(errors\.New|fmt\.Errorf)\(' | grep -v '%w'`; `curl` con un id que no es UUID. → [rechazos](2026-11-05-rechazos-sin-codigo-propio-y-500-donde-toca-4xx.md)
9. **Todo índice nuevo tiene su consulta.** `SET enable_seqscan=off; SET enable_sort=off; EXPLAIN <la consulta>`; sin cast ni `%x%` sobre la columna. → [índices](2026-11-05-un-indice-que-no-atiende-ninguna-consulta.md)
10. **Ids con la forma de la sesión real.** ¿Hay un test con `companyId` numérico (`100234`) y otro mal formado? `grep -n 'uuid.Validate'` antes de llegar al driver. → [ids](2026-11-05-la-forma-real-de-los-ids-de-sesion.md)
11. **El test se pone rojo sin la línea que protege.** Borra el lock, el `Validate`, la auditoría o el log, y corre el test; ¿el fixture trae el caso borde? → [tests](2026-11-05-tests-que-pasan-sin-ejercer-el-defecto.md)
12. **Lock, atomicidad y orden de efectos.** `grep -n 'FOR UPDATE'`: ¿todas las rutas que invalidan la regla toman el mismo? ¿Los rechazos corren antes del proveedor externo? ¿Casos con scope `PRODUCT` y compañía inactiva? → [concurrencia](2026-11-05-el-lock-la-atomicidad-y-el-orden-de-los-efectos.md)
13. **El PR es lo que dice ser.** `git diff --stat BASE...`; `git diff --name-only BASE... | grep -E 'entregas/|\.fixed|\.orig'`; `git cat-file -t <sha de la descripción>`; cada `[x]` de `tasks.md` lo hace el diff; cada diferido tiene tarea. → [alcance](2026-11-05-el-pr-es-lo-que-dice-ser.md)
14. **Nada copiado ni sin llamador.** `grep -rn '<literal o Err nuevo>' internal | grep -v _test`; un símbolo nuevo con un solo uso es de otro PR. → [duplicados](2026-11-05-constantes-copiadas-y-codigo-sin-llamador.md)

Las reglas 5, 6, 7 y 12 no se pueden comprobar con un `grep` solo: son una pregunta que hay que contestar con el ticket abierto.
