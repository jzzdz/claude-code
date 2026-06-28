from __future__ import annotations

from plotly.graph_objects import Figure, Scattergl

from graph_viewer.graph.builder import build_graph_model
from graph_viewer.layout.positions import compute_layout
from graph_viewer.render.plotly_renderer import build_figure, prepare_render_data


def test_prepare_render_data_contains_node_customdata_and_edge_segments(valid_payload):
    model = build_graph_model(valid_payload)
    layout = compute_layout(model)

    render_data = prepare_render_data(model, layout)

    assert render_data.node_ids == ("node-a", "node-b", "node-c")
    assert render_data.node_labels == ("Alpha", "Beta", "Gamma")
    assert render_data.node_customdata == render_data.node_ids
    assert None in render_data.edge_x
    assert render_data.edge_mode == "all"


def test_build_figure_uses_webgl_node_trace(valid_payload):
    model = build_graph_model(valid_payload)
    layout = compute_layout(model)
    render_data = prepare_render_data(model, layout)

    figure = build_figure(render_data)

    assert isinstance(figure, Figure)
    assert isinstance(figure.data[-1], Scattergl)
    assert tuple(figure.data[-1].customdata) == render_data.node_ids
    assert figure.layout.dragmode == "pan"

