# _contexto_agente_codificador

`_contexto_agente_codificador` es mi contexto global de agentes de codificacion.
Define una fuente comun para cuatro agentes reutilizables en cualquier
repositorio:

- `leader`
- `lector`
- `implementador`
- `revisor`

El proyecto no contiene codigo de producto ni scripts de generacion. Contiene
definiciones globales, memoria de preferencias, checkpoints y los YAML comunes.
La transformacion a formatos especificos para Codex, Claude Code y Devin vive
en el repo hermano `_crear_subagentes`.

## Para que sirve

- Mantener una unica fuente editable para los agentes.
- Servir como entrada del generador que vive en `_crear_subagentes`.
- Separar reglas globales de contexto local de cada repo.
- Reutilizar el mismo flujo de trabajo en proyectos distintos.

## Conceptos

| Concepto | Que es | Donde vive |
| --- | --- | --- |
| Agentes globales de codificacion | Roles reutilizables: `leader`, `lector`, `implementador`, `revisor`. | `agents/common/*.yaml`. |
| `AGENTS.md` global | Guia del framework global y reglas generales de trabajo. | `_contexto_agente_codificador/AGENTS.md`. |
| `CHECKPOINTS.md` universal | Checklist comun para cerrar features en cualquier repo. | `_contexto_agente_codificador/CHECKPOINTS.md`. |
| `AGENTS.md` local | Guia concreta de un repo de producto. | Raiz de cada repo. |
| Memoria global de codificacion | Preferencias, correcciones, decisiones y patrones reutilizables. | `_contexto_agente_codificador/memory/`. |
| Generador de subagentes | Scripts que transforman los YAML comunes a formatos por herramienta. | `_crear_subagentes/`. |
| `progress/` local | Memoria operativa de una tarea dentro de un repo concreto. | `progress/` del repo de producto. |

## Editar agentes comunes

Edita solo estos archivos:

```text
agents/common/leader.yaml
agents/common/lector.yaml
agents/common/implementador.yaml
agents/common/revisor.yaml
```

Cada YAML debe incluir:

```yaml
name: ...
description: ...
role: ...
tools:
  - ...
instructions: |
  ...
```

Estos YAML son neutrales: no deben estar escritos solo para Claude, Codex o
Devin. El generador transforma esa fuente comun al formato de cada herramienta.

## Editar memoria global

Edita `memory/` para ajustar como quieres que los agentes trabajen con el
tiempo:

- `memory/coding_preferences.md`: preferencias de comunicacion, flujo de
  aprobacion, versionado, testing, dependencias y documentacion.
- `memory/corrections.md`: errores recurrentes que el usuario corrige.
- `memory/decisions.md`: decisiones globales sobre el framework.
- `memory/patterns.md`: patrones reutilizables.

Los agentes generados son ligeros: solo contienen las instrucciones del rol y
un puntero a la memoria y reglas globales. La memoria y `AGENTS.md` se cargan
en tiempo de ejecucion via el `CLAUDE.md` / `AGENTS.md` global del harness, y
si el subagente las necesita las consulta con `Read` desde la ruta del
framework. No hace falta regenerar al cambiar `memory/`; basta con regenerar
cuando cambian los YAML de `agents/common/`.

## Generar agentes

La generacion ya no vive dentro de este repo. El generador esta en
`../_crear_subagentes` y lee por defecto los YAML de
`_contexto_agente_codificador/agents/common/`.

Desde la raiz de `_crear_subagentes`:

```bash
python scripts/generate_agents.py
```

Por defecto genera en una carpeta de inspeccion:

```text
output/generated_agents
```

Tambien puedes lanzar el instalador interactivo:

```bash
bash scripts/install_agents.sh
```

El instalador comprueba que Python existe, genera primero en
`output/generated_agents/`, muestra los archivos y pide confirmacion antes de
copiar nada a `~/.claude`, `~/.codex` o `~/.devin`.

## Destinos generados

Claude Code:

```text
~/.claude/agents/leader.md
~/.claude/agents/lector.md
~/.claude/agents/implementador.md
~/.claude/agents/revisor.md
```

Codex:

```text
~/.codex/agents/leader.toml
~/.codex/agents/lector.toml
~/.codex/agents/implementador.toml
~/.codex/agents/revisor.toml
```

Devin:

```text
~/.devin/agents/leader/AGENT.md
~/.devin/agents/lector/AGENT.md
~/.devin/agents/implementador/AGENT.md
~/.devin/agents/revisor/AGENT.md
```

Todos los archivos generados incluyen este aviso:

```text
AUTO-GENERATED FILE. DO NOT EDIT.
Edit _contexto_agente_codificador/agents/common/<agent>.yaml instead.
```

Cada agente generado contiene, en este orden:

1. Aviso `AUTO-GENERATED`.
2. Cabecera con `name`, `description` y herramientas mapeadas al destino.
3. Recordatorio breve de que las reglas globales viven en
   `_contexto_agente_codificador/AGENTS.md`, `CHECKPOINTS.md` y `memory/*.md`,
   y se cargan via
   `CLAUDE.md` / `AGENTS.md` global del harness.
4. Instrucciones del rol cargadas desde `agents/common/<agent>.yaml`.

El contenido literal de `AGENTS.md`, `CHECKPOINTS.md` y `memory/*` ya no se
inyecta dentro del agente: si el subagente necesita esas reglas, las consulta
con `Read` desde la ruta del framework.

## Como se usa en un repo de producto

1. El repo de producto define su propio `AGENTS.md`.
2. Si existe, el agente usa `feature_list.json` como backlog.
3. Si existe, el agente usa `progress/` como memoria operativa local.
4. Si existe, el agente ejecuta `./init.sh` como verificacion preferente.
5. Si no existe `./init.sh`, busca comandos de test en archivos del repo.
6. El `revisor` aplica `_contexto_agente_codificador/CHECKPOINTS.md` antes de
   aprobar o rechazar.
7. Los repos de producto no necesitan `CHECKPOINTS.md` local.

Este framework global no debe introducir rutas absolutas ni supuestos de un
proyecto concreto.
