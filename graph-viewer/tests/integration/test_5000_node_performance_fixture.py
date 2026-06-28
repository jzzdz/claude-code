from __future__ import annotations

import time

from graph_viewer.graph.builder import build_graph_model
from graph_viewer.layout.positions import compute_layout
from graph_viewer.render.plotly_renderer import prepare_render_data


def test_5000_node_fixture_prepares_within_budget(large_graph_payload):
    started_at = time.perf_counter()

    model = build_graph_model(large_graph_payload)
    layout = compute_layout(model)
    render_data = prepare_render_data(model, layout)

    elapsed = time.perf_counter() - started_at

    assert model.node_count == 5000
    assert len(render_data.node_ids) == 5000
    assert elapsed < 5.0

