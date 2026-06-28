from __future__ import annotations

from graph_viewer.validation.semantic import validate_semantics


def test_validate_semantics_detects_duplicate_ids_dangling_edges_and_empty_graph(invalid_payloads):
    duplicate = validate_semantics(invalid_payloads["duplicate_nodes"])
    dangling = validate_semantics(invalid_payloads["dangling_edge"])
    empty = validate_semantics(invalid_payloads["empty_graph"])

    assert [error.code for error in duplicate.errors] == ["duplicate_node_id"]
    assert [error.code for error in dangling.errors] == ["dangling_edge"]
    assert [error.code for error in empty.errors] == ["empty_graph"]


def test_validate_semantics_trims_labels_and_rejects_empty_trimmed_label():
    valid = validate_semantics(
        {
            "directed": True,
            "nodes": [{"id": "node-a", "label": "  Alpha  "}],
            "edges": [],
        }
    )
    invalid = validate_semantics(
        {
            "directed": True,
            "nodes": [{"id": "node-a", "label": "   "}],
            "edges": [],
        }
    )

    assert valid.payload is not None
    assert valid.payload["nodes"][0]["label"] == "Alpha"
    assert [error.code for error in invalid.errors] == ["empty_node_label"]


def test_validate_semantics_reports_duplicate_edges_as_warnings(valid_payload):
    valid_payload["edges"].append({"source": "node-a", "target": "node-b"})

    result = validate_semantics(valid_payload)

    assert result.errors == ()
    assert [warning.code for warning in result.warnings] == ["duplicate_edge"]

