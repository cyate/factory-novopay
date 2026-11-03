---
id: 2026/10/2026-10-30-check-then-insert-pierde-la-carrera-y-el
type: gotcha
title: Check-then-insert pierde la carrera y el 23505 no dice lo que parece
date: '2026-10-30'
tags:
- coderabbit
- concurrencia
- idempotencia
- sql
keywords:
- cada
- concurrentes
- mismo
- parte
- pierde
- requisito
- aparecio
- apilados
abstract: Un check-then-act contra la base de datos no es atómico y el mapeo perezoso
  del 23505 miente.
source: manual
tokens: 220
---

# Check-then-insert pierde la carrera y el 23505 no dice lo que parece

> Cerebro diario · gotcha · 2026-10-30 · manual

Un check-then-act contra la base de datos no es atómico y el mapeo perezoso del 23505 miente. En cifra-spend-corporate-api-go (PR 135), personFor hacía findPerson y después insertPerson: dos invitaciones concurrentes para el mismo correo no encuentran fila, la segunda choca con unique_violation y el código devolvía ErrAlreadyAMember, que es una respuesta falsa. Lo mismo apareció en el plan: al partir el requisito de Idempotency-Key entre dos tareas, el reenvío de invitación se quedó sin él, y dos reenvíos concurrentes mandan dos correos. La regla: INSERT ... ON CONFLICT en una sola sentencia en vez de comprobar y luego escribir, y cada violación de unicidad se mapea mirando QUÉ restricción saltó, no cualquiera. Lo que se parte en PRs apilados se parte entero: una garantía que vivía en el requisito común (idempotencia, límite de tasa) se repite en cada trozo o se pierde.
