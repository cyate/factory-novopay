---
id: 2026/10/2026-10-30-el-efecto-externo-va-despues-de-la-autorizacion
type: gotcha
title: El efecto externo va después de la autorización, no antes
date: '2026-10-30'
tags:
- autorizacion
- coderabbit
- efectos-externos
- go
- spd-80
keywords:
- ahi
- autorizacion
- caso
- cuenta
- despues
- efecto
- externo
- orden
abstract: Un efecto externo irreversible —crear la cuenta en el proveedor de identidad,
  mandar el correo— no puede ejecutarse antes de las comprobaciones que pueden rechazar
  la petición.
source: manual
tokens: 218
---

# El efecto externo va después de la autorización, no antes

> Cerebro diario · gotcha · 2026-10-30 · manual

Un efecto externo irreversible —crear la cuenta en el proveedor de identidad, mandar el correo— no puede ejecutarse antes de las comprobaciones que pueden rechazar la petición. En cifra-spend-corporate-api-go (PR 136 y 137, SPD-80), service.InviteUser llama a Inviter.Invite y solo después comprueba delegación, rol y borrado: un 403 ROLE_EXCEEDS_CALLER_ACCESS deja una cuenta huérfana en el IdP y ninguna membresía. El comentario del código justifica el orden para el caso de FALLO del proveedor, que es otro caso: ahí sí conviene que vaya primero. La regla que sale de ahí: las validaciones baratas y las de autorización van antes de cualquier llamada externa; el orden proveedor-primero se queda solo para la escritura. Si no se puede, el contrato del adaptador lleva compensación. CodeRabbit lo abrió tres veces en dos PRs: era un solo defecto visto desde tres sitios.
