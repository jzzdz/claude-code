from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixtures_path() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def valid_graph_path(fixtures_path: Path) -> Path:
    return fixtures_path / "valid_small_graph" / "graph.py"


@pytest.fixture(scope="session")
def valid_nodes_path(fixtures_path: Path) -> Path:
    return fixtures_path / "valid_small_graph" / "nodes"


@pytest.fixture(scope="session")
def invalid_graphs_path(fixtures_path: Path) -> Path:
    return fixtures_path / "invalid_graphs"


@pytest.fixture(scope="session")
def large_graph_payload(fixtures_path: Path) -> dict:
    generator_path = fixtures_path / "generated_large_graphs" / "generate_large_graph.py"
    spec = importlib.util.spec_from_file_location("large_graph_fixture", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load large graph fixture generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_large_graph()


@pytest.fixture
def valid_payload() -> dict:
    return {
        "directed": True,
        "nodes": [
            {"id": "node-a", "label": "Alpha"},
            {"id": "node-b", "label": "Beta"},
            {"id": "node-c", "label": "Gamma"},
        ],
        "edges": [
            {"source": "node-a", "target": "node-b"},
            {"source": "node-a", "target": "node-c"},
        ],
    }


@pytest.fixture
def invalid_payloads() -> dict[str, dict]:
    return {
        "duplicate_nodes": {
            "directed": True,
            "nodes": [
                {"id": "node-a", "label": "Alpha"},
                {"id": "node-a", "label": "Duplicate Alpha"},
            ],
            "edges": [],
        },
        "dangling_edge": {
            "directed": True,
            "nodes": [{"id": "node-a", "label": "Alpha"}],
            "edges": [{"source": "node-a", "target": "missing"}],
        },
        "empty_graph": {"directed": True, "nodes": [], "edges": []},
        "empty_label": {
            "directed": True,
            "nodes": [{"id": "node-a", "label": "   "}],
            "edges": [],
        },
    }

