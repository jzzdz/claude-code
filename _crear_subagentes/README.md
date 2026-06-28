# _crear_subagentes

`_crear_subagentes` transforma los agentes comunes definidos en
`../_contexto_agente_codificador/agents/common/` a los formatos de Claude Code,
Codex y Devin.

El repo de contexto conserva las reglas, checkpoints, memoria y YAML editables.
Este repo contiene solo la logica de generacion e instalacion.

## Estructura

| Ruta | Uso |
| --- | --- |
| `scripts/generate_agents.py` | Genera los agentes para cada herramienta. |
| `scripts/install_agents.sh` | Genera en `output/` y pide confirmacion antes de instalar. |
| `modelos.json` | Define los modelos usados al generar agentes de Claude y Codex. |
| `output/generated_agents/` | Salida regenerable para revisar los agentes antes de instalarlos. |

## Generar agentes

Desde la raiz de este repo:

```bash
python scripts/generate_agents.py
```

Por defecto lee:

```text
../_contexto_agente_codificador/agents/common/
```

Y escribe:

```text
output/generated_agents/
```

Tambien puedes indicar rutas explicitas:

```bash
python scripts/generate_agents.py \
  --common-dir ../_contexto_agente_codificador/agents/common \
  --output-root output/generated_agents
```

## Configurar modelos

`modelos.json` define un modelo por defecto y overrides por agente para Claude
Code y Codex:

```json
{
  "claude": {
    "default": "claude-sonnet-4-6",
    "agents": {
      "leader": "claude-opus-4-7"
    }
  },
  "codex": {
    "default": "gpt-5.4",
    "agents": {
      "leader": "gpt-5.5"
    }
  }
}
```

El generador lee ese archivo por defecto. Tambien puedes indicar otro:

```bash
python scripts/generate_agents.py --models-file ruta/a/modelos.json
```

## Instalar agentes

```bash
bash scripts/install_agents.sh
```

El instalador:

1. Comprueba que Python esta disponible.
2. Regenera `output/generated_agents/`.
3. Muestra los archivos que se instalarian.
4. Pide confirmacion antes de copiar a `~/.claude`, `~/.codex` y `~/.devin`.

Si respondes que no, no modifica las carpetas finales.
