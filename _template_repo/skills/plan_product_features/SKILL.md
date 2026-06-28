---
name: plan_product_features
description: Use after bootstrapping a repo or when the user describes a complex product that must be turned into epics and granular features in feature_list.json without implementing the whole product.
---

# Plan Product Features

Usa esta skill para convertir una idea de producto en una epica y features
granulares dentro del `feature_list.json` del repo destino.

Esta skill crea el plan de producto, no ejecuta todo el producto.

## Cuando usarla

- Despues de crear un repo con `bootstrap_repo`.
- Cuando el usuario describa un producto complejo.
- Cuando el `leader` necesite preparar trabajo delegable para el
  `implementador`.

## Flujo

1. Lee el `AGENTS.md` del repo destino.
2. Lee `docs/architecture.md`.
3. Lee `docs/conventions.md`.
4. Lee `feature_list.json`.
5. Crea una epica inicial, por ejemplo:

```text
EPIC-001 - Construccion inicial del producto
```

6. Divide la epica en features pequenas y ejecutables.
7. Cada feature debe seguir esta forma:

```json
{
  "id": "F001",
  "epic": "EPIC-001",
  "name": "...",
  "status": "pending",
  "description": "...",
  "acceptance": [
    "..."
  ]
}
```

8. Actualiza `feature_list.json`.
9. Actualiza `progress/current.md` con:
   - epica creada;
   - features creadas;
   - proxima feature recomendada;
   - decisiones pendientes;
   - riesgos o bloqueos.
10. Deja preparada la siguiente feature para que el `leader` pueda delegarla al
    `implementador`.

## Granularidad

No crees features gigantes como:

- "crear todo el agente";
- "implementar todo LangGraph";
- "hacer todo el producto".

Prefiere features pequenas. Para un agente LangGraph, una division razonable
puede ser:

```text
F001 - Definir estado base del grafo
F002 - Crear builder base del grafo
F003 - Crear router simple/complejo
F004 - Crear nodo planner
F005 - Crear nodo executor
F006 - Crear nodo reviewer
F007 - Crear aristas condicionales
F008 - Cargar system_prompt.md
F009 - Cargar prompts internos
F010 - Crear memory loader
F011 - Crear memory writer
F012 - Crear tool registry
F013 - Integrar tools en executor
F014 - Crear tests unitarios del grafo
F015 - Crear test end-to-end minimo
```

## Reglas

- No implementes todas las features durante la planificacion.
- No marques como `done` features que todavia no han sido implementadas y
  verificadas.
- Manten F000 como bootstrap historico y empieza features de producto desde
  F001.
- Si la idea de producto es ambigua, documenta decisiones pendientes en
  `progress/current.md` y prepara una primera feature que reduzca incertidumbre.
