from __future__ import annotations

from dataclasses import replace

from graph_viewer.app import LoadPipelineCache, PipelineDependencies, load_graph_for_render


def test_pipeline_cache_does_not_recompute_unchanged_inputs(valid_graph_path, valid_nodes_path):
    baseline = load_graph_for_render(str(valid_graph_path), str(valid_nodes_path))
    assert baseline.render_data is not None

    counts = {"parse": 0, "schema": 0, "semantic": 0, "graph": 0, "layout": 0, "render": 0}

    base_dependencies = PipelineDependencies.default()

    def counted_parse(graph_path, nodes_path):
        counts["parse"] += 1
        return base_dependencies.parse(graph_path, nodes_path)

    def counted_schema(payload):
        counts["schema"] += 1
        return base_dependencies.schema_validate(payload)

    def counted_semantic(payload):
        counts["semantic"] += 1
        return base_dependencies.semantic_validate(payload)

    def counted_graph(payload):
        counts["graph"] += 1
        return base_dependencies.build_graph(payload)

    def counted_layout(model):
        counts["layout"] += 1
        return base_dependencies.layout(model)

    def counted_render(model, layout):
        counts["render"] += 1
        return base_dependencies.render(model, layout)

    dependencies = replace(
        base_dependencies,
        parse=counted_parse,
        schema_validate=counted_schema,
        semantic_validate=counted_semantic,
        build_graph=counted_graph,
        layout=counted_layout,
        render=counted_render,
    )
    cache = LoadPipelineCache()

    first = cache.load(str(valid_graph_path), str(valid_nodes_path), dependencies)
    second = cache.load(str(valid_graph_path), str(valid_nodes_path), dependencies)

    assert first.render_data == second.render_data
    assert counts == {"parse": 1, "schema": 1, "semantic": 1, "graph": 1, "layout": 1, "render": 1}
