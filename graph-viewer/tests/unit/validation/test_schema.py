from __future__ import annotations

from graph_viewer.validation.schema import load_graph_schema, validate_payload_schema


def test_load_graph_schema_reads_packaged_contract():
    schema = load_graph_schema()

    assert schema["title"] == "Graph Viewer Input Payload"
    assert schema["required"] == ["nodes", "edges"]


def test_validate_payload_schema_collects_all_errors():
    payload = {
        "directed": "yes",
        "nodes": [{"id": "node-a"}],
        "edges": [{"source": "node-a"}],
    }

    result = validate_payload_schema(payload)

    assert result.has_errors is True
    assert len(result.errors) == 3
    assert {error.path for error in result.errors} == {
        "$.directed",
        "$.edges[0]",
        "$.nodes[0]",
    }

