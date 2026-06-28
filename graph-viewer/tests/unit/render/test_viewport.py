from __future__ import annotations

import pytest

from graph_viewer.graph.model import LayoutPositions
from graph_viewer.render.viewport import center_viewport_on_node


def _layout():
    return LayoutPositions(
        positions={
            "node-a": {"x": 0.0, "y": 0.0},
            "node-b": {"x": 10.0, "y": -4.0},
            "node-c": {"x": 20.0, "y": 2.0},
        },
        algorithm="test",
        options={},
        signature="layout",
    )


def test_center_viewport_on_node_returns_axis_ranges_centered_on_node():
    viewport = center_viewport_on_node(_layout(), "node-b")

    assert viewport is not None
    x_start, x_end = viewport["xaxis"]
    y_start, y_end = viewport["yaxis"]
    assert (x_start + x_end) / 2 == pytest.approx(10.0)
    assert (y_start + y_end) / 2 == pytest.approx(-4.0)
    assert x_end > x_start
    assert y_end > y_start


def test_center_viewport_on_node_returns_none_for_missing_node():
    assert center_viewport_on_node(_layout(), "missing") is None

