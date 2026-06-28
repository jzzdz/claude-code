from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

JsonObject = dict[str, Any]


@dataclass(frozen=True)
class ValidationErrorReport:
    code: str
    path: str
    message: str
    severity: str = "error"


@dataclass(frozen=True)
class ValidationResult:
    payload: JsonObject | None = None
    errors: tuple[ValidationErrorReport, ...] = ()
    warnings: tuple[ValidationErrorReport, ...] = ()

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


@dataclass(frozen=True)
class SourcePaths:
    graph_path: str
    nodes_path: str
    signature: str


@dataclass(frozen=True)
class RawGraphPayload:
    directed: bool
    nodes: tuple[JsonObject, ...]
    edges: tuple[JsonObject, ...]
    metadata: JsonObject = field(default_factory=dict)


@dataclass(frozen=True)
class GraphNode:
    id: str
    label: str
    metadata: JsonObject = field(default_factory=dict)
    degree: int = 0


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    directed: bool | None = None
    label: str | None = None
    metadata: JsonObject = field(default_factory=dict)
    id: str | None = None


@dataclass(frozen=True)
class GraphModel:
    graph: Any
    node_by_id: dict[str, GraphNode]
    edges: tuple[GraphEdge, ...]
    label_index: dict[str, tuple[str, ...]]
    neighbors_by_id: dict[str, frozenset[str]]
    edge_count: int
    node_count: int
    signature: str


@dataclass(frozen=True)
class LayoutPositions:
    positions: dict[str, dict[str, float]]
    algorithm: str
    options: dict[str, Any]
    signature: str


@dataclass(frozen=True)
class RenderGraphData:
    node_x: tuple[float, ...]
    node_y: tuple[float, ...]
    node_ids: tuple[str, ...]
    node_labels: tuple[str, ...]
    node_customdata: tuple[str, ...]
    node_colors: tuple[str, ...]
    node_sizes: tuple[int, ...]
    edge_x: tuple[float | None, ...]
    edge_y: tuple[float | None, ...]
    edge_mode: str
    viewport: dict[str, tuple[float, float]] | None = None


@dataclass(frozen=True)
class SelectionState:
    selected_node_id: str | None = None
    neighbor_ids: frozenset[str] = frozenset()
    highlighted_edge_ids: frozenset[str] = frozenset()


@dataclass(frozen=True)
class SearchState:
    query: str = ""
    matches: tuple[str, ...] = ()
    active_node_id: str | None = None
    message: str | None = None

