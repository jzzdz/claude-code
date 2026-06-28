---
name: bootstrap_repo
description: Use when the user asks to create a new repo, initialize a project, generate a base project structure, or prepare a repository for agent-assisted development from _template_repo templates.
---

# Bootstrap Repo

Usa esta skill para crear el esqueleto inicial de un repo nuevo a partir de una
template de `_template_repo`.

Esta skill crea el continente del repo, no el producto completo. No implementes
funcionalidades de negocio durante el bootstrap.

## Cuando usarla

- El usuario pide crear un nuevo repo.
- El usuario pide inicializar un proyecto.
- El usuario pide generar la estructura base de un proyecto.
- El usuario pide preparar un repo para desarrollo asistido por agentes.

## Flujo

1. Identifica el nombre del nuevo repo.
2. Identifica el tipo de template:
   - `python_basic`
   - `langgraph_agent`
3. Lee `templates/repo/<template_id>/TEMPLATE.md`.
4. Lee `templates/repo/<template_id>/template_manifest.json`.
5. Usa `scripts/bootstrap_repo.py` si existe. Es el camino preferente porque
   copia archivos, sustituye placeholders, valida contra el manifest, omite
   `.DS_Store`, conserva dotfiles requeridos como `.gitignore`, inicializa Git
   en el repo generado, ejecuta la verificacion del repo generado y marca F000
   como `done` solo si la verificacion pasa.
6. Si tienes que hacer el bootstrap manualmente, crea el repo destino como
   hermano de `_template_repo`, salvo que el usuario indique otra ruta.
7. Copia o genera la estructura definida en `templates/repo/<template_id>/files/`.
8. Sustituye estos placeholders en rutas y contenidos:
   - `{{project_name}}`
   - `{{package_name}}`
   - `{{template_id}}`
9. Crea la feature especial `F000 - Bootstrap inicial del repo`.
10. Valida la estructura contra `template_manifest.json`.
11. Crea `historico_versiones.md` vacio si el manifest lo exige.
12. Ejecuta `git init` dentro del repo destino para que sea un repo Git
    independiente, no solo una carpeta dentro de otro repo.
13. No crees `.claude/`, `.codex/` ni `.devin/` dentro del repo destino. Esas
    configuraciones son locales de herramienta y no deben salir de la template.
14. Ejecuta el comando de verificacion definido en `verification_command`.
15. Documenta el resultado en `progress/current.md`.

## Comando preferente

```bash
python3 scripts/bootstrap_repo.py langgraph_agent agente_prueba
```

Opciones utiles:

- `--destination-root <ruta>` para crear el repo en otra carpeta.
- `--package-name <nombre>` si el paquete importable no debe derivarse del repo.
- `--skip-verification` solo cuando no sea posible ejecutar la verificacion en
  ese momento; en ese caso F000 no debe marcarse como `done`.
- `--skip-git-init` solo si el usuario pide explicitamente no inicializar Git.

## Acceptance recomendado para F000

No dupliques manualmente todos los archivos en la acceptance. La validacion debe
apoyarse en `template_manifest.json`.

```text
- Se ha seleccionado la template correcta.
- La estructura generada coincide con la template seleccionada.
- Se cumplen todos los required_files definidos en template_manifest.json.
- Se cumplen todos los required_directories definidos en template_manifest.json.
- .gitignore existe en el repo generado.
- historico_versiones.md existe y queda vacio.
- Todos los placeholders han sido sustituidos correctamente.
- No quedan placeholders sin resolver.
- El repo destino tiene su propio .git inicializado.
- No se genera .claude/, .codex/ ni .devin/ dentro del repo destino.
- feature_list.json queda inicializado.
- progress/ queda inicializado.
- ./init.sh existe, es ejecutable y termina en verde.
- Existe al menos un test smoke y pasa correctamente.
```

## Reglas

- No crear el repo destino dentro de `_template_repo`.
- No copiar `.DS_Store`, `__pycache__` ni otros artefactos locales.
- No omitir dotfiles declarados en el manifest, especialmente `.gitignore`.
- No reescribir `AGENTS.md`, `CLAUDE.md`, `GLOBAL.md` ni otros punteros al
  contexto global. Deben copiarse desde la template y solo se sustituyen los
  placeholders declarados.
- No copiar agentes globales ni carpetas `.codex/`, `.claude/` o `.devin/`.
- No crear permisos de herramienta con rutas absolutas o rutas relativas rotas.
  Si una herramienta necesita permisos locales, se configuran fuera de la
  template y deben apuntar al contexto global como `../_contexto_agente_codificador/`.
- No introducir rutas absolutas de la maquina del usuario en archivos generados.
- No guardar datos personales, secretos ni memoria viva en la template.
- Si falta informacion no critica, usa una convencion razonable y documentala
  en `progress/current.md`.
