---
id: 2026/10/2026-10-30-la-nota-y-el-contrato-se-revisan-en
type: gotcha
title: La nota y el contrato se revisan en el mismo PR que cambia el código
date: '2026-10-30'
tags:
- coderabbit
- documentacion
- openapi
- spd-80
keywords:
- contrato
- codigo
- apagada
- bandera
- cambia
- notas
- openapi
- responde
abstract: Reglas de negocio documentadas en notas y en el contrato OpenAPI se quedan
  mintiendo en cuanto el código cambia, y el revisor del PR lo abre como hilo.
source: manual
tokens: 185
---

# La nota y el contrato se revisan en el mismo PR que cambia el código

> Cerebro diario · gotcha · 2026-10-30 · manual

Reglas de negocio documentadas en notas y en el contrato OpenAPI se quedan mintiendo en cuanto el código cambia, y el revisor del PR lo abre como hilo. De los 23 hilos que CodeRabbit abrió en los 9 PRs de SPD-80 (30 oct 2026), 9 eran exactamente eso y ninguno era código: 'con la bandera apagada la petición se rechaza' cuando con la bandera apagada la ruta ni se registra; el contrato acepta SMS y la implementación responde 400; 'POST /users siempre responde 503' cuando ya hay una rama 403; estados del OpenAPI que contradicen su propio ejemplo. Es el grupo más numeroso y el más barato de evitar: al cerrar cada PR, releer las notas y el contrato que cita el módulo tocado y corregir el que quedó falso, antes de abrir el PR y no después.
