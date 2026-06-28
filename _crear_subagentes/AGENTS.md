# AGENTS.md - _crear_subagentes

Este repo contiene la herramienta de generacion de subagentes. La fuente de
contexto y las definiciones editables viven fuera, en el repo hermano
`_contexto_agente_codificador`.

## Responsabilidad

- Leer agentes comunes desde `../_contexto_agente_codificador/agents/common/`.
- Transformarlos a los formatos de Claude Code, Codex y Devin.
- Escribir la salida generada en `output/generated_agents/`.
- Instalar los agentes en `~/.claude`, `~/.codex` y `~/.devin` solo tras
  confirmacion explicita del usuario.

Este repo no debe contener memoria global, checkpoints ni definiciones comunes
editables de agentes. Eso pertenece a `_contexto_agente_codificador`.

## Archivos principales

- `scripts/generate_agents.py`: generador real.
- `scripts/install_agents.sh`: envoltorio interactivo de instalacion.
- `output/generated_agents/`: salida regenerable.

No edites a mano los archivos de `output/generated_agents/`; modifica los YAML
en `_contexto_agente_codificador/agents/common/` y regenera.

## Verificacion

Desde la raiz de este repo:

```bash
python scripts/generate_agents.py --output-root output/generated_agents
```

El comando debe leer los YAML del repo hermano y generar 12 archivos: 4 para
Claude Code, 4 para Codex y 4 para Devin.
