from __future__ import annotations

from graph_viewer.config import DIMMED_NODE_COLOR, NEIGHBOR_NODE_COLOR, SELECTED_NODE_COLOR
from graph_viewer.graph.builder import build_graph_model
from graph_viewer.layout.positions import compute_layout
from graph_viewer.render.plotly_renderer import build_figure, prepare_render_data
from graph_viewer.render.selection import build_selection_state


def test_prepare_render_data_recolors_selected_neighbors_and_unrelated_nodes():
    payload = {
        "directed": True,
        "nodes": [
            {"id": "node-a", "label": "Alpha"},
            {"id": "node-b", "label": "Beta"},
            {"id": "node-c", "label": "Gamma"},
        ],
        "edges": [{"source": "node-a", "target": "node-b"}],
    }
    model = build_graph_model(payload)
    layout = compute_layout(model)
    selection = build_selection_state(model, "node-a")

    render_data = prepare_render_data(model, layout, selection=selection)
    colors_by_id = dict(zip(render_data.node_ids, render_data.node_colors, strict=True))

    assert colors_by_id["node-a"] == SELECTED_NODE_COLOR
    assert colors_by_id["node-b"] == NEIGHBOR_NODE_COLOR
    assert colors_by_id["node-c"] == DIMMED_NODE_COLOR


def test_prepare_render_data_focuses_edges_around_selected_node(valid_payload):
    model = build_graph_model(valid_payload)
    layout = compute_layout(model)
    selection = build_selection_state(model, "node-b")

    render_data = prepare_render_data(model, layout, selection=selection)

    assert render_data.edge_mode == "focused"
    assert len(render_data.edge_x) == 3
    assert len(render_data.edge_y) == 3


def test_build_figure_uses_recolored_node_trace(valid_payload):
    model = build_graph_model(valid_payload)
    layout = compute_layout(model)
    selection = build_selection_state(model, "node-b")
    render_data = prepare_render_data(model, layout, selection=selection)

    figure = build_figure(render_data)
    node_trace = figure.data[-1]

    assert tuple(node_trace.marker.color) == render_data.node_colors
    assert tuple(node_trace.marker.size) == render_data.node_sizes

