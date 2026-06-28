from __future__ import annotations

import hashlib
import json
import math
from typing import Any

import networkx as nx

from graph_viewer.config import (
    LAYOUT_DEFAULT_ITERATIONS,
    LAYOUT_LARGE_GRAPH_MAX_ITERATIONS,
    LAYOUT_LARGE_GRAPH_THRESHOLD,
    LAYOUT_SEED,
)
from graph_viewer.graph.model import GraphModel, LayoutPositions


def compute_layout(model: GraphModel) -> LayoutPositions:
    if model.node_count == 0:
        return LayoutPositions(positions={}, algorithm="empty", options={}, signature=model.signature)

    if model.node_count >= LAYOUT_LARGE_GRAPH_THRESHOLD:
        algorithm = "deterministic_circle"
        options: dict[str, Any] = {
            "seed": LAYOUT_SEED,
            "threshold": LAYOUT_LARGE_GRAPH_THRESHOLD,
            "max_iterations": LAYOUT_LARGE_GRAPH_MAX_ITERATIONS,
        }
        positions = _deterministic_circle_positions(tuple(model.node_by_id))
    else:
        algorithm, raw_positions = _small_graph_layout(model)
        options = {"seed": LAYOUT_SEED, "iterations": LAYOUT_DEFAULT_ITERATIONS}
        positions = _normalize_positions(raw_positions)

    signature = _layout_signature(model.signature, algorithm, options)
    return LayoutPositions(positions=positions, algorithm=algorithm, options=options, signature=signature)


def _small_graph_layout(model: GraphModel):
    if hasattr(nx, "forceatlas2_layout"):
        try:
            return "forceatlas2", nx.forceatlas2_layout(
                model.graph,
                seed=LAYOUT_SEED,
                max_iter=LAYOUT_DEFAULT_ITERATIONS,
            )
        except TypeError:
            pass
    return "spring", nx.spring_layout(model.graph, seed=LAYOUT_SEED, iterations=LAYOUT_DEFAULT_ITERATIONS)


def _deterministic_circle_positions(node_ids: tuple[str, ...]) -> dict[str, dict[str, float]]:
    radius = max(1.0, math.sqrt(len(node_ids)))
    total = len(node_ids)
    positions = {}
    for index, node_id in enumerate(node_ids):
        angle = (2.0 * math.pi * index) / total
        positions[node_id] = {
            "x": round(radius * math.cos(angle), 6),
            "y": round(radius * math.sin(angle), 6),
        }
    return positions


def _normalize_positions(raw_positions) -> dict[str, dict[str, float]]:
    return {
        str(node_id): {
            "x": round(float(position[0]), 6),
            "y": round(float(position[1]), 6),
        }
        for node_id, position in raw_positions.items()
    }


def _layout_signature(graph_signature: str, algorithm: str, options: dict[str, Any]) -> str:
    serialized = json.dumps(
        {"graph": graph_signature, "algorithm": algorithm, "options": options},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

