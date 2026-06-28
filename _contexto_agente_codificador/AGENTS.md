# AGENTS.md - Framework global de agentes de codificacion

> Punto de entrada global para agentes de codigo del workspace. Es un **mapa**:
> lee solo lo necesario cuando lo necesites. El contexto global no es un repo de
> producto y no debe contener logica de aplicaciones concretas.


## 1 Principio principal

Los agentes globales definen como trabajar; cada repo define sobre que trabajar:

- **Agentes globales**: `leader`, `lector`, `implementador` y `revisor`.
  Se definen en `agents/common/*.yaml` y se generan para Codex, Claude Code y
  Devin.
- **Contexto local del repo**: cada repo debe tener su propio `AGENTS.md` y,
  si procede, sus archivos de backlog, progreso, docs y verificacion.

Los agentes globales no deben depender de rutas absolutas de una maquina
concreta. Todas las rutas relativas mencionadas durante una tarea deben
interpretarse desde la raiz del repo activo, salvo que el usuario indique otra
ruta.

## 2 Agentes disponibles

| Agente | Responsabilidad principal |
| --- | --- |
| `leader` | Entender la peticion, descomponer, delegar y coordinar. |
| `lector` | Investigar codigo, docs, arquitectura, riesgos y dependencias. |
| `implementador` | Implementar una unica tarea o subtarea acotada. |
| `revisor` | Revisar cambios y emitir `APPROVED` o `CHANGES_REQUESTED`. |

## 3. Antes de empezar (obligatorio)

Primero identifica el **repo activo**: el directorio desde el que estas
trabajando en esta tarea. Todas las rutas relativas como `src/`, `docs/`,
`task.md`, `progress/Current.md` o `./init.sh` pertenecen al repo activo,
salvo que el usuario indique otra ruta explicitamente.

Despues aplica este arranque:

1. Lee el `AGENTS.md` local del repo activo si existe. Sus instrucciones mandan
   sobre los detalles del repo.
2. Inicializa el entorno con `./init.sh`:
   - Si existe `./init.sh`, ejecutalo antes de tocar codigo.
   - Si no existe y el repo activo es de codigo, copia la plantilla desde
     `../_contexto_agente_codificador/templates/init.sh` (o desde
     `$AGENTS_CONTEXT_DIR/templates/init.sh`) a la raiz del repo, marcala
     ejecutable y ejecutala.
   - `init.sh` primero andamia la estructura minima ausente (idempotente, no
     sobrescribe) y luego verifica entorno, backlog y tests. Si la verificacion
     falla, para y resuelve el entorno antes de modificar archivos.
3. Si existen `task.md` o `tasks.md` y `progress/Current.md`, usalos para
   entender el estado real del trabajo.
4. Si `progress/Current.md` indica una tarea o fase activa, continua esa tarea.
   No elijas una nueva tarea pendiente.
5. Si no hay ninguna tarea activa, elige la primera tarea pendiente respetando
   el orden y dependencias de `task.md` o `tasks.md`.
6. La estructura minima la crea `./init.sh` (paso 2), no la generes a mano:
   `tests/.gitkeep`; `docs/{architecture,conventions,verification}.md`;
   `progress/{Current,History,Decisions,Blockers}.md`. Solo crea archivos a
   mano si no hay `init.sh` ni plantilla accesible, o si el `AGENTS.md` local
   lo contradice.

## 4. Checkpoints para cerrar tareas

`CHECKPOINTS.md` es el checkpoint universal para cerrar tareas en cualquier
repo asistido por estos agentes.

Los repos de producto no necesitan tener un `CHECKPOINTS.md` local. Si existe
un checkpoint local por motivos historicos, se considera informacion auxiliar,
pero el criterio comun de cierre es siempre el checkpoint universal inyectado
desde `_contexto_agente_codificador`.


## 5 Mapa de directorios

Durante una tarea solo hay un **repo activo**: el directorio desde el que trabaja
el agente. Todas las rutas relativas se interpretan ahi. Solo sal a un repo
hermano si el usuario lo pide o un archivo local apunta explicitamente a el.

Prioridad de instrucciones:

1. Sistema o harness.
2. `AGENTS.md` local del repo activo.
3. Este `../_contexto_agente_codificador/AGENTS.md`.
4. Documentacion especifica del repo activo.

Los archivos locales como `AGENTS.md`, `CLAUDE.md` o `GLOBAL.md` pueden ser
punteros al contexto global. No copies ni expandas el contenido global dentro
del repo activo salvo peticion explicita.

Contexto global en `../_contexto_agente_codificador/`:

- `AGENTS.md`: reglas globales, siempre al empezar.
- `CHECKPOINTS.md`: criterios comunes de cierre, antes de declarar terminado.
- `memory/*.md`: preferencias, correcciones, decisiones y patrones globales;
  leer solo cuando afecten a la tarea.

Archivos locales frecuentes del repo activo:

- `task.md` / `tasks.md`: backlog Markdown; `- [ ]` pendiente y `- [x]`
  completado. La tarea activa vive en `progress/Current.md`.
- `progress/Current.md`: tarea/fase activa, estado real y siguiente paso.
- `progress/History.md`: bitacora cronologica de hitos.
- `progress/Decisions.md`: que se decidio, por que y alternativas descartadas.
- `progress/Blockers.md`: impedimentos abiertos o resueltos, con fecha.
- `Historico_versiones.md`: resumen de cada version nueva.
- `progress/Retrospectives.md`: retrospectivas de user story y de cierre de
  feature (siempre append, con fecha).
- `docs/architecture.md`, `docs/conventions.md`, `docs/verification.md`:
  arquitectura, convenciones y verificacion cuando existan.
