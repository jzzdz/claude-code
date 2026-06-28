from __future__ import annotations

from graph_viewer.graph.builder import build_graph_model
from graph_viewer.graph.queries import search_nodes_by_label


def _search_model():
    return build_graph_model(
        {
            "directed": True,
            "nodes": [
                {"id": "node-alpha", "label": "Alpha"},
                {"id": "node-alpha-copy", "label": " alpha "},
                {"id": "node-alphabet", "label": "Alphabet"},
                {"id": "node-beta", "label": "Beta Alpha"},
                {"id": "node-gamma", "label": "Gamma"},
            ],
            "edges": [],
        }
    )


def test_search_nodes_by_label_ranks_exact_case_insensitive_matches_first():
    matches = search_nodes_by_label(_search_model(), "ALPHA")

    assert matches == ("node-alpha", "node-alpha-copy", "node-alphabet", "node-beta")


def test_search_nodes_by_label_supports_partial_matches_in_graph_order():
    matches = search_nodes_by_label(_search_model(), "alp")

    assert matches == ("node-alpha", "node-alpha-copy", "node-alphabet", "node-beta")


def test_search_nodes_by_label_returns_empty_for_no_result_or_blank_query():
    model = _search_model()

    assert search_nodes_by_label(model, "missing") == ()
    assert search_nodes_by_label(model, "   ") == ()

