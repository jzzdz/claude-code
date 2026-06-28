from __future__ import annotations

from graph_viewer.parsing.signatures import create_source_paths, directory_signature


def test_source_paths_signature_is_stable(valid_graph_path, valid_nodes_path):
    first = create_source_paths(valid_graph_path, valid_nodes_path)
    second = create_source_paths(valid_graph_path, valid_nodes_path)

    assert first.signature == second.signature
    assert first.graph_path.endswith("tests/fixtures/valid_small_graph/graph.py")
    assert first.nodes_path.endswith("tests/fixtures/valid_small_graph/nodes")


def test_directory_signature_changes_when_child_content_changes(tmp_path):
    nodes_path = tmp_path / "nodes"
    nodes_path.mkdir()
    node_path = nodes_path / "node.py"
    node_path.write_text('NODE = {"id": "a", "label": "A"}\n', encoding="utf-8")

    before = directory_signature(nodes_path)
    node_path.write_text('NODE = {"id": "a", "label": "A changed"}\n', encoding="utf-8")
    after = directory_signature(nodes_path)

    assert before != after

