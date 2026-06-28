# Decisiones globales

Este archivo registra decisiones globales sobre como organizar repos y agentes.

No sustituye a `progress/Decisions.md` de cada repo. Las decisiones de este
archivo aplican al framework global.

## 2026-05-31 - Fuente comun neutral para agentes

- Contexto: los agentes deben poder usarse desde Codex, Claude Code o Devin.
- Decision: los agentes editables viven en `agents/common/*.yaml` y no estan
  escritos para una herramienta concreta.
- Consecuencia: los formatos especificos se regeneran con
  `scripts/generate_agents.py`.

## 2026-05-31 - Separar memoria global y progreso local

- Contexto: hay preferencias reutilizables y tambien estado operativo de cada
  tarea.
- Decision: `memory/` guarda preferencias globales; `progress/` vive en cada
  repo de producto y guarda el estado local.
- Consecuencia: los agentes globales pueden leer preferencias comunes, pero el
  trabajo real se documenta dentro del repo activo.

## 2026-05-31 - Verificacion preferente con init.sh

- Contexto: los repos asistidos por agentes necesitan una forma uniforme de
  verificar.
- Decision: `./init.sh` es el comando preferente cuando exista.
- Consecuencia: si un repo no tiene `init.sh`, el agente debe descubrir el
  comando equivalente en archivos del repo.

## 2026-05-31 - Inyectar AGENTS.md global, checkpoints y memoria en agentes generados (SUPERSEDIDA por 2026-06-01)

- Contexto: los agentes instalados en Codex, Claude Code o Devin no leen
  automaticamente `_contexto_agente_codificador/memory/`.
- Decision: `scripts/generate_agents.py` incrusta
  `_contexto_agente_codificador/AGENTS.md`,
  `_contexto_agente_codificador/CHECKPOINTS.md`,
  `memory/*.md`
  dentro de cada agente generado, antes de las instrucciones especificas del
  rol.
- Consecuencia: para aplicar cambios en la memoria global hay que ejecutar
  `bash scripts/install_agents.sh` o `python scripts/generate_agents.py`.
- Estado: SUPERSEDIDA. Ver entrada `2026-06-01 - Adelgazar agentes generados`.

## 2026-06-01 - Adelgazar agentes generados (slim + reminder + Read lazy)

- Contexto: verificado en sesion nueva que los subagentes de Claude Code y
  Codex heredan el `CLAUDE.md` / `AGENTS.md` global del harness y pueden seguir
  el puntero al framework con `Read`. La inyeccion masiva de `AGENTS.md`,
  `CHECKPOINTS.md` y `memory/*.md` dentro de cada agente generado duplicaba
  ~700 lineas por agente y obligaba a regenerar cada vez que cambiaba
  `memory/`.
- Decision: `scripts/generate_agents.py` ya no inyecta el bloque global. Cada
  agente generado contiene aviso `AUTO-GENERATED`, cabecera con `name` y
  `description`, herramientas mapeadas, un recordatorio corto de donde viven
  las reglas globales y las instrucciones del rol desde
  `agents/common/<agent>.yaml`.
- Consecuencia: los agentes pasan de ~800 a 75-123 lineas. Cambios en
  `memory/*.md` o `AGENTS.md` aplican sin regenerar; solo hace falta regenerar
  cuando cambian los YAML de `agents/common/`. Devin queda con la version
  anterior (fat) por ahora porque no se ha verificado su herencia.

## 2026-05-31 - Sin checkpoints locales en repos de producto

- Contexto: el usuario quiere que todos los repos trabajen igual.
- Decision: los repos de producto no tendran `CHECKPOINTS.md` local; el criterio
  de cierre vive centralizado en `_contexto_agente_codificador/CHECKPOINTS.md`.
- Consecuencia: `_template_repo` no incluye `CHECKPOINTS.md` y los agentes
  generados usan el checkpoint universal inyectado.
