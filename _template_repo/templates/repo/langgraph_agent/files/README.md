# {{project_name}}

Repo de agente creado desde la template `{{template_id}}`.

## Uso rapido

```bash
./init.sh
```

El script ejecuta los tests con `unittest` sin instalar dependencias externas.

## Ejecutar el modulo

```bash
PYTHONPATH=src python3 -m {{package_name}}.main
```

## Estructura

```text
{{project_name}}/
  .gitignore
  AGENTS.md
  README.md
  feature_list.json
  init.sh
  docs/
  progress/
  src/
    {{package_name}}/
      graph/
      prompts/
      memory/
      tools/
      utils/
  tests/
```

## Trabajo con agentes

Lee `AGENTS.md` antes de modificar el repo. Usa `feature_list.json` como
backlog local y `progress/` como memoria operativa.
