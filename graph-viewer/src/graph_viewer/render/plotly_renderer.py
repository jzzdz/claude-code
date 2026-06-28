from __future__ import annotations

import math

import plotly.graph_objects as go

from graph_viewer.config import (
    DENSE_EDGE_CAP,
    DIMMED_NODE_COLOR,
    EDGE_COLOR,
    NEIGHBOR_NODE_COLOR,
    NEIGHBOR_NODE_SIZE,
    NODE_COLOR,
    NODE_MAX_SIZE,
    NODE_MIN_SIZE,
    SELECTED_NODE_COLOR,
    SELECTED_NODE_SIZE,
)
from graph_viewer.graph.model import GraphEdge, GraphModel, LayoutPositions, RenderGraphData, SearchState, SelectionState
from graph_viewer.render.viewport import center_viewport_on_node


def prepare_render_data(
    model: GraphModel,
    layout: LayoutPositions,
    *,
    dense_edge_cap: int = DENSE_EDGE_CAP,
    selection: SelectionState | None = None,
    search: SearchState | None = None,
    viewport: dict[str, tuple[float, float]] | None = None,
) -> RenderGraphData:
    node_ids = tuple(model.node_by_id)
    node_x = tuple(layout.positions[node_id]["x"] for node_id in node_ids)
    node_y = tuple(layout.positions[node_id]["y"] for node_id in node_ids)
    node_labels = tuple(model.node_by_id[node_id].label for node_id in node_ids)
    node_colors = tuple(_node_color(node_id, selection) for node_id in node_ids)
    node_sizes = tuple(_selected_node_size(node_id, model, selection) for node_id in node_ids)
    edge_mode, visible_edges = _visible_edges(model, dense_edge_cap, selection)
    active_viewport = viewport or _search_viewport(layout, search)

    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for edge in visible_edges:
        if edge.source not in layout.positions or edge.target not in layout.positions:
            continue
        source = layout.positions[edge.source]
        target = layout.positions[edge.target]
        edge_x.extend([source["x"], target["x"], None])
        edge_y.extend([source["y"], target["y"], None])

    return RenderGraphData(
        node_x=node_x,
        node_y=node_y,
        node_ids=node_ids,
        node_labels=node_labels,
        node_customdata=node_ids,
        node_colors=node_colors,
        node_sizes=node_sizes,
        edge_x=tuple(edge_x),
        edge_y=tuple(edge_y),
        edge_mode=edge_mode,
        viewport=active_viewport,
    )


def build_figure(render_data: RenderGraphData) -> go.Figure:
    edge_trace = go.Scattergl(
        x=render_data.edge_x,
        y=render_data.edge_y,
        mode="lines",
        line={"width": 1, "color": EDGE_COLOR},
        hoverinfo="none",
        showlegend=False,
    )
    node_trace = go.Scattergl(
        x=render_data.node_x,
        y=render_data.node_y,
        mode="markers+text",
        text=render_data.node_labels,
        customdata=render_data.node_customdata,
        textposition="top center",
        hovertemplate="%{text}<extra></extra>",
        marker={
            "color": render_data.node_colors,
            "size": render_data.node_sizes,
            "line": {"width": 1, "color": "rgba(15, 23, 42, 0.65)"},
        },
        showlegend=False,
    )
    figure = go.Figure(data=[edge_trace, node_trace])
    xaxis = {"visible": False, "showgrid": False, "zeroline": False}
    yaxis = {"visible": False, "showgrid": False, "zeroline": False, "scaleanchor": "x", "scaleratio": 1}
    if render_data.viewport is not None:
        xaxis["range"] = render_data.viewport["xaxis"]
        yaxis["range"] = render_data.viewport["yaxis"]

    figure.update_layout(
        dragmode="pan",
        hovermode="closest",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=xaxis,
        yaxis=yaxis,
        uirevision="graph-viewer-us1",
    )
    return figure


def _node_size(degree: int) -> int:
    if degree <= 0:
        return NODE_MIN_SIZE
    return min(NODE_MAX_SIZE, NODE_MIN_SIZE + int(math.log2(degree + 1) * 3))


def _node_color(node_id: str, selection: SelectionState | None) -> str:
    if selection is None or selection.selected_node_id is None:
        return NODE_COLOR
    if node_id == selection.selected_node_id:
        return SELECTED_NODE_COLOR
    if node_id in selection.neighbor_ids:
        return NEIGHBOR_NODE_COLOR
    return DIMMED_NODE_COLOR


def _selected_node_size(node_id: str, model: GraphModel, selection: SelectionState | None) -> int:
    if selection is not None and node_id == selection.selected_node_id:
        return SELECTED_NODE_SIZE
    if selection is not None and node_id in selection.neighbor_ids:
        return NEIGHBOR_NODE_SIZE
    return _node_size(model.node_by_id[node_id].degree)


def _visible_edges(
    model: GraphModel,
    dense_edge_cap: int,
    selection: SelectionState | None,
) -> tuple[str, tuple[GraphEdge, ...]]:
    if selection is not None and selection.selected_node_id is not None:
        selected_edges = tuple(
            edge
            for edge in model.edges
            if (edge.id or f"{edge.source}->{edge.target}") in selection.highlighted_edge_ids
        )
        return "focused", selected_edges
    if len(model.edges) <= dense_edge_cap:
        return "all", model.edges
    return "sampled", model.edges[:dense_edge_cap]


def _search_viewport(
    layout: LayoutPositions,
    search: SearchState | None,
) -> dict[str, tuple[float, float]] | None:
    if search is None or search.active_node_id is None:
        return None
    return center_viewport_on_node(layout, search.active_node_id)
