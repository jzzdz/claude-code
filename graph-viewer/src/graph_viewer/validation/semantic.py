from __future__ import annotations

from typing import Any

from graph_viewer.graph.model import ValidationResult
from graph_viewer.parsing.errors import error_report, warning_report


def validate_semantics(payload: dict[str, Any]) -> ValidationResult:
    nodes = [dict(node) for node in payload.get("nodes", [])]
    edges = [dict(edge) for edge in payload.get("edges", [])]
    errors = []
    warnings = []

    if not nodes:
        errors.append(error_report("empty_graph", "$.nodes", "Graph must contain at least one node."))

    seen_node_ids: set[str] = set()
    duplicate_node_ids: set[str] = set()
    normalized_nodes = []
    for index, node in enumerate(nodes):
        node_id = str(node.get("id", ""))
        label = str(node.get("label", "")).strip()
        if node_id in seen_node_ids and node_id not in duplicate_node_ids:
            duplicate_node_ids.add(node_id)
            errors.append(
                error_report(
                    "duplicate_node_id",
                    f"$.nodes[{index}].id",
                    f"Duplicate node id '{node_id}' found.",
                )
            )
        seen_node_ids.add(node_id)
        if not label:
            errors.append(
                error_report(
                    "empty_node_label",
                    f"$.nodes[{index}].label",
                    f"Node '{node_id}' label cannot be empty after trimming.",
                )
            )
        normalized = dict(node)
        normalized["label"] = label
        normalized_nodes.append(normalized)

    directed = bool(payload.get("directed", True))
    seen_edges: set[tuple[str, str]] = set()
    for index, edge in enumerate(edges):
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        missing = [node_id for node_id in (source, target) if node_id not in seen_node_ids]
        if missing:
            errors.append(
                error_report(
                    "dangling_edge",
                    f"$.edges[{index}]",
                    f"Edge references missing node id(s): {', '.join(missing)}.",
                )
            )
        edge_key = (source, target) if directed else tuple(sorted((source, target)))
        if edge_key in seen_edges:
            warnings.append(
                warning_report(
                    "duplicate_edge",
                    f"$.edges[{index}]",
                    f"Duplicate edge '{source}' -> '{target}' found.",
                )
            )
        seen_edges.add(edge_key)

    if errors:
        return ValidationResult(payload=None, errors=tuple(errors), warnings=tuple(warnings))

    normalized_payload = dict(payload)
    normalized_payload.setdefault("directed", True)
    normalized_payload["nodes"] = normalized_nodes
    normalized_payload["edges"] = edges
    return ValidationResult(payload=normalized_payload, warnings=tuple(warnings))

