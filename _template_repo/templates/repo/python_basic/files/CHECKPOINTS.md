# CHECKPOINTS.md

Checkpoint local complementario para `{{project_name}}`.

Antes de cerrar una feature:

- La feature tiene acceptance clara en `feature_list.json`.
- La implementacion se limita a la feature activa.
- `./init.sh` termina en verde.
- La documentacion afectada esta actualizada.
- `progress/current.md` refleja el estado final.
- No quedan placeholders sin resolver ni datos sensibles.

Si existe un checkpoint global del entorno de agentes, este archivo no lo
sustituye; solo resume validaciones locales del repo.
