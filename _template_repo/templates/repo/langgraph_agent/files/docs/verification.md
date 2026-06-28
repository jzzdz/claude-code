# Verificacion de {{project_name}}

- Comando preferente: `./init.sh` (ejecuta los tests con `unittest` sin
  dependencias externas).
- Ejecutar el modulo: `PYTHONPATH=src python3 -m {{package_name}}.main`.
- Los tests del bootstrap no deben requerir servicios externos.
- No declarar trabajo terminado con tests en rojo.
