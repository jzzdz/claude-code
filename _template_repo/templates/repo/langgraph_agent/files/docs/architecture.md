# Arquitectura de {{project_name}}

Este repo fue creado desde la template `{{template_id}}`.

## Vista general

La arquitectura inicial separa el runtime del agente en areas pequenas:

- `src/{{package_name}}/main.py`: punto de entrada minimo.
- `src/{{package_name}}/graph/`: estado, nodos, aristas y builder.
- `src/{{package_name}}/prompts/`: prompts del sistema, agentes internos y
  plantillas de salida.
- `src/{{package_name}}/memory/`: carga, escritura y schemas de memoria.
- `src/{{package_name}}/tools/`: registro de tools disponibles.
- `src/{{package_name}}/utils/`: utilidades compartidas.
- `tests/`: tests automaticos.
- `progress/`: memoria operativa del trabajo con agentes.

## Principios

- El bootstrap define limites, no comportamiento profundo.
- El grafo debe poder probarse por piezas.
- Los prompts son artefactos versionados del producto.
- La memoria y las tools deben integrarse mediante interfaces pequenas.
- Documentar cambios de arquitectura antes de cerrar la feature.
