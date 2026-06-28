from __future__ import annotations

import math

from graph_viewer.graph.builder import build_graph_model
from graph_viewer.layout.positions import compute_layout


def test_compute_layout_returns_finite_position_for_every_node(valid_payload):
    model = build_graph_model(valid_payload)

    layout = compute_layout(model)

    assert set(layout.positions) == set(model.node_by_id)
    for position in layout.positions.values():
        assert math.isfinite(position["x"])
        assert math.isfinite(position["y"])


def test_compute_layout_is_deterministic_for_same_graph(valid_payload):
    model = build_graph_model(valid_payload)

    first = compute_layout(model)
    second = compute_layout(model)

    assert first.positions == second.positions
    assert first.signature == second.signature

