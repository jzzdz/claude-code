# AGENTS.md - Guia local para `_template_repo`

`_template_repo` es una plantilla de plantillas, no un repo de producto final.
Los agentes codificadores deben mantenerlo generico y reutilizable.

## Reglas principales

- No crear funcionalidades de negocio dentro de `_template_repo`.
- No convertir este repo en un producto concreto.
- Mantener las templates genericas, copiables y sin datos personales.
- No copiar aqui agentes globales de Codex, Claude, Devin u otras herramientas.
- No crear carpetas `.codex/`, `.claude/` ni `.devin/`.
- No usar rutas absolutas de una maquina concreta en archivos generados.
- No guardar memoria viva, secretos, tokens ni datos personales en templates.
- Usar placeholders como `{{project_name}}`, `{{package_name}}` y
  `{{template_id}}` cuando un dato dependa del repo destino.
- Planificar antes de actuar y pedir autorización al usuario para salir
- Especificar siempre la skill que se va a usar

## Rutas importantes

| Ruta | Uso |
| --- | --- |
| `skills/` | Skills reutilizables para agentes. |
| `templates/repo/` | Templates para crear repos destino. |
| `templates/repo/<template_id>/files/` | Archivos que se copian o generan en el repo destino. |

## Mantenimiento de skills

- Cada skill debe tener un unico `SKILL.md` con frontmatter `name` y
  `description`.
- Las skills deben describir procedimientos accionables, no planes historicos.
- No anadir documentacion auxiliar dentro de una skill si `SKILL.md` basta.

