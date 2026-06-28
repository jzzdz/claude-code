# Research: Interactive Graph Viewer

## Decision: Use Plotly as the Streamlit graph renderer

**Decision**: Use Plotly, rendered through `st.plotly_chart`, with
precomputed NetworkX layout coordinates and WebGL-capable traces for nodes and
edges.

**Rationale**:
- Streamlit has a native Plotly integration. `st.plotly_chart` accepts Plotly
  figures, supports `on_select="rerun"`, and returns point-selection data to
  Python. That directly supports click/select behavior without a custom
  Streamlit component.
- Streamlit documents that Plotly charts with more than 1,000 data points use a
  WebGL renderer, which aligns better with the 5,000-node constitutional gate
  than SVG-only paths.
- Plotly's official network graph example uses NetworkX coordinates and
  separate edge/node traces. This matches the required separation between graph
  model, layout, and render preparation.
- Plotly is actively maintained and broad-purpose. PyPI lists Plotly 6.8.0 as
  released on 2026-06-03, with Python 3.13 classifier support.

**Alternatives considered**:

| Library | Strengths | Risks / trade-offs | Decision |
| --- | --- | --- | --- |
| `streamlit-agraph` | Streamlit-specific API with nodes, edges, config, physics, and a return value. Simple for small demos. | PyPI latest release is 2023-01-28; GitHub shows no releases. README states its NetworkX graph algos are "untested & incomplete". It is based on react-graph-vis/vis-network physics, so 5,000-node browser-side layout risk is high unless physics is disabled. | Reject for initial implementation. Good prototype API, weak maintenance/performance confidence for constitutional gate. |
| PyVis | Built on Vis.js, supports NetworkX import, `neighborhood_highlight`, `select_menu`, physics solvers, and HTML export. | Streamlit integration usually means embedding generated HTML. Streamlit's `st.components.v1.html` is deprecated and renders inside an iframe, making reliable node-click state back into Python awkward. Browser-side physics on 5,000 nodes is a risk. | Reject for initial implementation. Useful export/demo path, but not the best Streamlit state integration. |
| Plotly | Native Streamlit chart API, selection events return to Python, WebGL path for large point sets, maintained, and works with NetworkX coordinates. | Not graph-specific. We must implement adjacency lookup, highlighting, search centering, and edge level-of-detail ourselves. | Choose. Best fit for Streamlit rerun model, testability, and 5,000-node performance gate. |

**Sources**:
- Streamlit `st.plotly_chart`: https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart
- Plotly network graphs: https://plotly.com/python/network-graphs/
- Plotly PyPI: https://pypi.org/project/plotly/
- streamlit-agraph GitHub: https://github.com/ChrisDelClea/streamlit-agraph
- streamlit-agraph PyPI: https://pypi.org/project/streamlit-agraph/
- PyVis docs: https://pyvis.readthedocs.io/en/latest/documentation.html
- PyVis PyPI: https://pypi.org/project/pyvis/
- Streamlit HTML component docs: https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v1.html

## Decision: Use NetworkX as the canonical graph model

**Decision**: Build a NetworkX `Graph` or `DiGraph` after validation, plus
explicit indexes for node ids, labels, neighbors, and render order.

**Rationale**:
- The user requested NetworkX.
- NetworkX provides standard graph types, adjacency lookup, arbitrary node/edge
  attributes, and JSON-serializable conversion utilities.
- The plan does not use NetworkX drawing as the app renderer; NetworkX owns the
  model and graph algorithms, while Plotly owns visualization.

**Alternatives considered**:
- Custom adjacency dictionaries only: lighter, but loses a mature graph API and
  makes later graph queries harder.
- PyVis internal graph model: couples model to rendering and violates layer
  separation.

**Sources**:
- NetworkX introduction: https://networkx.org/documentation/stable/reference/introduction.html
- NetworkX JSON support: https://networkx.org/documentation/stable/reference/readwrite/json_graph.html

## Decision: Use jsonschema for graph payload validation

**Decision**: Use `jsonschema` with Draft 2020-12 schema for structural
validation, followed by a semantic validation pass for constraints JSON Schema
cannot express cleanly, such as unique node ids and dangling edges.

