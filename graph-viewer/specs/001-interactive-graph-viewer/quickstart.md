# Quickstart: Interactive Graph Viewer

## Prerequisites

- Python 3.11+ (matches `pyproject.toml`; the original 3.12+ target was lowered
  during US1, see `progress/Decisions.md`)
- A local trusted graph source file matching
  [python-source-contract.md](./contracts/python-source-contract.md)
- A local trusted node source directory matching
  [python-source-contract.md](./contracts/python-source-contract.md)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run Tests

```bash
pytest
```

Expected outcome:
- Unit tests pass for parsing, validation, graph model, layout, render
  preparation, selection, search, and cache-key behavior.
- Integration tests pass for valid load, invalid input, and 5,000-node
  performance fixture.

## Run the App

```bash
streamlit run src/graph_viewer/app.py
```

Expected outcome:
- The Streamlit app opens in the browser.
- The UI asks for a graph source file path and a node source directory path.

## Scenario 1: Load a Valid Small Graph

1. Enter a valid graph source path.
2. Enter a valid node source directory path.
3. Load the graph.

Expected outcome:
- The graph renders visually.
- Nodes and edges are visible.
- Pan and zoom work.
- No validation errors appear.

## Scenario 2: Invalid Path or Schema Error

1. Enter a missing graph path, missing node directory, or malformed graph data.
2. Load the graph.

Expected outcome:
- Rendering is blocked.
- The app shows actionable error messages.
- Errors include which path or payload field failed when available.

## Scenario 3: Select a Node

1. Load a known graph with at least one node with neighbors.
2. Select a node in the graph.

Expected outcome:
- The selected node is highlighted.
- Direct neighbors are highlighted.
- Unrelated nodes remain visible but visually de-emphasized.

## Scenario 4: Search by Label

1. Load a known graph.
2. Search for an exact node label.

Expected outcome:
- The matching node is identified and centered within 2 seconds.
- If multiple labels match, the app lets the user choose.
- If no labels match, a no-results message appears and the current view remains
  stable.

## Scenario 5: 5,000-Node Performance Gate

1. Generate or load the large graph fixture with at least 5,000 nodes.
2. Load it in the app.
3. Pan and zoom after initial render.
4. Select a node and run an exact-label search.

Expected outcome:
- The interface does not freeze.
- Pan/zoom remains usable.
- Selection highlights the selected node and direct neighbors.
- Search locates the target node in under 2 seconds.
- Repeated Streamlit reruns do not recompute parsing or layout when source
  signatures are unchanged.

## Validation Results (2026-06-27, feature close-out — T053/T054)

Environment: `python311_neo_env` (Python 3.11.0, Streamlit 1.56.0).

### T053 — Full pytest suite

```text
45 passed in 0.81s
```

No failures. No remaining failures to record.

### T054 — Quickstart scenario validation

The interactive scenarios are validated programmatically by the integration
suite (manual Streamlit walkthroughs match this automated coverage):

| Scenario | Covered by | Result |
|----------|-----------|--------|
| 1 — Load a valid small graph | `tests/integration/test_load_validate_render_flow.py` | PASS |
| 2 — Invalid path or schema error | `tests/integration/test_load_validate_render_flow.py`, `test_streamlit_cache_boundaries.py` | PASS |
| 3 — Select a node | `tests/integration/test_plotly_selection_flow.py` | PASS |
| 4 — Search by label | `tests/integration/test_search_center_flow.py` | PASS |
| 5 — 5,000-node performance gate | `tests/integration/test_5000_node_performance_fixture.py` | PASS (render prep ~0.03s, budget < 5.0s) |

### T055 — 5,000-node edge level-of-detail tuning

No tuning required: `test_5000_node_fixture_prepares_within_budget` passes with
~0.03s against a 5.0s budget, so the `DENSE_EDGE_CAP` default in `config.py` is
left unchanged.
