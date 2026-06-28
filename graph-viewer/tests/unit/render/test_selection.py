from __future__ import annotations

from graph_viewer.graph.builder import build_graph_model
from graph_viewer.render.selection import build_selection_state, clear_selection_state


def test_build_selection_state_uses_graph_model_direct_neighbors(valid_payload):
    model = build_graph_model(valid_payload)

    state = build_selection_state(model, "node-a")

    assert state.selected_node_id == "node-a"
    assert state.neighbor_ids == frozenset({"node-b", "node-c"})
    assert state.highlighted_edge_ids == frozenset({"edge-0", "edge-1"})


def test_build_selection_state_supports_directed_predecessor_neighbors(valid_payload):
    model = build_graph_model(valid_payload)

    state = build_selection_state(model, "node-b")

    assert state.selected_node_id == "node-b"
    assert state.neighbor_ids == frozenset({"node-a"})
    assert state.highlighted_edge_ids == frozenset({"edge-0"})


def test_build_selection_state_clears_unknown_node():
    model = build_graph_model({"directed": True, "nodes": [{"id": "node-a", "label": "A"}], "edges": []})

    assert build_selection_state(model, "missing") == clear_selection_state()

