from __future__ import annotations

from graph_viewer.app import format_error_reports, load_graph_for_render


def test_load_graph_for_render_returns_renderable_data(valid_graph_path, valid_nodes_path):
    result = load_graph_for_render(str(valid_graph_path), str(valid_nodes_path))

    assert result.errors == ()
    assert result.render_data is not None
    assert set(result.render_data.node_ids) == {"graph-only", "node-a", "node-b", "node-c"}
    assert result.figure is not None


def test_load_graph_for_render_blocks_invalid_payload(invalid_graphs_path, tmp_path):
    nodes_path = tmp_path / "nodes"
    nodes_path.mkdir()

    result = load_graph_for_render(str(invalid_graphs_path / "missing_target_graph.py"), str(nodes_path))

    assert result.render_data is None
    assert result.figure is None
    assert [error.code for error in result.errors] == ["dangling_edge"]


def test_format_error_reports_includes_actionable_context(invalid_graphs_path, tmp_path):
    nodes_path = tmp_path / "nodes"
    nodes_path.mkdir()
    result = load_graph_for_render(str(invalid_graphs_path / "malformed_graph.py"), str(nodes_path))

    messages = format_error_reports(result.errors)

    assert messages
    assert all(message.startswith("ERROR") for message in messages)
    assert any("$.directed" in message for message in messages)

