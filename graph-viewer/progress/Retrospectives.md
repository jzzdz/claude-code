# Retrospectives

## 2026-06-27 — User Story 1: Cargar y explorar un grafo válido (MVP, P1)

**Alcance cubierto**: fase Setup (`T001`-`T004`), fase Foundational (`T005`-`T009`)
e implementación del MVP de US1 (`T010`-`T031`): entrada de rutas, validación,
modelo de grafo, layout automático, render Plotly inicial, pan/zoom y caché.

### Qué salió según lo previsto

- **Disciplina TDD completa**: los tests `T010`-`T019` se escribieron primero y se
  confirmó el estado rojo (`History`, 20:36 CEST) antes de implementar `T020`-`T031`.
  Al cierre del MVP la suite pasaba en verde (20:53 CEST).
- **Arquitectura por capas puras**: parsing, validación, modelo de grafo, layout y
  preparación de render quedaron como módulos importables, con `app.py` limitado al
  cableado de Streamlit y los límites de caché, tal como exigía la constitución y se
  fijó en la decisión de las 20:20 CEST. La estructura `src/graph_viewer/**` coincide
  con la planificada en `plan.md`.
- **Cobertura de los criterios de aceptación**: carga válida, bloqueo ante entradas
  inválidas, límites de caché y preparación de render de 5.000 nodos quedaron
  cubiertos por tests de integración (`T017`-`T019`).
- **Fixtures deterministas como base**: el trabajo previo de fixtures (`T005`-`T008`)
  permitió escribir los tests de US1 sin fricción y sostener el resto de historias.

### Qué se desvió del plan y por qué

- **Estrategia de layout**: el plan (`T027`) preveía "ForceAtlas2 primero y spring como
  fallback". La implementación añadió un **layout circular determinista** para grafos
  por encima del umbral de grafo grande, reservando ForceAtlas2/spring para los
  pequeños (`layout/positions.py`). Motivo: la puerta de rendimiento de 5.000 nodos de
  la constitución; los layouts force-directed de NetworkX eran demasiado lentos a esa
  escala sin añadir dependencias (decisión 20:45 CEST).
- **Versión de Python**: el plan declaraba `Python 3.12+`; se ajustó `pyproject.toml`
  a `>=3.11`. Motivo: el único runtime mantenido disponible era `python311_neo_env`, y
  la suite de US1 pasaba en 3.11 (decisión 21:10 CEST). Es una desviación de la
  «Technical Context» del plan, no de una tarea concreta.
- **Apoyo con subagente**: se incorporó un subagente con rol `implementador` como
  revisor de solo lectura de riesgo/cobertura, manteniendo todas las escrituras en el
  hilo principal (decisión 20:20 CEST). No estaba en `tasks.md`; surgió a petición del
  usuario y para evitar conflictos en `tasks.md`/`progress/`.

### Decisiones tomadas sobre la marcha y su impacto

- **Layout circular determinista para grafos grandes**: desbloqueó la puerta de
  rendimiento sin nuevas dependencias y mantuvo el resultado reproducible (clave para
  tests). Impacto: el MVP cumple el presupuesto de 5.000 nodos; coste: dos caminos de
  layout que mantener y un layout menos "orgánico" en grafos grandes.
- **Aceptar runtime Python 3.11**: desbloqueó la instalación editable y la ejecución
  local de Streamlit. Impacto positivo inmediato; queda como caveat la paridad con
  3.12 documentada en `Blockers`.
- **Centralizar escrituras en el hilo principal + subagente de revisión**: evitó
  conflictos en archivos interdependientes durante el TDD inicial, a costa de no
  paralelizar la edición de código.

### Impedimentos encontrados y cómo se resolvieron

- **Discordancia de runtime (Python 3.12 no disponible, `python3` = 3.11)**: no
  bloqueó los tests (`python3 -m pytest` funcionaba); se resolvió bajando el requisito
  de `pyproject.toml` a `>=3.11` y verificando instalación + suite en
  `python311_neo_env` (Blockers 20:36 → 21:12 CEST).
- **Streamlit ausente / `pip install -e '.[dev]'` fallando por metadata `>=3.12`**: se
  resolvió con el entorno `python311_neo_env` aportado por el usuario (Streamlit
  1.56.0) y el ajuste de metadata (Blockers 21:01 → 21:08 CEST).
- **`PermissionError: Operation not permitted` al abrir el socket de Streamlit**:
  primer arranque del servidor local falló en el sandbox; se resolvió reintentando con
  el permiso de servidor local aprobado (Blockers 21:14 CEST).

### Aprendizajes para las siguientes user stories

