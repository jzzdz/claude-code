# Python Basic Repo

Template base para crear un proyecto Python sencillo preparado para desarrollo
asistido por agentes.

## Cuando usarla

- El producto necesita un paquete Python minimo.
- No hace falta todavia una arquitectura de agente runtime.
- El objetivo inicial es tener estructura, tests, documentacion y progreso
  local.

## Estructura generada

La template genera:

- `AGENTS.md` con reglas locales para agentes.
- `.gitignore` con ignores genericos de Python y sistema.
- `README.md` de arranque del repo destino.
- `historico_versiones.md` vacio para iniciar el versionado del producto.
- `feature_list.json` inicializado con F000.
- `CHECKPOINTS.md` local complementario.
- `init.sh` como comando unico de verificacion.
- `docs/architecture.md` y `docs/conventions.md`.
- `progress/` con memoria operativa inicial.
- `src/{{package_name}}/` con paquete Python minimo.
- `tests/test_smoke.py` con test de importacion y ejecucion basica.

## Placeholders

- `{{project_name}}`: nombre del repo destino.
- `{{package_name}}`: nombre importable del paquete Python.
- `{{template_id}}`: identificador de template, normalmente `python_basic`.

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
