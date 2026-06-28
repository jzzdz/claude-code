from __future__ import annotations

from graph_viewer.app import load_graph_for_render, update_render_for_search


def test_search_center_flow_centers_matching_node(valid_graph_path, valid_nodes_path):
    loaded = load_graph_for_render(valid_graph_path, valid_nodes_path)

    searched = update_render_for_search(loaded, "gamma")

    assert searched.search_state.query == "gamma"
    assert searched.search_state.matches == ("node-c",)
    assert searched.search_state.active_node_id == "node-c"
    assert searched.render_data is not None
    assert searched.render_data.viewport is not None
    assert searched.figure is not None
    assert tuple(searched.figure.layout.xaxis.range) == searched.render_data.viewport["xaxis"]
    assert tuple(searched.figure.layout.yaxis.range) == searched.render_data.viewport["yaxis"]


def test_search_center_flow_supports_result_selection(valid_graph_path, valid_nodes_path):
    loaded = load_graph_for_render(valid_graph_path, valid_nodes_path)

    searched = update_render_for_search(loaded, "a", active_node_id="node-c")

    assert searched.search_state.matches == ("graph-only", "node-a", "node-b", "node-c")
    assert searched.search_state.active_node_id == "node-c"
    assert searched.render_data.viewport is not None


def test_no_result_search_preserves_current_render_viewport(valid_graph_path, valid_nodes_path):
    loaded = load_graph_for_render(valid_graph_path, valid_nodes_path)
    centered = update_render_for_search(loaded, "alpha")

    missing = update_render_for_search(centered, "missing")

    assert missing.search_state.active_node_id is None
    assert missing.search_state.message == "No nodes found for 'missing'."
    assert missing.render_data is not None
    assert centered.render_data is not None
    assert missing.render_data.viewport == centered.render_data.viewport
