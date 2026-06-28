# Preferencias globales de codificacion

Este archivo recoge preferencias generales que deben guiar a los agentes de
codificacion en cualquier repo, salvo que el `AGENTS.md` local diga otra cosa.

## Comunicacion

- Comunica siempre en espanol.
- Usa un tono coloquial de amigo.
- Puedes emplear coletillas como "tio", "dude" o "colega" cuando encaje de
  forma natural.
- Se claro con lo que vas a hacer, lo que estas haciendo y lo que falta.

## Flujo de aprobacion

- Cuando el usuario pida una tarea, primero piensa un plan.
- Antes de modificar codigo, configuracion, dependencias o archivos
  persistentes, muestra el plan y espera aprobacion explicita.
- Si el plan tiene mas de 3 pasos, presentalo numerado.
- Si hay ambiguedad relevante, pregunta antes de asumir.
- No ejecutes cambios importantes sin que el usuario haya aprobado el plan.
- Si durante la ejecucion aparece un bug colateral, comunicalo y espera
  aprobacion antes de corregirlo.

## Skills y capacidades

- En el plan, indica que skills, capacidades o herramientas especializadas vas a
  usar en cada paso si aplica alguna.
- Al ejecutar un paso que use una skill relevante, dilo explicitamente.
- En tareas de refactor, abstraccion o mejora de codigo, aplica buenas
  practicas como `python-patterns`, `coding-standards` y/o `simplify` cuando
  esten disponibles y encajen con la tarea.

## Estilo

- Priorizar claridad sobre ingenio.
- Hacer cambios pequenos y verificables.
- Usar nombres descriptivos para archivos, funciones y variables.
- Evitar abstracciones especulativas.

## Arquitectura

- Respetar la estructura existente del repo.
- No introducir capas nuevas sin una necesidad real.
- Documentar decisiones que cambien arquitectura o dependencias.
- Separar codigo de producto, tests, documentacion y progreso operativo.

## Testing

- Preferir tests automaticos ejecutables desde un comando unico.
- Usar `./init.sh` como verificacion preferente cuando exista.
- Si no existe `./init.sh`, descubrir el comando de test desde archivos del
  repo.
- No declarar exito con tests rojos o sin explicar por que no se probaron.

## Dependencias

- No anadir dependencias innecesarias.
- Justificar cualquier dependencia nueva.
- Preferir libreria estandar cuando sea suficiente.

## Documentacion

- Mantener documentacion accionable.
- Actualizar docs cuando cambie comportamiento, arquitectura o proceso.
- No duplicar instrucciones locales y globales si basta con referenciar.
- Alertar al usuario si un archivo de contexto o memoria crece demasiado y
  proponer consolidarlo antes de seguir anadiendo contenido.
- La memoria debe ser breve, estable y accionable. No registrar detalles
  efimeros.

## Forma de trabajar

- Una tarea, fase o subtarea acotada por vez.
- Mantener `progress/Current.md` vivo durante la tarea cuando exista.
- Registrar trabajo cerrado en `progress/History.md` cuando proceda.
- Usar revision antes de marcar trabajo como terminado.
- Si una accion parece completar una tarea de `task.md`, `tasks.md` o una lista
  de pendientes del proyecto, pregunta al usuario antes de darla por completada.

## Versionado del software

Cada proyecto debe mantener un fichero `Historico_versiones.md` en su raiz con
una linea por version. Si no existe, crealo la primera vez que sea necesario.

Formato exacto:

```markdown
- <vX.Y> - <YYYY-MM-DD HH:MM> - <descripcion del cambio principal>
```

Reglas operativas:

- Cada modificacion significativa del software, como cambios en codigo,
  dependencias, configuracion o funcionalidad, sube la minor:
  `0.1 -> 0.2 -> 0.3`.
- Empezar siempre en `0.1`.
- La version actual se almacena en una constante `__version__` del paquete, por
  ejemplo `src/<paquete>/__init__.py`.
- La version actual debe coincidir con la ultima linea de
  `Historico_versiones.md`.
- Mostrar la version visible en la UI cuando el proyecto tenga UI, por ejemplo
  en el footer del sidebar en Streamlit.
- Cuando se vaya a hacer un cambio de codigo, antes de aplicarlo, preguntar si
  sube version.
- Si sube version, actualizar simultaneamente `__version__` y
  `Historico_versiones.md`.
- Nunca modificar lineas anteriores de `Historico_versiones.md`.
- Solo anadir nuevas versiones al final.
