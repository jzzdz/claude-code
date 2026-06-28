# Arquitectura de {{project_name}}

Este repo fue creado desde la template `{{template_id}}`.

## Vista general

La arquitectura inicial es deliberadamente pequena:

- `src/{{package_name}}/`: paquete Python principal.
- `src/{{package_name}}/main.py`: punto de entrada minimo.
- `tests/`: tests automaticos.
- `docs/`: documentacion tecnica local.
- `progress/`: memoria operativa del trabajo con agentes.

## Principios

- Mantener el bootstrap ligero.
- Anadir modulos solo cuando una feature lo necesite.
- Preferir funciones pequenas, importables y faciles de probar.
- Documentar cambios de arquitectura antes de cerrar la feature.
