from __future__ import annotations

from graph_viewer.graph.model import GraphModel, SelectionState


def clear_selection_state() -> SelectionState:
    return SelectionState()


def build_selection_state(model: GraphModel, selected_node_id: str | None) -> SelectionState:
    if not selected_node_id or selected_node_id not in model.node_by_id:
        return clear_selection_state()

    neighbor_ids = model.neighbors_by_id.get(selected_node_id, frozenset())
    highlighted_edge_ids = frozenset(
        edge.id or f"{edge.source}->{edge.target}"
        for edge in model.edges
        if edge.source == selected_node_id
        or edge.target == selected_node_id
        or (edge.source in neighbor_ids and edge.target == selected_node_id)
        or (edge.target in neighbor_ids and edge.source == selected_node_id)
    )
    return SelectionState(
        selected_node_id=selected_node_id,
        neighbor_ids=neighbor_ids,
        highlighted_edge_ids=highlighted_edge_ids,
    )

