# Graph Viewer

Interactive Streamlit graph viewer with JSON Schema validation and Plotly
WebGL rendering. You provide a trusted graph Python file and a node Python
directory; the app parses them into a JSON-compatible payload, validates it,
builds a NetworkX model, computes a deterministic layout, and renders an
interactive view with pan/zoom, neighbor highlighting on selection, and label
search with centering.

## Requirements

- Python 3.11+ (`pyproject.toml` declares `requires-python = ">=3.11"`).
- A local **trusted** graph source file and node source directory matching
  [`specs/001-interactive-graph-viewer/contracts/python-source-contract.md`](specs/001-interactive-graph-viewer/contracts/python-source-contract.md).
  Sources are imported as-is; do not point the app at untrusted code.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run tests

The suite is configured in `pyproject.toml` (`testpaths = ["tests"]`,
`pythonpath = ["src"]`), so no extra flags are needed:

```bash
pytest
```

Expected: unit tests for parsing, validation, graph model, layout, render
preparation, selection, and search; integration tests for valid load, invalid
input blocking, cache boundaries, and the 5,000-node performance fixture.

## Run the app

```bash
streamlit run src/graph_viewer/app.py
```

The UI asks for a graph file path and a node directory path. After **Load
graph**, you can:

- Pan and zoom the graph (scroll-zoom enabled).
- Click a node to highlight it and its direct neighbors.
- Search by label; pick among multiple matches and center the view on the
  result. No-result searches leave the current view stable.

## Project layout

```text
src/graph_viewer/
├── app.py            # Streamlit presentation + cached load pipeline (UI-only edge)
├── parsing/          # trusted source loading, cache-key signatures, error model
├── validation/       # JSON Schema + semantic validation
├── graph/            # NetworkX model, builder, label/neighbor queries
├── layout/           # deterministic automatic layout
└── render/           # Plotly figure prep, selection, search, viewport
tests/                # unit tests mirror modules; integration covers flows + perf
specs/001-interactive-graph-viewer/   # spec, plan, tasks, contracts, quickstart
```

See [`docs/architecture.md`](docs/architecture.md) for module boundaries, the
cache strategy, and the Plotly selection flow.
