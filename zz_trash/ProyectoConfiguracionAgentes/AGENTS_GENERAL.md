# AGENTS_GENERAL.md

Este fichero guía al agente de codificación cuando trabaja en este repositorio.

## Comunicación

- Siempre en español.
- Tono coloquial de amigo. Puedes emplear coletillas como "tío", "dude" o "colega".

## Cómo trabajar

- Cuando te pida algo, no ejecutes sin preguntar.
- Cuando te pida algo, primero planifica, segundo muéstrame el plan y solo si te digo que ejecutes, ejecuta.
- Cuando te pida algo, dime qué skills invocas para hacerlo.
- Si identificas que con alguna acción hemos completado una tarea de la lista de todos de cada proyecto, preguntame si la das por completada

## COMENTARIOS PARA EL DESARROLLO


### Versionado del software

Cada proyecto debe mantener un fichero `historico_versiones.md` en su raíz con una línea por versión. Si no existe crealo la primera vez que lo necesites.

Formato exacto:

~~~markdown
- <vX.Y> - <YYYY-MM-DD HH:MM> - <descripción del cambio principal>
~~~

Reglas operativas:

- Cada modificación significativa del software, como cambios en código, dependencias, configuración o funcionalidad, sube la minor: `0.1 -> 0.2 -> 0.3...`
- Empezar siempre en `0.1`.
- La versión actual se almacena en una constante `__version__` del paquete, por ejemplo `src/<paquete>/__init__.py`.
- La versión actual debe coincidir con la última línea de `historico_versiones.md`.
- Mostrar la versión visible en la UI cuando el proyecto tenga UI, por ejemplo en el footer del sidebar en Streamlit.
- Cuando vaya a hacer un cambio de código, antes de aplicarlo, preguntar si sube versión.
- Si sube versión, actualizar simultáneamente `__version__` y `historico_versiones.md`.
- Nunca modificar líneas anteriores de `historico_versiones.md`.
- Solo añadir nuevas versiones al final.

### Comunicar bugs antes de corregirlos
Si durante la ejecución de un paso se detecta un bug colateral, comunicarlo y esperar aprobación antes de corregirlo. No actuar unilateralmente aunque sea obvio.

### Indicar skills en el plan
En el plan paso a paso, indicar qué skill se usaría en cada paso (si aplica alguna). Al ejecutar cada paso, indicarlo explícitamente antes de usar la skill.

### Pedir aprobación antes de actuar
SIEMPRE presentar el plan y esperar aprobación antes de codificar. Esto incluye correcciones de bugs detectados durante la ejecución.

### Flujo de trabajo obligatorio
- SIEMPRE piensa un plan antes de ejecutar cualquier tarea.
- SIEMPRE explícame el plan paso a paso y espera mi aprobación antes de empezar a codificar.
- Si el plan tiene más de 3 pasos, preséntalos numerados.
- Si detectas ambigüedad en lo que te pido, pregúntame antes de asumir.
- Si durante la ejecución de un paso detectas un bug o problema colateral, comunícamelo y espera aprobación antes de corregirlo.
- En el plan, indica qué skill usarías en cada paso (si aplica alguna).
- Al ejecutar cada paso, indica explícitamente qué skill estás usando antes de usarla.
- En tareas de refactor, abstracción o mejora de código, aplicar siempre las skills de buenas prácticas: `python-patterns`, `coding-standards` y/o `simplify` según corresponda.


