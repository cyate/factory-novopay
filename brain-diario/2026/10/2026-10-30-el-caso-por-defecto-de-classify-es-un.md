---
id: 2026/10/2026-10-30-el-caso-por-defecto-de-classify-es-un
type: pattern
title: El caso por defecto de classify() es un defecto propio, no una caída
date: '2026-10-30'
tags:
- coderabbit
- errores
- go
- http
- observabilidad
keywords:
- defecto
- classify
- caso
- pgerror
- propio
- salia
- vez
- 5xx
abstract: Una función classify() que mapea 'todo lo que no reconozco' a error de transporte
  convierte defectos propios en caídas de infraestructura.
source: manual
tokens: 208
---

# El caso por defecto de classify() es un defecto propio, no una caída

> Cerebro diario · pattern · 2026-10-30 · manual

Una función classify() que mapea 'todo lo que no reconozco' a error de transporte convierte defectos propios en caídas de infraestructura. En cifra-spend-corporate-api-go (PR 131), classify trataba como ErrUnreachable todo lo que no fuera PgError ni context.Canceled: un fallo de rows.Scan (desajuste de tipos o columnas, deriva de esquema) salía como 503 USER_DIRECTORY_UNAVAILABLE en vez de 500, y un cursor con fecha inválida provocaba un PgError 22007 que salía como 5xx en vez de 400. Efecto en pruebas: QA ve 503 intermitentes y culpa a la base de datos; las alertas de disponibilidad se ensucian con entradas malformadas del cliente. La regla: el caso por defecto de una clasificación de errores es 'defecto propio' (500), nunca 'el otro lado se cayó'; la indisponibilidad se reconoce por una señal positiva, no por descarte.