- `src/` y `tests/`: codigo y tests.

## 6. Reglas duras (no negociables)

- **Una sola tarea o fase a la vez.** Si el repo usa `task.md` o `tasks.md`, no
  mezcles cambios de varias tareas en la misma sesion.
- **No marques una tarea como completada sin pruebas verdes.** Si el repo usa
  backlog, ejecuta `./init.sh` si existe y asegurate de que el bloque de tests
  pasa al 100%.
- **Documenta lo que haces** en `progress/Current.md` mientras trabajas si el
  repo activo tiene ese archivo. No lo dejes para el final.
- **Resume cada version nueva** en `Historico_versiones.md` si el cambio genera
  una version.
- **Deja el repositorio limpio** antes de cerrar la sesión (ver §5).
- **Si no sabes algo, busca en `docs/`** si existe antes de inventarlo.
- **durante la ejecución** especifica siempre las skills que estás usando

## 7. Como elegir una tarea

Aplica esta seccion solo si el repo activo tiene `task.md` o `tasks.md`.

1. Abre `task.md` o el `tasks.md` equivalente. En repos Spec Kit suele estar en
   `specs/<feature>/tasks.md`.
2. Lee `progress/Current.md`. Si identifica una tarea o fase activa no
   completada, continua con ella.
3. Si no hay tarea activa, elige la primera tarea pendiente (`- [ ]`) respetando
   dependencias, fases y orden del archivo.
4. Registra la tarea/fase, hora de inicio, estado y siguiente paso inmediato en
   `progress/Current.md` si el repo usa esa carpeta.
5. No marques `- [x]` hasta que la tarea este implementada, verificada y
   documentada segun proceda.

## 8. Pausa y cierre de trabajo

Aplica esta seccion solo si el repo activo usa `task.md` o `tasks.md` y
`progress/Current.md`. Si no los usa, deja un resumen final claro y ejecuta la
verificacion disponible.

Si paras con la tarea en curso:

1. No marques el checkbox como completado.
2. Actualiza `progress/Current.md` con hecho, pendiente, ultima verificacion y
   siguiente paso inmediato.
3. Si hay impedimento, anotalo en `progress/Blockers.md` con fecha.
4. No vacies `progress/Current.md` ni muevas su contenido a
   `progress/History.md` salvo que haga falta una nota historica adicional.

Si la tarea esta acabada:

1. Ejecuta `./init.sh` o la verificacion equivalente, todo verde.
2. Marca el checkbox como completado en `task.md` o `tasks.md`.
3. Resume el cierre en `progress/History.md`.
4. Deja `progress/Current.md` con plantilla o estado "sin tarea activa".
5. Si hay version nueva, resume la version en `Historico_versiones.md`.
6. Si el cierre completa una **user story** o la **feature** entera (incluida
   Polish), anade una retrospectiva en `progress/Retrospectives.md` (append, con
   fecha) segun las plantillas de `CHECKPOINTS.md` C8.
7. No dejes temporales, `print()` de debug ni TODOs sin contexto.


## 9. Si te bloqueas

- Relee la sección relevante de `docs/`.
- Si la herramienta no hace lo que esperas, **no inventes un workaround**:
  documenta el bloqueo en `progress/Current.md` y `progress/Blockers.md` si
  existen, con fecha, y para la sesion.

## 10. Revision documental tras cambios

Despues de cualquier modificacion relevante, el agente debe revisar si procede
actualizar estos archivos cuando existan en el repo activo:

- `README.md`
- `docs/architecture.md`
- `docs/conventions.md`
- `task.md` o `tasks.md`
- `progress/Current.md`
- `progress/History.md`
- `progress/Decisions.md`
- `progress/Blockers.md`
- `progress/Retrospectives.md`
- `Historico_versiones.md`

No se debe actualizar documentacion por inercia. Si no procede tocar alguno de
estos archivos, el agente debe indicarlo brevemente al cerrar la tarea.


## 11. Memoria global de codificacion

`memory/` contiene preferencias, correcciones, decisiones y patrones globales.
Leelo solo cuando afecte a una decision de implementacion o estilo. Si detectas
una preferencia estable, correccion recurrente o patron reutilizable, propon
registrarlo ahi, pero no modifiques memoria global sin aprobacion del usuario.

Los agentes generados no inyectan esta memoria como texto literal: el harness
propaga `CLAUDE.md` / `AGENTS.md`, y cada subagente lee `memory/*.md` cuando lo
necesita.

## 12. Presupuesto de contexto

Los archivos de contexto deben ser compactos y accionables. Si alguno crece
demasiado, alerta al usuario y propón consolidar antes de acumular mas texto.

Alertas orientativas: `AGENTS.md` 220 lineas; `CHECKPOINTS.md` 160;
`memory/coding_preferences.md` 220; `memory/corrections.md` 150 entradas o 250
lineas; `memory/decisions.md` 120 decisiones o 250 lineas; `memory/patterns.md`
260; `agents/common/*.yaml` 180 por agente.

Consolidar no es borrar sin mas: fusiona correcciones repetidas, mueve reglas
estables a `coding_preferences.md`, resume patrones largos y archiva decisiones
obsoletas solo con aprobacion del usuario.


## 13. Fuente comun de agentes

Los archivos editables a mano son `agents/common/leader.yaml`,
`agents/common/lector.yaml`, `agents/common/implementador.yaml` y
`agents/common/revisor.yaml`.

No edites directamente los agentes generados en `~/.claude/agents/`,
`~/.codex/agents/` o `~/.devin/agents/`. Regenera desde el repo hermano
`_crear_subagentes`, que lee `agents/common/*.yaml` y escribe en
`_crear_subagentes/output/generated_agents/`.
