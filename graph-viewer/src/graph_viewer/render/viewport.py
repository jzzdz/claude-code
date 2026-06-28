from __future__ import annotations

from graph_viewer.graph.model import LayoutPositions

DEFAULT_VIEWPORT_PADDING_RATIO = 0.25
MIN_VIEWPORT_SPAN = 4.0


def center_viewport_on_node(
    layout: LayoutPositions,
    node_id: str,
    *,
    padding_ratio: float = DEFAULT_VIEWPORT_PADDING_RATIO,
    min_span: float = MIN_VIEWPORT_SPAN,
) -> dict[str, tuple[float, float]] | None:
    target = layout.positions.get(node_id)
    if target is None:
        return None

    x_values = [position["x"] for position in layout.positions.values()]
    y_values = [position["y"] for position in layout.positions.values()]
    x_span = max(max(x_values) - min(x_values), min_span)
    y_span = max(max(y_values) - min(y_values), min_span)
    span = max(x_span, y_span) * (1.0 + padding_ratio)
    half_span = span / 2.0

    return {
        "xaxis": (target["x"] - half_span, target["x"] + half_span),
        "yaxis": (target["y"] - half_span, target["y"] + half_span),
    }

