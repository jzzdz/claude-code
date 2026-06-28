from __future__ import annotations

from graph_viewer.app import load_graph_for_render, update_render_for_selection_event
from graph_viewer.config import NEIGHBOR_NODE_COLOR, SELECTED_NODE_COLOR


def test_plotly_selection_event_updates_rendered_highlight_state(valid_graph_path, valid_nodes_path):
    loaded = load_graph_for_render(valid_graph_path, valid_nodes_path)
    event_payload = {"selection": {"points": [{"customdata": "node-a"}]}}

    selected = update_render_for_selection_event(loaded, event_payload)

    assert selected.selection_state.selected_node_id == "node-a"
    assert selected.selection_state.neighbor_ids == frozenset({"node-b", "node-c"})
    colors_by_id = dict(zip(selected.render_data.node_ids, selected.render_data.node_colors, strict=True))
    assert colors_by_id["node-a"] == SELECTED_NODE_COLOR
    assert colors_by_id["node-b"] == NEIGHBOR_NODE_COLOR
    assert colors_by_id["node-c"] == NEIGHBOR_NODE_COLOR
    assert selected.figure is not None


def test_empty_selection_event_clears_highlight_state(valid_graph_path, valid_nodes_path):
    loaded = load_graph_for_render(valid_graph_path, valid_nodes_path)

    cleared = update_render_for_selection_event(loaded, {"selection": {"points": []}})

    assert cleared.selection_state.selected_node_id is None
    assert cleared.render_data == loaded.render_data