- **Fijar el runtime real al inicio**: validar la versión de Python y la presencia de
  Streamlit antes de planificar evita un caveat arrastrado; conviene reflejar el
  entorno efectivo (`python311_neo_env`) en la documentación de setup (pendiente en
  `T051`).
- **Las puertas de rendimiento condicionan el diseño, no solo la validación**: el
  umbral de 5.000 nodos forzó la elección de layout; conviene anticipar estrategias de
  nivel de detalle (también para aristas) como decisión de diseño temprana, no como
  ajuste posterior.
- **Permisos del sandbox para servidores locales**: anticipar la aprobación del
  servidor local ahorra un ciclo de fallo en futuras verificaciones manuales de la app.
- **La inversión en fixtures deterministas rinde**: tenerlos listos en Foundational
  aceleró US1 y, después, US2 y US3; mantener ese patrón para nuevas historias.
- **Mantener la lógica fuera de Streamlit es replicable**: el límite "puro vs UI" que
  funcionó en US1 se reutilizó tal cual en US2 (selección) y US3 (viewport); seguir
  formalizándolo en contratos.

---

## 2026-06-27 — User Story 2: Resaltar vecinos directos (P2)

**Alcance cubierto**: tests y MVP de US2 (`T032`-`T041`): captura del evento de
selección de Plotly, cálculo de vecinos directos sobre el `GraphModel` de US1, y
recoloreado/reconstrucción de trazas para nodo seleccionado, vecinos, nodos
atenuados y aristas enfocadas, más el comportamiento de limpiar/reemplazar selección.

### Qué salió según lo previsto

- **TDD respetado**: los tests `T032`-`T035` se escribieron y confirmaron en rojo
  (`Historico`, 21:38 CEST) antes de implementar `T036`-`T041`; al cierre la suite
  completa quedó verde con 33 tests (`History`, 21:46 CEST).
- **Reutilización limpia de US1**: la selección se apoyó en el índice de vecinos del
  `GraphModel` y en los `customdata` con ids de nodo que el render de US1 ya emitía,
  exactamente como anticipaba la dependencia US2→US1 del `plan.md`. No hubo que tocar
  el modelo de grafo.
- **Lógica de selección fuera de Streamlit**: el parseo del evento, el estado de nodo
  seleccionado, el cálculo de vecinos y el recoloreado quedaron en módulos puros;
  `app.py` solo guarda `session_state` y pasa el payload del evento (decisión 21:32
  CEST). Esto permitió testear simulando el payload de `st.plotly_chart` sin montar
  Streamlit.
- **Limpiar/reemplazar selección** (`T040`) implementado: seleccionar otro nodo
  sustituye la selección y existe acción explícita de "Clear selection".

### Qué se desvió del plan y por qué

- **Módulo `selection_event.py` separado**: el árbol de estructura de `plan.md` solo
  preveía `render/selection.py` (y `viewport.py`) para US2. La implementación separó el
  parseo del payload del evento (`selection_event.py`) del cálculo de estado/vecinos
  (`selection.py`). Las `tasks.md` ya lo anticipaban en `T036`, así que es una
  desviación respecto al diagrama del plan, no respecto a las tareas. Motivo: aislar la
  forma del evento de Streamlit/Plotly hace ese parseo testeable por separado de la
  lógica de grafo.
- **Render de aristas enfocadas más rico de lo mínimo**: además de atenuar lo no
  relacionado, se recolorearon aristas seleccionadas y se reconstruyeron "segmentos de
  arista enfocados" (`Historico`, 21:46 CEST), yendo algo más allá del resaltado
  estrictamente requerido para mejorar la legibilidad del vecindario.

### Decisiones tomadas sobre la marcha y su impacto

- **Mantener toda la selección en módulos puros** (21:32 CEST): impacto positivo en
  testabilidad (payloads simulados, sin runtime Streamlit) y alineamiento con el
  render-interaction contract; coste menor de indirección al pasar el evento por
  `session_state`. Rechazado calcular vecinos en `app.py` por acoplar reruns de UI a la
  lógica de grafo.
- **Migración de API de ancho de Streamlit**: durante la validación de US2 se sustituyó
  el `use_container_width` deprecado por `width="stretch"` y se revalidó la suite (33
  tests, 21:49 CEST). Impacto: elimina el warning de deprecación y prepara la UI para
  versiones futuras de Streamlit; coste casi nulo.

### Impedimentos encontrados y cómo se resolvieron

- **Sin bloqueantes formales**: `Blockers` 21:46 CEST registra "US2 blockers: none";
  tests y suite completa pasaban en `python311_neo_env`.
