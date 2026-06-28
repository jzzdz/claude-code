# Bitácora de prompts — Spec Kit / graph-viewer

Registro cronológico de los prompts usados para construir el visor de grafos
(`001-interactive-graph-viewer`) con Spec Kit, agente **Codex** (skills-based) +
Claude Code, sobre un proyecto **full Python / Streamlit / TDD**.

> Nota de invocación:
> - **Codex** (skills-based): los comandos NO son slash literales. Se piden en
>   lenguaje natural — *"Usa la skill speckit-<fase> ..."*.
> - **Claude Code**: los mismos comandos sí funcionan como slash — `/speckit.<fase> ...`.

---

##  El mapeo conceptual de Jira

| Spec Kit | Jira | Qué es |
|---|---|---|
| Feature, la spec entera, (specs/001-.../) | Epic | El gran bloque de trabajo: tu visor de grafos completo |
| User Story (US1, US2, US3) | Story | Una funcionalidad entregable e independiente |
| Tarea (T001, T002…) | Sub-task | Unidad concreta de trabajo dentro de una story |
| Prioridad (P1, P2, P3) | Priority / orden de backlog | Qué va primero |



## 0. Setup del proyecto

```
specify init graph-viewer --integration codex --script sh
# (integración de Claude añadida después, conviviendo sobre las mismas specs)
```

Resultado: estructura `.specify/`, integración Codex (`.agents/skills/`),
context file `AGENTS.md`, constitution copiada de plantilla, scripts sh.

---

## 1. Constitution

```
Define la constitution del proyecto graph-viewer con estos principios no negociables:

1. STACK (MUST): aplicación full Python con frontend en Streamlit. La UI se
   construye con componentes de Streamlit; no se introduce frontend custom en
   JS/TS. Cualquier librería de visualización de grafos nueva debe justificarse
   en el plan.

2. RENDIMIENTO (MUST): el visor debe manejar grafos de al menos 5.000 nodos de
   forma usable. Dado el modelo de reejecución de Streamlit, todo cálculo costoso
   (parsing, layout) debe cachearse adecuadamente (st.cache_data /
   st.cache_resource) para no recomputarse en cada interacción.

3. TEST-FIRST / TDD (MUST): se sigue desarrollo dirigido por tests. Para toda
   lógica nueva, los tests se escriben primero, se confirma que fallan (fase Red),
   y solo entonces se implementa hasta que pasan (fase Green). No se escribe código
   de implementación antes de tener tests que definan su comportamiento.

4. TESTABILIDAD (MUST): la lógica de parsing del input y de construcción/layout
   del grafo debe vivir en módulos Python puros, independientes de Streamlit, y
   ser testeable de forma aislada con pytest. La capa de Streamlit es solo
   presentación.

5. SEPARACIÓN DE RESPONSABILIDADES: parsing, modelo de datos del grafo, layout y
   capa de presentación (Streamlit) son módulos distintos y desacoplados. La
   lógica de negocio no debe depender de Streamlit.

6. VALIDACIÓN DE ENTRADA (MUST): el input (JSON de nodos/aristas) debe validarse
   contra un esquema antes de renderizar; los errores se muestran al usuario en
   la UI, no se silencian.
```

Genera `.specify/memory/constitution.md` y propaga checks a spec/plan/tasks.

---

## 2. Specify (el *qué*, sin tecnología)

```
Un visor de grafos interactivo. El usuario carga un fichero con la descripción de
un grafo (nodos y aristas) y la aplicación lo renderiza visualmente para que pueda
explorarlo.

Comportamiento esperado:

- El usuario puede cargar un grafo desde un fichero. Si el fichero es inválido o
  está mal formado, se le muestra un mensaje de error claro en lugar de fallar
  silenciosamente.
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
```

Crea la feature `001-interactive-graph-viewer` y `specs/.../spec.md`.

---

## 3. Plan (el *cómo*) — opción "que investigue la librería"

```
Aplicación full Python con Streamlit, siguiendo la constitution.

Quiero que en research.md evalúes y recomiendes la librería de visualización de
grafos más adecuada para Streamlit que cumpla: (a) interactividad —clic en nodo
con resaltado de vecinos— y (b) rendimiento usable con ~5.000 nodos. Compara al
menos streamlit-agraph, pyvis y Plotly, con sus trade-offs, y justifica la
elección.

El resto del stack: networkx para el modelo del grafo, validación de JSON de
entrada con esquema (jsonschema o pydantic), pytest para tests.

Estructura en módulos Python puros desacoplados de Streamlit (parsing, graph,
layout, app de presentación), con tests espejo. Cachear parsing y layout para
respetar el rendimiento bajo el modelo de reejecución de Streamlit. Asumir TDD.
```

Genera `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.
**Decisión de research resultante:** Plotly (sobre streamlit-agraph y PyVis), por
integración nativa con Streamlit, eventos de selección vía `st.plotly_chart`, y
ruta WebGL para volúmenes grandes.

---

## 4. Tasks (desglose ejecutable, reforzado en US2)

```
Genera el tasks.md de la feature activa (001-interactive-graph-viewer) a partir
del plan y la spec.

