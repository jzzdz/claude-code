from __future__ import annotations

import networkx as nx

from graph_viewer.graph.builder import build_graph_model


def test_build_graph_model_creates_directed_networkx_graph_and_indexes(valid_payload):
    model = build_graph_model(valid_payload)

    assert isinstance(model.graph, nx.DiGraph)
    assert model.node_count == 3
    assert model.edge_count == 2
    assert model.node_by_id["node-a"].degree == 2
    assert model.label_index == {"alpha": ("node-a",), "beta": ("node-b",), "gamma": ("node-c",)}
    assert model.neighbors_by_id["node-b"] == frozenset({"node-a"})
    assert len(model.signature) == 64


def test_build_graph_model_supports_undirected_graph(valid_payload):
    valid_payload["directed"] = False

    model = build_graph_model(valid_payload)

    assert isinstance(model.graph, nx.Graph)
    assert model.neighbors_by_id["node-b"] == frozenset({"node-a"})

