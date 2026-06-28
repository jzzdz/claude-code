# Patrones reutilizables

Este archivo documenta patrones globales que pueden repetirse en repos de
producto.

## Estructura minima de repo asistido por agentes

```text
repo/
  AGENTS.md
  task.md o specs/<feature>/tasks.md
  init.sh
  docs/
    architecture.md
    conventions.md
    verification.md
  progress/
    Current.md
    History.md
    Decisions.md
    Blockers.md
  src/
  tests/
```

No todos los repos necesitan todos los archivos desde el primer dia, pero los
agentes deben usarlos si estan presentes.

El cierre de tareas se revisa con el checkpoint universal:

```text
_contexto_agente_codificador/CHECKPOINTS.md
```

Los repos de producto no necesitan `CHECKPOINTS.md` local.

## Flujo leader -> lector -> implementador -> revisor

1. `leader` entiende la peticion y decide el plan.
2. `lector` investiga cuando falta contexto o hay riesgo.
3. `implementador` ejecuta una unica tarea o subtarea.
4. `revisor` valida y emite `APPROVED` o `CHANGES_REQUESTED`.

## Uso de task.md o tasks.md

- Funcionan como backlog local en Markdown.
- Cada tarea pendiente se marca con `- [ ]` y cada tarea completada con
  `- [x]`.
- La tarea o fase activa vive en `progress/Current.md` cuando el repo usa esa
  carpeta.
- Si no hay tarea activa, el agente elige la primera pendiente respetando orden,
  fases y dependencias.
- No marcar `- [x]` sin implementacion, verificacion y documentacion cuando
  proceda.
- Si el usuario da un prompt que no corresponde a una tarea existente, el
  `leader` debe proponer anadirla como pendiente y pedir confirmacion antes de
  implementarla.
- El `implementador` trabaja sobre tareas aceptadas; no inventa backlog por su
  cuenta.

## Uso de CHECKPOINTS.md universal

- `_contexto_agente_codificador/CHECKPOINTS.md` define cuando una tarea puede
  darse por cerrada en cualquier repo.
- Si un repo contiene un `CHECKPOINTS.md` local por motivos historicos, se trata
  como informacion auxiliar; el criterio comun sigue siendo el checkpoint
  universal.

## Arquitectura runtime para productos agentic

Cuando el primer prompt del usuario implique crear un asistente, agente runtime
o producto con prompts, herramientas, LLMs y memoria, el `leader` debe proponer
una tarea inicial para crear una arquitectura runtime clara.

Patron recomendado:

```text
src/
  <package_name>/
    main.py
    graph/
    prompts/
      system_prompt.md
      agents/
      templates/
    memory/
    tools/
    llms/
    utils/
```

Fronteras:

- `src/` contiene producto runtime.
- `prompts/` dentro de `src/` contiene prompts runtime del producto.
- `memory/` dentro de `src/` contiene codigo de gestion de memoria, no memoria
  viva real.
- La memoria viva real vive fuera del repo, por ejemplo
  `~/.<assistant_name>/memory/`.
- Los agentes codificadores globales viven fuera del repo.
- `progress/`, `task.md` o `tasks.md`, `AGENTS.md`, `docs/`, `tests/` e
  `init.sh`
  viven fuera de `src/`.

No crear toda esta estructura si el producto no la necesita. Para CLIs,
librerias o APIs simples, empezar con una estructura minima y crecer segun las
tareas.

## Uso de progress/

- `progress/Current.md`: estado vivo de la sesion.
- `progress/History.md`: trabajo cerrado.
- `progress/Decisions.md`: decisiones tecnicas locales.
- `progress/Blockers.md`: bloqueos activos o resueltos.
- Informes especializados: `progress/lectura_<tema>.md`,
  `progress/impl_<tarea>.md`, `progress/review_<tarea>.md`.

## Uso de init.sh

- `./init.sh` debe ser la verificacion preferente.
- Debe fallar con mensajes claros.
- Debe ejecutar tests o comprobaciones equivalentes.
- Si no existe, el agente debe descubrir comandos en archivos del repo.

## Presupuesto de contexto

- Mantener `AGENTS.md`, checkpoints, memoria y YAML de agentes lo bastante
  compactos para que los agentes puedan leerlos completos.
- Si un archivo de contexto supera los limites orientativos definidos en
  `_contexto_agente_codificador/AGENTS.md`, alertar al usuario.
- Antes de anadir mas contenido a un archivo grande, proponer consolidar:
  correcciones repetidas, decisiones obsoletas o patrones demasiado largos.