- **Fricción real: deprecación de la API de ancho de Streamlit**: el único roce fue el
  `use_container_width` deprecado, detectado al validar US2 y resuelto migrando a
  `width="stretch"` con revalidación inmediata de la suite (21:49 CEST).

### Aprendizajes para las siguientes user stories

- **El límite puro/UI de US1 amortiza de inmediato**: poder simular el payload de
  `st.plotly_chart` sin Streamlit hizo US2 rápida de testear; conviene mantener el
  parseo de eventos en su propio módulo y no mezclarlo con la lógica de grafo.
- **Diseñar el render pensando en la interacción futura paga**: los `customdata` con
  ids definidos en US1 fueron el habilitador directo de la selección; merece la pena
  fijar esos contratos de render con la interacción en mente desde el principio.
- **Presupuestar mantenimiento por deprecaciones del framework**: Streamlit evoluciona
  rápido; conviene revisar warnings de deprecación en cada validación y absorber esos
  pequeños cambios en el momento, no acumularlos. Este patrón ya se reaplicó en US3.

---

## 2026-06-27 — User Story 3: Buscar y centrar un nodo por etiqueta (P3)

**Alcance cubierto**: tests y MVP de US3 (`T042`-`T050`): búsqueda por etiqueta
(exacta-primero y parcial) sobre el índice de etiquetas del `GraphModel`, `SearchState`
con orden de resultados y mensajes, selección entre múltiples coincidencias, centrado
de la vista por rangos de ejes y estabilidad de viewport en búsquedas sin resultado.

### Qué salió según lo previsto

- **TDD respetado**: los tests `T042`-`T045` se confirmaron en rojo (4 errores de
  import por módulos US3 aún inexistentes, `Current` 22:06 CEST) antes de implementar
  `T046`-`T050`; al cierre la rebanada US3 pasó 12 tests y la suite completa quedó verde
  con 45 tests (`Current`/`History`, 22:13 CEST).
- **Centrado como rangos de ejes en módulo puro**: el centrado se calculó en
  `render/viewport.py` y se almacenó en `RenderGraphData.viewport`, aplicándose a los
  ejes de Plotly en `build_figure()` (decisión 22:01 CEST), tal como describía el árbol
  de `plan.md` para `viewport.py`. Testeable sin Streamlit.
- **Comportamiento de búsqueda completo**: búsqueda exacta-primero y parcial, orden de
  coincidencias, selección entre múltiples matches vía `selectbox`, y mensajes de
  no-resultado, cubriendo el "Independent Test" de US3.
- **Reutilización del andamiaje previo**: US3 se apoyó en el índice de etiquetas del
  `GraphModel`, las posiciones de layout y el estado de app de US1, y pudo desarrollarse
  en paralelo a US2 tras el MVP, como anticipaba la dependencia del `plan.md`.

### Qué se desvió del plan y por qué

- **Módulo `render/search.py` adicional**: el árbol de estructura de `plan.md` no
  incluía un módulo de estado de búsqueda en `render/` (solo `plotly_renderer.py`,
  `selection.py`, `viewport.py`). La implementación separó la **consulta de etiquetas**
  en la capa de grafo (`graph/queries.py`, sí previsto) del **estado de búsqueda de
  cara a UI** (`render/search.py`: orden, nodo activo, mensajes de no-resultado). Las
  `tasks.md` ya lo anticipaban en `T047`. Motivo: mantener limpio el corte entre
  consulta pura y estado presentacional.
- **Preservación explícita del viewport previo en no-resultado**: la estabilidad de la
  vista se implementó pasando el `viewport` anterior cuando la búsqueda no tiene nodo
  activo (`active_node_id is None`), en lugar de recalcular o resetear ejes. Es un
  mecanismo concreto no detallado en el plan, derivado del requisito de "no
  desestabilizar la vista actual".

### Decisiones tomadas sobre la marcha y su impacto

- **Representar el centrado como rangos de ejes en `RenderGraphData.viewport`** (22:01
  CEST): impacto positivo en testabilidad (sin Streamlit) y robustez bajo reruns; coste
  de hilar el `viewport` a través de los datos de render y reaplicar el anterior en
  no-resultado. Rechazadas las APIs imperativas de cámara de Plotly/Streamlit desde
  `app.py` por ser menos testeables y más frágiles ante reruns.

### Impedimentos encontrados y cómo se resolvieron

- **Sin impedimentos**: `Blockers` 22:13 CEST registra "US3 blockers: none"; tests y
  suite completa pasaron a la primera en `python311_neo_env`. Fue la entrega más limpia
  de las tres historias: no hubo fricción de entorno ni de API porque el andamiaje
  (fixtures, módulos puros, caché, contratos) ya estaba maduro.

