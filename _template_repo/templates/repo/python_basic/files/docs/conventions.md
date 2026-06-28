# Convenciones de {{project_name}}

## Codigo

- Usar Python estandar salvo que una feature justifique dependencias externas.
- Mantener nombres claros y funciones pequenas.
- Evitar efectos secundarios al importar modulos.
- Colocar codigo de producto en `src/{{package_name}}/`.
- Colocar tests en `tests/`.

## Tests

- `./init.sh` es el comando de verificacion preferente.
- Los tests deben poder ejecutarse sin servicios externos en el bootstrap.
- Cada feature debe anadir o ajustar tests cuando cambie comportamiento.

## Documentacion

- Actualizar `docs/architecture.md` si cambia la estructura.
- Actualizar este archivo si cambian convenciones.
- Usar `progress/` para estado operativo, no para documentacion permanente.
