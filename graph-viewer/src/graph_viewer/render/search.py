from __future__ import annotations

from graph_viewer.graph.model import GraphModel, SearchState
from graph_viewer.graph.queries import search_nodes_by_label


def clear_search_state() -> SearchState:
    return SearchState()


def build_search_state(
    model: GraphModel,
    query: str,
    *,
    active_node_id: str | None = None,
) -> SearchState:
    normalized_query = query.strip()
    if not normalized_query:
        return clear_search_state()

    matches = search_nodes_by_label(model, normalized_query)
    if not matches:
        return SearchState(
            query=normalized_query,
            matches=(),
            active_node_id=None,
            message=f"No nodes found for '{normalized_query}'.",
        )

    active = active_node_id if active_node_id in matches else matches[0]
    message = f"{len(matches)} matches found. Choose a result." if len(matches) > 1 else None
    return SearchState(
        query=normalized_query,
        matches=matches,
        active_node_id=active,
        message=message,
    )