### Aprendizajes para las siguientes user stories

- **Estado declarativo > llamadas imperativas de UI**: representar el estado de vista
  (rangos de ejes) como datos que fluyen por la preparación de render pura fue clave
  para testear el centrado y sobrevivir reruns; generalizable a cualquier estado visual
  futuro.
- **Separar "consulta pura" de "estado de cara a UI" escala bien**: dividir la búsqueda
  entre `graph/queries.py` y `render/search.py` mantuvo ambas capas testeables; conviene
  repetir ese patrón cuando una feature mezcla lógica de dominio y estado presentacional.
- **La inversión inicial compone**: que una historia P3 aterrizara con cero bloqueantes
  confirma que el esfuerzo en fixtures, capas puras, caché y contratos de US1/US2 reduce
  drásticamente el coste de las historias posteriores.
- **Codificar la estabilidad de UX como contrato explícito**: la preservación de
  viewport en no-resultado es un requisito de estabilidad que merece quedar como
  comportamiento contractual y test dedicado, no como efecto colateral.

---

## 2026-06-27 — RETRO DE CIERRE — feature 001-interactive-graph-viewer

Feature completa: 55/55 tareas en `[X]` (Setup, Foundational, US1, US2, US3 y
Polish `T051`-`T055`), versión `0.1.0`, suite de 45 tests verde en
`python311_neo_env`. Esta retro no repite las de US1/US2/US3; las sintetiza y se
centra en lo que solo se ve con la feature terminada.

### Síntesis de las retros US1/US2/US3: patrones comunes

- **El límite "lógica pura, UI solo en `app.py`" fue el eje de todo**: nacido en US1,
  habilitó directamente US2 (simular el payload de `st.plotly_chart` sin Streamlit) y
  US3 (centrado como rangos de ejes en módulo puro). Es el patrón con más palanca de
  toda la feature.
- **TDD rojo→verde en las tres historias, sin excepción**: `T010`-`T019`, `T032`-`T035`
  y `T042`-`T045` se confirmaron en rojo antes de implementar. Nunca se invirtió el orden.
- **Estado de vista como datos declarativos**: ids en `customdata` (US2) y rangos de
  ejes en `RenderGraphData.viewport` (US3) — la misma idea de representar la interacción
  como datos que fluyen por el render puro, en vez de llamadas imperativas a la UI.
- **Desviación recurrente idéntica**: cada historia añadió un módulo de `render/` que el
  árbol de `plan.md` no listaba pero que `tasks.md` sí anticipaba (`selection_event.py`
  en US2, `search.py` en US3). El diagrama del plan quedó sistemáticamente por detrás de
  las tareas; la implementación siguió `tasks.md`.
- **Fricción decreciente**: US1 acumuló casi todos los impedimentos (entorno), US2 tuvo
  uno (deprecación), US3 cero. La inversión en fixtures/contratos/caché/módulos puros
  compuso a lo largo de la feature.

### Cumplimiento global de la constitution

Matiz de conteo: la `constitution.md` define **5 Core Principles** (I, II, III, V con la
etiqueta `(MUST)` explícita; IV "Layered Graph Architecture" con cláusulas MUST en el
cuerpo) más una sección de **Quality Gates** que incluye el gate de facto de TDD. Evalúo
los cinco principios de punta a punta más el gate de TDD que cita la petición:

- **I — Rendimiento como frontera de producto (5.000 nodos)**: ✅ de punta a punta. El
  plan definió un check medible; `test_5000_node_fixture_prepares_within_budget` pasa
  ~0.03s frente a 5.0s; el layout circular determinista se eligió documentando el
  tradeoff (Decisions 20:45) para preservar la cota, y `DENSE_EDGE_CAP` cubre grafos
  densos. `T055` confirmó que no hacía falta tuning.
- **II — Stack frontend mínimo (Streamlit) + disciplina de dependencias**: ✅. Streamlit
  confinado a `app.py`; Plotly integrado vía `st.plotly_chart` nativo (no componente
  custom, así que no cuenta como dependencia pesada nueva); todas las dependencias
  justificadas en `plan.md` con alternativa más ligera descartada.
- **III — Testabilidad aislada**: ✅. Las cinco capas se testean sin montar UI; 45 tests,
  los unit mirror de cada módulo, y selección/búsqueda/viewport verificadas con payloads
  simulados.
- **IV — Arquitectura por capas**: ✅. Dependencia unidireccional; el render no parsea
  input crudo ni muta el modelo canónico; ninguna capa depende de la UI. Los módulos
  extra (`selection_event.py`, `search.py`) se añadieron **dentro** de los límites de capa.