Asegúrate de que:
- Las tareas respetan el enfoque TDD de la constitution: en cada user story, las
  tareas de test se escriben y deben fallar antes de las de implementación.
- Las tareas estén organizadas por user story (US1=MVP carga+render, US2=resaltado
  de vecinos, US3=búsqueda) con rutas de fichero exactas.
- Para el resaltado de vecinos (US2) con Plotly, las tareas bajen al detalle del
  mecanismo: capturar el evento de selección de st.plotly_chart, calcular los
  vecinos con networkx, y recolorear/reconstruir la traza. No dejar la tarea como
  un genérico "implementar resaltado".
```

**Resultado:** 55 tareas — US1: 22, US2: 10, US3: 9, Setup/foundational/polish: 14.

---

## 5. (Opcional, recomendado) Analyze — gate de cobertura

```
Verifica la consistencia y cobertura entre la constitution, la spec, el plan y el
tasks.md de la feature activa. Reporta gaps de cobertura y cualquier
inconsistencia, sin modificar ficheros.
```

Read-only. Detecta requisitos sin tareas, tareas huérfanas, y violaciones de
principios MUST de la constitution.

---

## 6. Implement — POR FASES (Setup + Foundational + US1)

```
Implementa la feature activa (001-interactive-graph-viewer), SOLO las fases de
Setup, Foundational y User Story 1 (MVP: carga + render con zoom/pan). NO
implementes US2 ni US3 todavía.

Respeta el enfoque TDD de la constitution: tests primero (deben fallar), luego
implementación hasta que pasen. Marca cada tarea como [X] en tasks.md.

Mantén actualizado el sistema progress/ definido en AGENTS.md durante todo el
trabajo:
- Current.md: actualiza al empezar y al cerrar cada fase/tarea relevante (tarea
  activa + siguiente paso inmediato).
- Blockers.md: registra cualquier impedimento con fecha; márcalo resuelto sin
  borrar el histórico.
- Decisions.md: ante cualquier decisión técnica no trivial, añade entrada (qué,
  por qué, alternativas descartadas, fecha).
- History.md: una línea por hito completado (fase cerrada, US entregada), con fecha.
- Historico_versiones.md: registra el versionado conforme avances.
Estos ficheros son append-mostly: añade, no reescribas el histórico.