**Rationale**:
- The user requested JSON schema validation using `jsonschema` or Pydantic.
- `jsonschema` directly implements JSON Schema for Python and supports lazy
  iteration over validation errors, which lets the UI show all actionable
  issues instead of one failure at a time.
- The contract is external and JSON-compatible. A JSON Schema file is easier to
  inspect, test, and reuse than Python-only Pydantic models.

**Alternatives considered**:
- Pydantic: strong Python modeling and type coercion, but less direct as a
  standalone JSON Schema contract for this app. It may be useful later for
  internal typed models, but is not needed initially.

**Sources**:
- jsonschema docs: https://python-jsonschema.readthedocs.io/en/stable/
- jsonschema validation API: https://python-jsonschema.readthedocs.io/en/stable/validate/

## Decision: Cache parsing, validated graph construction, layout, and render arrays

**Decision**: Use `st.cache_data` for pure deterministic data results:
source signatures, parsed payloads, validation reports, NetworkX-derived
serializable graph data, layout positions, Plotly-ready node arrays, edge arrays,
and label indexes. Use stable file/directory signatures as cache keys.

**Rationale**:
- Streamlit reruns the app after widget and selection changes. Without caching,
  node click, search, and UI changes could repeat parsing and layout work.
- Streamlit documents `st.cache_data` for data-returning functions and returns
  cached data across reruns. Cached return values must be pickleable, so pure
  dataclasses/dicts/lists are preferred.
- Avoid `st.cache_resource` for mutable graph state; it is for shared resource
  objects/singletons and requires care around thread safety.

**Alternatives considered**:
- No caching: violates performance goal under Streamlit reruns.
- `st.cache_resource` for all graph data: risks shared mutable state and makes
  tests harder.
- Browser-only physics layout cache: couples layout to renderer and makes
  performance less testable.

**Sources**:
- Streamlit `st.cache_data`: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data
- Streamlit `st.cache_resource`: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource

## Decision: Use deterministic NetworkX layout with performance budgets

**Decision**: Implement a pure layout module that starts with NetworkX
`forceatlas2_layout` for readability and exposes a fallback to
`spring_layout(method="energy")` or simpler component packing if the 5,000-node
performance fixture fails. Layout output is cached by graph signature and
layout options.

**Rationale**:
- NetworkX documents `forceatlas2_layout` as a force-directed layout designed
  to visually represent graph structure.
- NetworkX `spring_layout` now has `method="auto"` and uses an energy-based
  optimization for graphs with at least 500 nodes, which is relevant to this
  scale.
- Keeping layout in a pure module makes it benchmarkable and replaceable
  without touching Streamlit or Plotly.

**Alternatives considered**:
- Browser physics layout from PyVis/vis-network: easier visually for small
  graphs, but moves expensive layout work into the browser and is harder to
  test/cache.
- Static circular layout for all graphs: fast, but may not be legible enough
  for real graph inspection.

**Sources**:
- NetworkX `forceatlas2_layout`: https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.forceatlas2_layout.html
- NetworkX `spring_layout`: https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html

## Decision: Apply edge level-of-detail for dense graphs

**Decision**: Render all nodes for search and selection. Render all edges for
representative sparse graphs, but for dense graphs prioritize visible edges
around the selected node/search result and cap background edge segments to keep
pan/zoom usable.

**Rationale**:
- The constitution guarantees usability for at least 5,000 nodes, but does not
  require drawing every edge of an arbitrarily dense graph at full fidelity in
  the initial viewport.
- Rendering millions of edge segments would threaten browser interactivity.
- The local-inspection workflow benefits most from selected-neighborhood edges,
  so detail should concentrate around the user's focus.

**Alternatives considered**:
- Always render every edge: simplest but likely violates performance on dense
  graphs.
- Never render background edges: fastest, but weakens initial graph
  comprehension.

## Decision: TDD with mirrored pure-module tests

**Decision**: Write failing pytest tests before implementation for parsing,
schema validation, semantic validation, graph building, layout positions,
render-data preparation, selection, search, and cache key behavior.

**Rationale**:
- Required by user and constitution.
- The planned module boundaries make isolated tests straightforward and keep
  Streamlit UI tests small.

**Alternatives considered**:
- UI-first tests only: insufficient for parser/layout/render-preparation logic
  and explicitly rejected by the constitution.
