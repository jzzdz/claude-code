# Implementation Plan: Interactive Graph Viewer

**Branch**: `001-interactive-graph-viewer` | **Date**: 2026-06-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-interactive-graph-viewer/spec.md`

## Summary

Build a full-Python Streamlit graph viewer. Users provide a graph Python file
path and a node Python directory path; pure Python parsing modules extract a
JSON-compatible graph payload, validate it against a JSON Schema, build a
NetworkX graph model, compute/cache a layout, and render an interactive Plotly
WebGL view inside Streamlit. The viewer supports pan/zoom in MVP, selected-node
neighbor highlighting in P2, and label search/centering in P3.

The implementation follows TDD and keeps parsing, validation, graph model,
layout, render preparation, and Streamlit presentation as separate layers.

## Technical Context

**Language/Version**: Python 3.12+

**Frontend Stack**: Streamlit

**Primary Dependencies**: Streamlit, NetworkX, Plotly, jsonschema, pytest

**New Dependency Justification**:
- **Streamlit**: Required by constitution as the frontend shell.
- **NetworkX**: Required by user for canonical graph model and adjacency
  queries.
- **Plotly**: Recommended visualization library after research. Native
  `st.plotly_chart` integration supports selection events and WebGL rendering
  paths for large point sets without adding a custom Streamlit component.
- **jsonschema**: Chosen over Pydantic for the external JSON-compatible graph
  payload contract because it validates directly against JSON Schema and can
  report all validation errors for user-facing feedback.
- **pytest**: Required for TDD and isolated tests of parsing, validation,
  graph, layout, render-preparation, and app-level smoke behavior.

**Storage**: Local filesystem input paths only; no database. Streamlit
in-process cache stores parsed payloads, validated graph models, layout
positions, and render-prepared arrays keyed by file path metadata and content
signatures.

**Testing**: pytest; unit tests mirror each pure module, plus integration tests
for source path loading, validation errors, layout/render preparation, and
5,000-node performance fixture.

**Target Platform**: Local Streamlit web app in a desktop browser.

**Project Type**: Single Python application with modular library code and a
Streamlit presentation entry point.

**Performance Goals**:
- Load and render small valid graphs within 5 seconds.
- Keep pan/zoom responsive for a 5,000-node graph with representative sparse
  edges.
- Resolve exact-label search and center the view within 2 seconds.
- Avoid recomputing parsing and layout on Streamlit reruns when inputs are
  unchanged.

**Constraints**:
- Validate graph payload before rendering.
- Do not execute untrusted Python sources; this app assumes local/trusted graph
  and node files supplied by the user.
- Parsing, validation, graph model, layout, render preparation, and Streamlit UI
  remain separate importable modules.
- Cache expensive parse/layout/render-preparation work under Streamlit's rerun
  model.
- Dense graphs may require level-of-detail rendering for edges while keeping
  all nodes searchable and selectable.

**Scale/Scope**:
- MVP handles valid graph loading, schema validation, automatic layout, and
  pan/zoom.
- P2 adds selected-node neighbor highlighting.
- P3 adds label search and centering.
- Performance gate targets at least 5,000 nodes and a representative sparse
  edge set; very dense graphs are handled with edge visibility strategies so
  the UI remains usable.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Stack clarity**: PASS. Frontend stack is Streamlit. Plotly is justified as
  the renderer integrated through Streamlit's native chart API, not a custom
  component.
- **Performance**: PASS. Plan includes a reproducible 5,000-node fixture,
  cached parsing/layout, WebGL-backed rendering, and edge level-of-detail for
  dense graphs.
- **Dependency discipline**: PASS. All new dependencies are listed above with
  purpose and alternatives researched in [research.md](./research.md).
- **Testability**: PASS. Core logic is split into pure modules with mirrored
  pytest coverage.
- **Layer boundaries**: PASS. Parsing, validation, graph model, layout,
  render preparation, and Streamlit UI are separate layers with contracts.
- **Input validation**: PASS. Graph and node data are validated against
  [graph-input.schema.json](./contracts/graph-input.schema.json) before render;
  errors are surfaced to users.

## Project Structure

### Documentation (this feature)

```text
specs/001-interactive-graph-viewer/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── graph-input.schema.json
│   ├── python-source-contract.md
│   └── render-interaction-contract.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/
└── graph_viewer/
    ├── __init__.py
    ├── app.py                         # Streamlit presentation only
    ├── parsing/
    │   ├── __init__.py
    │   ├── python_sources.py          # path checks + trusted Python source extraction
    │   ├── signatures.py              # file/directory signature for cache keys
    │   └── errors.py                  # user-facing parse error model
    ├── validation/
    │   ├── __init__.py
    │   ├── schema.py                  # JSON Schema loading + validation
    │   └── semantic.py                # duplicate ids, dangling edges, empty graph
    ├── graph/
    │   ├── __init__.py
    │   ├── model.py                   # dataclasses / typed graph entities
    │   ├── builder.py                 # payload -> NetworkX graph + indexes
    │   └── queries.py                 # neighbors, search, degree metadata
    ├── layout/
    │   ├── __init__.py
    │   └── positions.py               # deterministic automatic layout
    └── render/
        ├── __init__.py
        ├── plotly_renderer.py         # Plotly figure construction
        ├── selection.py               # selected node + neighbor state
        └── viewport.py                # search centering / axis ranges

tests/
├── unit/
│   ├── parsing/
│   ├── validation/
│   ├── graph/
│   ├── layout/
│   └── render/
├── integration/
│   ├── test_load_validate_render_flow.py
│   ├── test_streamlit_cache_boundaries.py
│   └── test_5000_node_performance_fixture.py
└── fixtures/
    ├── valid_small_graph/
    ├── invalid_graphs/
    └── generated_large_graphs/
```

**Structure Decision**: Use one Python package under `src/graph_viewer`.
Streamlit is limited to `app.py`; all behavior that can be tested without UI
lives in pure modules. Tests mirror the module layout so constitutional
testability can be verified directly.

## Phase 0 Research

Completed in [research.md](./research.md).

## Phase 1 Design

Completed artifacts:
- [data-model.md](./data-model.md)
- [contracts/graph-input.schema.json](./contracts/graph-input.schema.json)
- [contracts/python-source-contract.md](./contracts/python-source-contract.md)
- [contracts/render-interaction-contract.md](./contracts/render-interaction-contract.md)
- [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

- **Stack clarity**: PASS. Streamlit remains the UI shell; Plotly is the
  renderer.
- **Performance**: PASS. Design includes Streamlit cache keys based on path
  signatures, layout caching, WebGL traces, and a 5,000-node performance
  quickstart scenario.
- **Dependency discipline**: PASS. No unresearched dependency is introduced.
  `orjson`, Streamlit custom components, `streamlit-agraph`, and PyVis are
  rejected for initial scope.
- **Testability**: PASS. Data model and contracts define pure inputs/outputs
  for isolated tests before UI work.
- **Layer boundaries**: PASS. Contracts separate source parsing, JSON schema,
  NetworkX graph model, layout, render data, and Streamlit event handling.
- **Input validation**: PASS. JSON Schema plus semantic validation blocks render
  until the graph is valid.

## Complexity Tracking

No constitution violations.
