from __future__ import annotations

from graph_viewer.graph.model import GraphModel


def search_nodes_by_label(model: GraphModel, query: str) -> tuple[str, ...]:
    normalized_query = query.casefold().strip()
    if not normalized_query:
        return ()

    exact_matches = model.label_index.get(normalized_query, ())
    exact_set = set(exact_matches)
    partial_matches = tuple(
        node_id
        for node_id, node in model.node_by_id.items()
        if node_id not in exact_set and normalized_query in node.label.casefold().strip()
    )
    return exact_matches + partial_matches

