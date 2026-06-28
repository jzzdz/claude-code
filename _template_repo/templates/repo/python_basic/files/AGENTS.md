# AGENTS.md - Guia local para {{project_name}}

Este repo fue creado desde la template `{{template_id}}`.

## Proposito

`{{project_name}}` es un repo de producto preparado para desarrollo asistido por
agentes. Este archivo define el contexto local del repo, no los agentes
globales.

## Orden recomendado de lectura

1. `AGENTS.md`
2. `feature_list.json`
3. `progress/current.md`
4. `docs/architecture.md`
5. `docs/conventions.md`
6. Checkpoint global disponible en el entorno del agente, si existe.

## Flujo de trabajo

- Trabaja sobre una feature concreta de `feature_list.json`.
- Manten `progress/current.md` actualizado durante la sesion.
- Registra decisiones relevantes en `progress/decisions.md`.
- Registra bloqueos activos en `progress/blockers.md`.
- Al cerrar trabajo relevante, resume en `progress/history.md`.
- Ejecuta `./init.sh` antes de entregar cambios.
- No marques una feature como `done` sin verificacion y revision.

## Reglas locales

- No guardes secretos ni credenciales en el repo.
- No introduzcas dependencias sin justificar la decision.
- Actualiza `docs/architecture.md` si cambia la estructura.
- Actualiza `docs/conventions.md` si cambian las reglas de codigo.
- Manten las features pequenas y verificables.
