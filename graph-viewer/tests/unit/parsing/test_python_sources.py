from __future__ import annotations

from graph_viewer.parsing.python_sources import load_graph_payload


def test_load_graph_payload_merges_graph_and_node_exports(valid_graph_path, valid_nodes_path):
    result = load_graph_payload(valid_graph_path, valid_nodes_path)

    assert result.errors == ()
    assert result.payload is not None
    assert result.payload["directed"] is True
    assert {node["id"] for node in result.payload["nodes"]} == {
        "graph-only",
        "node-a",
        "node-b",
        "node-c",
    }
    assert len(result.payload["edges"]) == 3


def test_load_graph_payload_prefers_getters_and_warns_on_ignored_node_files(tmp_path):
    graph_path = tmp_path / "graph.py"
    graph_path.write_text(
        "\n".join(
            [
                'GRAPH = {"nodes": [], "edges": []}',
                "def get_graph():",
                '    return {"directed": False, "nodes": [], "edges": []}',
            ]
        ),
        encoding="utf-8",
    )
    nodes_path = tmp_path / "nodes"
    nodes_path.mkdir()
    (nodes_path / "node.py").write_text(
        "\n".join(
            [
                'NODE = {"id": "constant", "label": "Constant"}',
                "def get_node():",
                '    return {"id": "getter", "label": "Getter"}',
            ]
        ),
        encoding="utf-8",
    )
    (nodes_path / "ignored.py").write_text("VALUE = 1\n", encoding="utf-8")

    result = load_graph_payload(graph_path, nodes_path)

    assert result.errors == ()
    assert result.payload is not None
    assert result.payload["directed"] is False
    assert result.payload["nodes"] == [{"id": "getter", "label": "Getter"}]
    assert len(result.warnings) == 1
    assert result.warnings[0].code == "node_export_missing"


def test_load_graph_payload_reports_invalid_paths(valid_nodes_path, tmp_path):
    missing_graph = tmp_path / "missing.py"

    result = load_graph_payload(missing_graph, valid_nodes_path)

    assert result.payload is None
    assert [error.code for error in result.errors] == ["graph_path_missing"]

