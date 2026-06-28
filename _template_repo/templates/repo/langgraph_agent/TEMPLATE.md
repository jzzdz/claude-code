# LangGraph Agent Repo

Template base para crear un proyecto de agente preparado para evolucionar a un
runtime basado en LangGraph.

## Cuando usarla

- El producto necesita una arquitectura inicial de agente con grafo, prompts,
  memoria, tools y utilidades separadas.
- Todavia no hace falta implementar comportamiento profundo del agente.
- El objetivo inicial es tener estructura, tests, documentacion y progreso
  local para desarrollo asistido por agentes.

## Estructura generada

La template genera:

- `AGENTS.md` con reglas locales para agentes.
- `.gitignore` con ignores genericos de Python y sistema.
- `README.md` de arranque del repo destino.
- `historico_versiones.md` vacio para iniciar el versionado del producto.
- `feature_list.json` inicializado con F000.
- `init.sh` como comando unico de verificacion.
- `docs/architecture.md` y `docs/conventions.md`.
- `progress/` con memoria operativa inicial.
- `src/{{package_name}}/graph/` con estado, nodos, aristas y builder minimos.
- `src/{{package_name}}/prompts/` con prompts base versionados.
- `src/{{package_name}}/memory/` con stubs de memoria.
- `src/{{package_name}}/tools/` con registro de tools inicial.
- `src/{{package_name}}/utils/` con utilidades compartidas.
- `tests/test_smoke.py` con tests de importacion y runtime minimo.

## Placeholders

- `{{project_name}}`: nombre del repo destino.
- `{{package_name}}`: nombre importable del paquete Python.
- `{{template_id}}`: identificador de template, normalmente `langgraph_agent`.

## Validaciones

El agente debe validar:

- `template_manifest.json` es JSON valido.
- Todos los `required_files` existen bajo `files/`.
- Todos los `required_directories` existen bajo `files/`.
- Los placeholders de rutas y contenidos son coherentes con el manifest.
- Tras generar el repo destino, no quedan placeholders sin sustituir.
- El repo destino conserva `.gitignore`.
- `historico_versiones.md` existe y esta vacio.
- El repo destino se inicializa como repo Git independiente.
- No se generan carpetas `.claude/`, `.codex/` ni `.devin/`.
- `./init.sh` existe, es ejecutable y termina en verde.

## Durante el bootstrap no hacer

- No implementar funcionalidades profundas del producto.
- No anadir dependencias externas por defecto.
- No copiar agentes globales ni carpetas de herramientas.
- No crear configuracion local de herramientas como `.claude/settings.local.json`.
- No usar rutas absolutas ni datos personales.