Al terminar US1, párate, actualiza progress/ y reporta qué se implementó y cómo
arrancar la app para validarla.
```

Validar tras US1: `streamlit run ...` (carga + render con zoom/pan), `pytest`
(parser y modelo pasan), y que la lógica esté desacoplada de Streamlit.

### 6.1 Retrospectiva US1

Genera una retrospectiva de la User Story 1 . Apóyate en 

progress/Decisions.md, progress/History.md y progress/Blockers.md, y en el diff 

entre lo planeado (plan.md/tasks.md) y lo realmente implementado. Estructura:

- Qué salió según lo previsto

- Qué se desvió del plan y por qué

- Decisiones tomadas sobre la marcha y su impacto

- Impedimentos encontrados y cómo se resolvieron

- Aprendizajes para las siguientes user stories

Escribe el resultado en progress/Retrospectivas.md (append, con fecha).
---


## 7. Implement — POR FASES (US2 - resaltado de vecinos)


Usa la skill speckit-implement para implementar la User Story 2 (resaltado de 
vecinos) de la feature activa (001-interactive-graph-viewer). Las fases de Setup, 
Foundational y US1 ya están completas y validadas — NO las re-implementes.

Respeta el TDD de la constitution: tests primero (deben fallar), luego 
implementación hasta que pasen. Marca cada tarea como [X] en tasks.md.

Atención al mecanismo de Plotly: capturar el evento de selección de 
st.plotly_chart, extraer el customdata, calcular los vecinos directos con el 
GraphModel/networkx, y recolorear/reconstruir las trazas. Mantén la lógica de 
cálculo de vecinos en módulos Python puros, fuera de la capa Streamlit.

Mantén actualizado el sistema progress/ definido en AGENTS.md (Current.md, 
Blockers.md, Decisions.md, History.md, Historico_versiones.md), append-mostly.

Al terminar US2, párate, actualiza progress/ y reporta qué se implementó y cómo 
validar el resaltado antes de seguir con US3.


Prompt para US3 (búsqueda + centrado)
Usa la skill speckit-implement para implementar la User Story 3 (búsqueda de nodo 
por etiqueta y centrado) de la feature activa. Setup, Foundational, US1 y US2 ya 
están completas y validadas — NO las re-implementes.

Respeta el TDD: tests primero (deben fallar), luego implementación. Marca cada 
tarea como [X] en tasks.md. Mantén progress/ actualizado (append-mostly).

Al terminar US3, párate, actualiza progress/ y reporta.
Y al final: Polish
Quedan las tareas de Setup/foundational/polish (14 en total); las de polish son las transversales de cierre. Cuando US1-US3 estén entregadas y validadas:
Usa la skill speckit-implement para completar las tareas restantes de Polish y 
cross-cutting de la feature activa. Respeta el TDD. Marca cada tarea como [X]. 
Actualiza progress/ y el Historico_versiones.md con el cierre de la feature.


### 7.1 Retrospectiva US2

Genera una retrospectiva de la User Story 2 . Apóyate en 

progress/Decisions.md, progress/History.md y progress/Blockers.md, y en el diff 

entre lo planeado (plan.md/tasks.md) y lo realmente implementado. Estructura:

- Qué salió según lo previsto

- Qué se desvió del plan y por qué

- Decisiones tomadas sobre la marcha y su impacto

- Impedimentos encontrados y cómo se resolvieron

- Aprendizajes para las siguientes user stories

Escribe el resultado en progress/Retrospectivas.md (append, con fecha).
---

## 8. Implement — POR FASES (US3 - búsqueda + centrado)
Usa la skill speckit-implement para implementar la User Story 3 (búsqueda de nodo 
por etiqueta y centrado) de la feature activa. Setup, Foundational, US1 y US2 ya 
están completas y validadas — NO las re-implementes.

Respeta el TDD: tests primero (deben fallar), luego implementación. Marca cada 
tarea como [X] en tasks.md. Mantén progress/ actualizado (append-mostly).

Al terminar US3, párate, actualiza progress/ y reporta.


### 8.1 Retrospectiva US3

Genera una retrospectiva de la User Story 3 . Apóyate en 

progress/Decisions.md, progress/History.md y progress/Blockers.md, y en el diff 

entre lo planeado (plan.md/tasks.md) y lo realmente implementado. Estructura:

- Qué salió según lo previsto

- Qué se desvió del plan y por qué

- Decisiones tomadas sobre la marcha y su impacto

- Impedimentos encontrados y cómo se resolvieron

- Aprendizajes para las siguientes user stories

Escribe el resultado en progress/Retrospectivas.md (append, con fecha).
---

## 8. Implement — Y al final: Polish
Quedan las tareas de Setup/foundational/polish (14 en total); las de polish son las transversales de cierre. 

Usa la skill speckit-implement para completar las tareas restantes de Polish y 
cross-cutting de la feature activa. Respeta el TDD. Marca cada tarea como [X]. 
Actualiza progress/ y el Historico_versiones.md con el cierre de la feature.

### 8.1 Restrospectiva polish

Genera la retrospectiva final de cierre de la feature 001-interactive-graph-viewer,
ahora que Polish está completo. Ya existen retrospectivas por user story en 
progress/Retrospectivas.md — NO las repitas; sintetízalas y céntrate en lo que 
solo es visible con la feature completa.

Apóyate en: las retros de US ya escritas, todo el progress/ (Decisions.md, 
History.md, Blockers.md, Historico_versiones.md) y el contraste entre 
constitution.md, plan.md y lo realmente implementado.

Estructura:
- Síntesis de las retros de US1/US2/US3: patrones comunes y aprendizajes que se 
  repitieron a lo largo de la feature
- Cumplimiento global de la constitution: ¿se respetaron los 6 principios MUST de 
  punta a punta? (TDD, rendimiento 5.000 nodos, desacople de Streamlit, validación)
- Evaluación de la decisión arquitectónica central (Plotly): vista con todo 
  terminado, ¿fue acertada? ¿coste acumulado real?
- Impedimentos recurrentes a nivel de feature
- Aprendizajes para futuras features y proyectos (qué llevarme a la siguiente 
  constitution/plan)
Escribe el resultado en progress/Retrospectivas.md (append, con fecha, marcado 
como "RETRO DE CIERRE — feature 001").


## Sistema progress/ (definido en AGENTS.md)

| Fichero | Contenido |
|---|---|
| `Blockers.md` | Impedimentos abiertos, con fecha |
| `Current.md` | Tarea/fase activa + siguiente paso inmediato |
| `Decisions.md` | Log de decisiones (qué, por qué, alternativas descartadas) |
| `History.md` | Bitácora cronológica de hitos |
| `Historico_versiones.md` | Versionado del proyecto |

**Pendiente de robustez:** está en `AGENTS.md` global. Para que sea fiable en este
proyecto, conviene (a) duplicarlo en el `AGENTS.md` del proyecto fuera de los
marcadores `SPECKIT START/END`, o (b) subirlo a la constitution como principio
MUST (lo lee `implement` siempre y lo trata como gate), o (c) un hook
`after_implement`.

---

## Notas de proceso

- **Codex es skills-based**: los `/speckit.*` no son slash nativos; se invocan por
  lenguaje natural ("Usa la skill speckit-...") o como `/speckit-<fase>`.
- **Codex y Claude Code conviven** sobre las mismas specs (árboles `.agents/` y
  `.claude/` separados, context files `AGENTS.md` vs `CLAUDE.md`).
- **No se creó rama git** por feature (sin hook de git / repo no inicializado);
  todo va sobre la rama actual.
- **Implement por fases** para no saturar el contexto del agente: Setup →
  Foundational → US1 (validar) → US2 → US3 → Polish.
- **Punto frágil:** el resaltado de vecinos (US2) con Plotly no es nativo; requiere
  capturar evento + calcular vecinos con networkx + recolorear traza. Quedó
  detallado en tasks.

