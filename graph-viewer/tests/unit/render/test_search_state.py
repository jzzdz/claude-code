from __future__ import annotations

from graph_viewer.graph.builder import build_graph_model
from graph_viewer.render.search import build_search_state, clear_search_state


def _model():
    return build_graph_model(
        {
            "directed": True,
            "nodes": [
                {"id": "node-alpha", "label": "Alpha"},
                {"id": "node-alphabet", "label": "Alphabet"},
                {"id": "node-beta", "label": "Beta Alpha"},
            ],
            "edges": [],
        }
    )


def test_build_search_state_selects_first_match_and_reports_multiple_matches():
    state = build_search_state(_model(), "alp")

    assert state.query == "alp"
    assert state.matches == ("node-alpha", "node-alphabet", "node-beta")
    assert state.active_node_id == "node-alpha"
    assert state.message == "3 matches found. Choose a result."


def test_build_search_state_keeps_requested_active_match():
    state = build_search_state(_model(), "alp", active_node_id="node-beta")

    assert state.active_node_id == "node-beta"


def test_build_search_state_reports_no_results_without_active_node():
    state = build_search_state(_model(), "missing")

    assert state.matches == ()
    assert state.active_node_id is None
    assert state.message == "No nodes found for 'missing'."


def test_clear_search_state_returns_empty_state():
    assert clear_search_state() == build_search_state(_model(), "")

