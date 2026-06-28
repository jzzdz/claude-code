from __future__ import annotations

from graph_viewer.app import load_graph_for_render
from graph_viewer.graph.builder import build_graph_model
from graph_viewer.parsing.python_sources import load_graph_payload
from graph_viewer.validation.schema import validate_payload_schema
from graph_viewer.validation.semantic import validate_semantics


def test_four_node_graph_preserves_second_node_subgraph_metadata(fixtures_path):
    graph_path = fixtures_path / "valid_nested_graph" / "graph.py"
    nodes_path = fixtures_path / "valid_nested_graph" / "nodes"

    source_result = load_graph_payload(graph_path, nodes_path)
    schema_result = validate_payload_schema(source_result.payload)
    semantic_result = validate_semantics(schema_result.payload)
    model = build_graph_model(semantic_result.payload)
    render_result = load_graph_for_render(graph_path, nodes_path)

    nested_subgraph = model.node_by_id["node-2"].metadata["subgraph"]

    assert source_result.errors == ()
    assert schema_result.errors == ()
    assert semantic_result.errors == ()
    assert model.node_count == 4
    assert len(nested_subgraph["nodes"]) == 5
    assert len(nested_subgraph["edges"]) == 4
    assert render_result.render_data is not None
    assert render_result.render_data.node_ids == ("node-1", "node-2", "node-3", "node-4")

