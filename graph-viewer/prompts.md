usa speckit.constitution parar Define la constitution del proyecto graph-viewer con estos 
principios no negociables:

1. RENDIMIENTO (MUST): el visor debe renderizar e interactuar con grafos de al 
   menos 5.000 nodos sin degradación perceptible (pan/zoom fluido, sin congelar 
   la UI). Cualquier decisión de render debe respetar este límite.

2. STACK (MUST): frontend en . Evitar dependencias pesadas o 
   innecesarias; justificar en el plan cualquier librería nueva.

3. TESTABILIDAD (MUST): la lógica de parsing del input y de layout/render debe 
   ser modular y testeable de forma aislada de la UI. Todo cambio en esa lógica 
   debe acompañarse de tests.

4. SEPARACIÓN DE RESPONSABILIDADES: parsing, modelo de datos del grafo, layout y 
   render son capas distintas y desacopladas.

5. VALIDACIÓN DE ENTRADA (MUST): el input (JSON de nodos/aristas) debe validarse 
   contra un esquema antes de intentar renderizar; los errores se reportan al 
   usuario, no se silencian.


usa  speckit.specify Un visor de grafos interactivo. El usuario carga dos rutas donde están los grafos y los nodos programados en python
yl a aplicación lo renderiza  visualmente.

Comportamiento esperado:

- El usuario especifica la ruta del grafo (\migrafo\migrafo.py) y la ruta donde están los nodos (\misnodos\)
- Una vez cargado, el grafo se muestra con un layout automático legible.
- El usuario puede explorar el grafo: hacer zoom y desplazarse (pan) por él.
- Al seleccionar un nodo, se resaltan ese nodo y sus vecinos directos, para 
  entender sus conexiones.
- El usuario puede buscar un nodo por su etiqueta y la vista lo localiza/centra.
- El visor debe seguir siendo usable con grafos grandes (del orden de miles de 
  nodos), sin congelarse.

Usuarios y motivación: personas que necesitan inspeccionar visualmente la 
estructura de un grafo (relaciones entre entidades) sin escribir código, de forma 
rápida y exploratoria.

Prioridades (para organizar la entrega):
- P1 (MVP): cargar un grafo válido y verlo renderizado con zoom/pan.
- P2: resaltado de vecinos al seleccionar un nodo.
- P3: búsqueda de nodo por etiqueta y centrado.
- Validación de entrada con errores claros: transversal, parte del P1.

Usa la skill speckit-tasks para generar el tasks.md de la feature activa 
(001-interactive-graph-viewer) a partir del plan y la spec.

Asegúrate de que:
- Las tareas respetan el enfoque TDD de la constitution: en cada user story, las 
  tareas de test se escriben y deben fallar antes de las de implementación.
- Las tareas estén organizadas por user story (US1=MVP carga+render, US2=resaltado 
  de vecinos, US3=búsqueda) con rutas de fichero exactas.
- Para el resaltado de vecinos (US2) con Plotly, las tareas bajen al detalle del 
  mecanismo: capturar el evento de selección de st.plotly_chart, calcular los 
  vecinos con networkx, y recolorear/reconstruir la traza. No dejar la tarea como 
  un genérico "implementar resaltado".




  en "'/Users/javierzazo/Library/CloudStorage/GoogleDrive-javizzdz76@gmail.com/Mi unidad/context/Repos/_contexto_agente_codificador'" hay dos archivos que quiero modificar

  AGENTS.md y CHECKPOINTS.md.

  quiero que los adaptes a la forma de trabajar de este repo.

  Es decir, usar task.md en lugar de feature_list.json

y que se siga el proceso del trabajo en :
  o	\progress\
  	Blockers.md = impedimentos abiertos, con fecha
  	Current.md = tarea/fase activa + siguiente paso inmediato
  	Decisions.md = log de decisiones (qué, por qué, alternativas descartadas)
  	History.md = bitácora cronológica de hitos
  
  y que cada vez que hay una versión nueva se resuma en :

  Historico_versiones.md
  

  › quiero que m edigas sin tocar nada, si te pido que use speckit.implementer que proceso segurías, quiero asegurar que lo que te he especificado lo tienes recogido