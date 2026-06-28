from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any

import networkx as nx

from graph_viewer.graph.model import GraphEdge, GraphModel, GraphNode


def build_graph_model(payload: dict[str, Any]) -> GraphModel:
    directed = bool(payload.get("directed", True))
    graph = nx.DiGraph() if directed else nx.Graph()

    raw_nodes = payload.get("nodes", [])
    for node in raw_nodes:
        graph.add_node(
            node["id"],
            label=node["label"],
            metadata=dict(node.get("metadata", {})),
        )

    edges: list[GraphEdge] = []
    for index, edge in enumerate(payload.get("edges", [])):
        graph_edge = GraphEdge(
            source=edge["source"],
            target=edge["target"],
            directed=edge.get("directed"),
            label=edge.get("label"),
            metadata=dict(edge.get("metadata", {})),
            id=edge.get("id", f"edge-{index}"),
        )
        edges.append(graph_edge)
        graph.add_edge(
            graph_edge.source,
            graph_edge.target,
            id=graph_edge.id,
            label=graph_edge.label,
            metadata=graph_edge.metadata,
            directed=graph_edge.directed,
        )

    node_by_id = {
        node["id"]: GraphNode(
            id=node["id"],
            label=node["label"],
            metadata=dict(node.get("metadata", {})),
            degree=int(graph.degree(node["id"])),
        )
        for node in raw_nodes
    }
    label_index = _build_label_index(node_by_id)
    neighbors_by_id = _build_neighbor_index(graph, node_by_id)
    signature = _graph_signature(payload)

    return GraphModel(
        graph=graph,
        node_by_id=node_by_id,
        edges=tuple(edges),
        label_index=label_index,
        neighbors_by_id=neighbors_by_id,
        edge_count=len(edges),
        node_count=len(node_by_id),
        signature=signature,
    )


def _build_label_index(node_by_id: dict[str, GraphNode]) -> dict[str, tuple[str, ...]]:
    labels: dict[str, list[str]] = defaultdict(list)
    for node_id, node in node_by_id.items():
        labels[node.label.casefold().strip()].append(node_id)
    return {label: tuple(node_ids) for label, node_ids in labels.items()}


def _build_neighbor_index(graph, node_by_id: dict[str, GraphNode]) -> dict[str, frozenset[str]]:
    neighbors: dict[str, frozenset[str]] = {}
    for node_id in node_by_id:
        if graph.is_directed():
            adjacent = set(graph.successors(node_id)) | set(graph.predecessors(node_id))
        else:
            adjacent = set(graph.neighbors(node_id))
        neighbors[node_id] = frozenset(sorted(adjacent))
    return neighbors


def _graph_signature(payload: dict[str, Any]) -> str:
    canonical = {
        "directed": bool(payload.get("directed", True)),
        "nodes": [
            {
                "id": node["id"],
                "label": node["label"],
                "metadata": node.get("metadata", {}),
            }
            for node in payload.get("nodes", [])
        ],
        "edges": [
            {
                "id": edge.get("id"),
                "source": edge["source"],
                "target": edge["target"],
                "directed": edge.get("directed"),
                "label": edge.get("label"),
                "metadata": edge.get("metadata", {}),
            }
            for edge in payload.get("edges", [])
        ],
        "metadata": payload.get("metadata", {}),
    }
    serialized = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

