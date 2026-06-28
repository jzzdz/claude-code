# Convenciones de {{project_name}}

## Codigo

- Usar Python estandar en el bootstrap.
- Mantener efectos secundarios fuera de imports.
- Colocar definiciones del grafo en `src/{{package_name}}/graph/`.
- Colocar prompts en `src/{{package_name}}/prompts/`.
- Colocar memoria en `src/{{package_name}}/memory/`.
- Colocar tools en `src/{{package_name}}/tools/`.
- Colocar tests en `tests/`.

## Prompts

- Los prompts deben tener un proposito claro.
- Evitar datos personales o secretos.
- Mantener plantillas pequenas y reutilizables.

## Tests

- `./init.sh` es el comando de verificacion preferente.
- Los tests del bootstrap no deben requerir servicios externos.
- Cada feature debe anadir o ajustar tests cuando cambie comportamiento.

## Documentacion

- Actualizar `docs/architecture.md` si cambia el grafo o sus limites.
- Actualizar este archivo si cambian convenciones.
- Usar `progress/` para estado operativo, no para documentacion permanente.
