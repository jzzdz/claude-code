# Architecture

This project implements `specs/001-interactive-graph-viewer/plan.md`. The core
constitutional constraint is **layer separation**: everything that can be tested
without mounting Streamlit lives in pure, importable modules; `app.py` only wires
the UI and owns the cache boundary.

## Module boundaries

Data flows in one direction, each layer depending only on the ones above it:

```text
parsing  →  validation  →  graph  →  layout  →  render  →  app (Streamlit)
```

- **`parsing/`** — `python_sources.py` loads the trusted graph/node sources into a
  JSON-compatible payload; `signatures.py` derives deterministic file/directory
  signatures used as cache keys; `errors.py` holds the user-facing error model.
  No knowledge of NetworkX, Plotly, or Streamlit.
- **`validation/`** — `schema.py` validates the payload against the bundled JSON
  Schema (`validation/graph-input.schema.json`); `semantic.py` catches duplicate
  ids, dangling edges, and empty graphs, and trims labels. Returns a
  `ValidationResult` carrying normalized payload plus errors/warnings.
- **`graph/`** — `builder.py` turns a validated payload into a `GraphModel`
  (NetworkX `Graph`/`DiGraph` plus id, label, and neighbor indexes and a content
  signature); `queries.py` provides label search and neighbor lookups; `model.py`
  holds the typed entities (`GraphNode`, `GraphEdge`, `GraphModel`, `LayoutPositions`,
  `RenderGraphData`, `SelectionState`, `SearchState`, `ValidationErrorReport`).
- **`layout/`** — `positions.py` computes a deterministic layout: a circular
  layout for graphs at/above `LAYOUT_LARGE_GRAPH_THRESHOLD`, ForceAtlas2/spring
  otherwise. Output is keyed by a layout signature derived from the model signature.
- **`render/`** — `plotly_renderer.py` builds WebGL-compatible traces and the
  Plotly figure (node `customdata` carries ids; edge level-of-detail caps dense
  graphs via `DENSE_EDGE_CAP`); `selection.py`, `selection_event.py`, `search.py`,
  and `viewport.py` are pure helpers for highlight state, event parsing, search
  state, and axis-range centering.
- **`app.py`** — the only Streamlit-aware module. It owns the cache, session
  state, and the `st.plotly_chart` event wiring.

Tests mirror this layout (`tests/unit/<layer>/…`) so each layer is verified in
isolation; `tests/integration/` covers the end-to-end flows and the 5,000-node
performance gate.

## Cache strategy

`LoadPipelineCache` (in `app.py`) memoizes every expensive stage independently so
Streamlit reruns never recompute unchanged work. Each stage has its own dict keyed
by the most specific signature available:

| Stage | Cache key |
|-------|-----------|
| parse | `SourcePaths.signature` (file + directory content signatures) |
| schema validation | `SourcePaths.signature` |
| semantic validation | `SourcePaths.signature` |
| graph build | `SourcePaths.signature` |
| layout | `GraphModel.signature` |
| render preparation | `LayoutPositions.signature` |

Because layout is keyed by the **model** signature and render by the **layout**
signature, two different source paths that yield the same graph still share
downstream work, and a rerun with unchanged inputs is a pure dictionary lookup.
The pipeline short-circuits on the first stage that produces errors, returning an
empty render with surfaced messages — render never runs on invalid input.

Dependencies are injected through `PipelineDependencies` (defaulting to the real
modules), which lets integration tests assert cache boundaries by counting calls.

## Plotly selection flow

Selection is captured by Streamlit and resolved by pure modules; `app.py` only
moves data between them:

1. `st.plotly_chart(..., on_select="rerun", selection_mode=["points"])` returns an
   event payload on click and triggers a rerun.
2. `selection_event.extract_selected_node_id()` reads the node id from the point's
   `customdata`.
3. The id is stored in `st.session_state["selected_node_id"]`; on the next run
   `update_render_for_selected_node()` calls `selection.build_selection_state()` to
   compute direct neighbors from the NetworkX model.
4. `plotly_renderer.prepare_render_data(..., selection=…)` recolors selected,
   neighbor, and dimmed nodes and rebuilds focused edge segments; `build_figure()`
   produces the new figure.
5. **Clear selection** resets the session id; selecting another node replaces it.

Search follows the same shape: `search.build_search_state()` ranks label matches,
`viewport.py` computes axis ranges to center the active result, and those ranges
ride along in `RenderGraphData.viewport`. No-result searches reuse the previous
viewport so the current view stays stable.