- **V — Validación de entrada schema-first**: ✅. JSON Schema + validación semántica
  bloquean el render; la pipeline hace short-circuit en el primer error y emite mensajes
  accionables; cubierto por fixtures inválidas.
- **Gate de TDD / quality gates**: ✅. TDD en cada historia, check de rendimiento
  reproducible, y reporte de errores de usuario cubierto por tests.

**Salvedad honesta**: el cambio de runtime Python 3.12→3.11 fue una desviación de la
*Technical Context* del `plan.md`, **no** una violación de la constitution (que no fija
versión de Python). Quedó documentada en Decisions/Blockers. Cumplimiento constitucional:
limpio de punta a punta.

### Evaluación de la decisión arquitectónica central (Plotly)

Vista con todo terminado, **fue acertada**. Las tres capacidades que sostienen las tres
historias mapearon de forma natural a Plotly sobre `st.plotly_chart`:

- Eventos de selección nativos (`on_select="rerun"`, `selection_mode=["points"]`) →
  US2 sin componente custom.
- Trazas WebGL + `customdata` con ids → identidad de nodo para selección y rendimiento a
  5.000 nodos.
- Rangos de ejes declarativos → centrado de US3 testeable y robusto bajo reruns.

**Coste acumulado real** (modesto y localizado):
- Maquinaria de nivel de detalle de aristas (`DENSE_EDGE_CAP`) para densos — añade
  complejidad, pero ni siquiera hubo que tunearla (`T055`).
- Hilar el `viewport` por `RenderGraphData` y reaplicar el anterior en no-resultado —
  fontanería derivada del modelo declarativo de figura de Plotly bajo reruns de Streamlit.
- Superficie de mantenimiento por acoplamiento a la forma del payload (`selection_event.py`)
  y por churn de APIs (la deprecación de `use_container_width`).

Veredicto: el beneficio (cero componentes custom, las 3 US encajan, cota de rendimiento
cumplida) superó con holgura un coste que se concentró en un par de módulos puros
dedicados, algo de plumbing de viewport y una migración de API. **No se materializó
ningún riesgo de rendimiento** que obligara a replantear el renderer.

### Impedimentos recurrentes a nivel de feature

- **Desajuste de entorno/runtime (dominante y front-loaded)**: Python 3.12 no disponible,
  Streamlit ausente, `pip install` fallando por metadata, y `PermissionError` del socket.
  Causa raíz: el plan asumió un runtime (3.12) que no era el entorno mantenido real
  (`python311_neo_env`). Todos se concentraron en US1 y se resolvieron alineando la
  metadata a 3.11. Fue el mayor lastre de la feature, y fue ambiental, no arquitectónico.
- **Churn de APIs del framework**: deprecación de `use_container_width` → `width="stretch"`.
  Riesgo recurrente de bajo grado, absorbido en el momento.
- **Diagrama de `plan.md` por detrás de `tasks.md`**: fricción menor pero repetida en las
  tres historias (módulos no listados en el árbol del plan).

### Aprendizajes para futuras features y proyectos (qué llevar a la siguiente constitution/plan)

- **Fijar y verificar el runtime ANTES de planificar**: añadir un gate explícito —"el
  runtime declarado debe estar instalado y la suite verde en él antes de Phase 0"—
  habría eliminado casi todos los bloqueantes de US1. Es el cambio de mayor retorno.
- **`tasks.md` como mapa de módulos autoritativo** (o mantener el árbol de `plan.md`
  sincronizado): el diagrama del plan se quedó corto las tres veces.
- **Elevar "estado de vista como dato declarativo" a contrato**: `customdata` y rangos de
  ejes fueron un patrón reutilizable para cualquier renderer interactivo; merece quedar
  documentado, no redescubierto por historia.
- **El límite puro/UI es la regla de mayor palanca**: ya vive en los principios III/IV;
  conviene reafirmarlo porque fue el motor real de testabilidad y de la fricción
  decreciente.
- **Presupuestar mantenimiento por deprecaciones del framework** en cada pase de validación.
- **Las tareas de polish condicionales necesitan un gate medible**: el test de 5.000 nodos
  convirtió "no hace falta tuning" (`T055`) en una decisión documentada y defendible, no
  en una corazonada. Replicar ese patrón de "polish guiado por medición".
- **La inversión foundational compone**: la curva de fricción US1→US3 (muchos → uno →
  cero bloqueantes) es la mejor evidencia para defender ese gasto inicial en la próxima
  feature.
