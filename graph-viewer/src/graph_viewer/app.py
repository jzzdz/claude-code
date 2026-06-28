from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from graph_viewer.graph.builder import build_graph_model
from graph_viewer.graph.model import (
    GraphModel,
    LayoutPositions,
    RenderGraphData,
    SearchState,
    SelectionState,
    ValidationErrorReport,
    ValidationResult,
)
from graph_viewer.layout.positions import compute_layout
from graph_viewer.parsing.errors import SourceLoadResult
from graph_viewer.parsing.python_sources import load_graph_payload
from graph_viewer.parsing.signatures import create_source_paths
from graph_viewer.render.plotly_renderer import build_figure, prepare_render_data
from graph_viewer.render.search import build_search_state, clear_search_state
from graph_viewer.render.selection import build_selection_state, clear_selection_state
from graph_viewer.render.selection_event import extract_selected_node_id
from graph_viewer.validation.schema import validate_payload_schema
from graph_viewer.validation.semantic import validate_semantics


@dataclass(frozen=True)
class LoadPipelineResult:
    render_data: RenderGraphData | None
    figure: object | None
    graph_model: GraphModel | None = None
    layout: LayoutPositions | None = None
    selection_state: SelectionState = clear_selection_state()
    search_state: SearchState = clear_search_state()
    errors: tuple[ValidationErrorReport, ...] = ()
    warnings: tuple[ValidationErrorReport, ...] = ()


@dataclass(frozen=True)
class PipelineDependencies:
    parse: Callable[[str | Path, str | Path], SourceLoadResult]
    schema_validate: Callable[[dict], ValidationResult]
    semantic_validate: Callable[[dict], ValidationResult]
    build_graph: Callable[[dict], GraphModel]
    layout: Callable[[GraphModel], LayoutPositions]
    render: Callable[[GraphModel, LayoutPositions], RenderGraphData]

    @classmethod
    def default(cls) -> "PipelineDependencies":
        return cls(
            parse=load_graph_payload,
            schema_validate=validate_payload_schema,
            semantic_validate=validate_semantics,
            build_graph=build_graph_model,
            layout=compute_layout,
            render=prepare_render_data,
        )


class LoadPipelineCache:
    def __init__(self) -> None:
        self._parsed: dict[str, SourceLoadResult] = {}
        self._schema: dict[str, ValidationResult] = {}
        self._semantic: dict[str, ValidationResult] = {}
        self._graph: dict[str, GraphModel] = {}
        self._layout: dict[str, LayoutPositions] = {}
        self._render: dict[str, RenderGraphData] = {}

    def load(
        self,
        graph_path: str | Path,
        nodes_path: str | Path,
        dependencies: PipelineDependencies | None = None,
    ) -> LoadPipelineResult:
        dependencies = dependencies or PipelineDependencies.default()
        try:
            source_paths = create_source_paths(graph_path, nodes_path)
        except OSError:
            parse_result = dependencies.parse(graph_path, nodes_path)
            return LoadPipelineResult(
                render_data=None,
                figure=None,
                errors=parse_result.errors,
                warnings=parse_result.warnings,
            )

        parse_result = self._parsed.get(source_paths.signature)
        if parse_result is None:
            parse_result = dependencies.parse(graph_path, nodes_path)
            self._parsed[source_paths.signature] = parse_result
        if parse_result.errors or parse_result.payload is None:
            return LoadPipelineResult(
                render_data=None,
                figure=None,
                errors=parse_result.errors,
                warnings=parse_result.warnings,
            )

        payload = parse_result.payload

        schema_result = self._schema.get(source_paths.signature)
        if schema_result is None:
            schema_result = dependencies.schema_validate(payload)
            self._schema[source_paths.signature] = schema_result
        if schema_result.errors or schema_result.payload is None:
            return LoadPipelineResult(
                render_data=None,
                figure=None,
                errors=schema_result.errors,
                warnings=parse_result.warnings + schema_result.warnings,
            )

        semantic_result = self._semantic.get(source_paths.signature)
        if semantic_result is None:
            semantic_result = dependencies.semantic_validate(schema_result.payload)
            self._semantic[source_paths.signature] = semantic_result
        if semantic_result.errors or semantic_result.payload is None:
            return LoadPipelineResult(
                render_data=None,
                figure=None,
                errors=semantic_result.errors,
                warnings=parse_result.warnings + semantic_result.warnings,
            )

        graph_model = self._graph.get(source_paths.signature)
        if graph_model is None:
            graph_model = dependencies.build_graph(semantic_result.payload)
            self._graph[source_paths.signature] = graph_model

        layout = self._layout.get(graph_model.signature)
        if layout is None:
            layout = dependencies.layout(graph_model)
            self._layout[graph_model.signature] = layout

        render_data = self._render.get(layout.signature)
        if render_data is None:
            render_data = dependencies.render(graph_model, layout)
            self._render[layout.signature] = render_data

        return LoadPipelineResult(
            render_data=render_data,
            figure=build_figure(render_data),
            graph_model=graph_model,
            layout=layout,
            search_state=clear_search_state(),
            warnings=parse_result.warnings + semantic_result.warnings,
        )


_DEFAULT_CACHE = LoadPipelineCache()


def load_graph_for_render(graph_path: str | Path, nodes_path: str | Path) -> LoadPipelineResult:
    return _DEFAULT_CACHE.load(graph_path, nodes_path)


def update_render_for_selection_event(
    loaded_graph: LoadPipelineResult,
    event_payload: object,
) -> LoadPipelineResult:
    selected_node_id = extract_selected_node_id(event_payload)
    return update_render_for_selected_node(loaded_graph, selected_node_id)


def update_render_for_selected_node(
    loaded_graph: LoadPipelineResult,
    selected_node_id: str | None,
) -> LoadPipelineResult:
    if (
        selected_node_id is None
        or loaded_graph.graph_model is None
        or loaded_graph.layout is None
        or loaded_graph.render_data is None
    ):
        return LoadPipelineResult(
            render_data=loaded_graph.render_data,
            figure=loaded_graph.figure,
            graph_model=loaded_graph.graph_model,
            layout=loaded_graph.layout,
            selection_state=clear_selection_state(),
            search_state=loaded_graph.search_state,
            errors=loaded_graph.errors,
            warnings=loaded_graph.warnings,
        )

    selection_state = build_selection_state(loaded_graph.graph_model, selected_node_id)
    if selection_state.selected_node_id is None:
        return update_render_for_selected_node(loaded_graph, None)

    render_data = prepare_render_data(
        loaded_graph.graph_model,
        loaded_graph.layout,
        selection=selection_state,
        search=loaded_graph.search_state,
        viewport=loaded_graph.render_data.viewport,
    )
    return LoadPipelineResult(
        render_data=render_data,
        figure=build_figure(render_data),
        graph_model=loaded_graph.graph_model,
        layout=loaded_graph.layout,
        selection_state=selection_state,
        search_state=loaded_graph.search_state,
        errors=loaded_graph.errors,
        warnings=loaded_graph.warnings,
    )


def update_render_for_search(
    loaded_graph: LoadPipelineResult,
    query: str,
    *,
    active_node_id: str | None = None,
) -> LoadPipelineResult:
    if loaded_graph.graph_model is None or loaded_graph.layout is None or loaded_graph.render_data is None:
        return loaded_graph

    previous_viewport = loaded_graph.render_data.viewport
    search_state = build_search_state(
        loaded_graph.graph_model,
        query,
        active_node_id=active_node_id,
    )
    render_data = prepare_render_data(
        loaded_graph.graph_model,
        loaded_graph.layout,
        selection=loaded_graph.selection_state,
        search=search_state,
        viewport=previous_viewport if search_state.active_node_id is None else None,
    )
    return LoadPipelineResult(
        render_data=render_data,
        figure=build_figure(render_data),
        graph_model=loaded_graph.graph_model,
        layout=loaded_graph.layout,
        selection_state=loaded_graph.selection_state,
        search_state=search_state,
        errors=loaded_graph.errors,
        warnings=loaded_graph.warnings,
    )


def format_error_reports(reports: tuple[ValidationErrorReport, ...]) -> list[str]:
    return [
        f"{report.severity.upper()} [{report.code}] {report.path}: {report.message}"
        for report in reports
    ]


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="Graph Viewer", layout="wide")
    st.title("Graph Viewer")

    graph_path = st.text_input("Graph Python file path")
    nodes_path = st.text_input("Node Python directory path")
    load_requested = st.button("Load graph", type="primary")

    if load_requested:
        st.session_state["loaded_graph_result"] = load_graph_for_render(graph_path, nodes_path)
        st.session_state["selected_node_id"] = None
        st.session_state["search_query"] = ""
        st.session_state["active_search_node_id"] = None

    loaded_graph = st.session_state.get("loaded_graph_result")
    if loaded_graph is None:
        return

    selected_node_id = st.session_state.get("selected_node_id")
    result = update_render_for_selected_node(loaded_graph, selected_node_id)

    st.divider()
    search_query = st.text_input(
        "Search node label",
        value=st.session_state.get("search_query", ""),
        key="search-query-input",
    )
    search_requested = st.button("Search")
    if search_requested:
        st.session_state["search_query"] = search_query
        st.session_state["active_search_node_id"] = None
        result = update_render_for_search(result, search_query)
        st.session_state["loaded_graph_result"] = result
    elif st.session_state.get("search_query"):
        result = update_render_for_search(
            result,
            st.session_state["search_query"],
            active_node_id=st.session_state.get("active_search_node_id"),
        )

    if len(result.search_state.matches) > 1:
        labels_by_id = {
            node_id: result.graph_model.node_by_id[node_id].label
            for node_id in result.search_state.matches
        }
        current_index = result.search_state.matches.index(result.search_state.active_node_id)
        selected_match = st.selectbox(
            "Search results",
            options=result.search_state.matches,
            index=current_index,
            format_func=lambda node_id: labels_by_id[node_id],
        )
        if selected_match != result.search_state.active_node_id:
            st.session_state["active_search_node_id"] = selected_match
            result = update_render_for_search(result, result.search_state.query, active_node_id=selected_match)
            st.session_state["loaded_graph_result"] = result

    if result.search_state.message:
        if result.search_state.matches:
            st.info(result.search_state.message)
        else:
            st.warning(result.search_state.message)

    for warning in result.warnings:
        st.warning(f"[{warning.code}] {warning.path}: {warning.message}")
    if result.errors:
        for message in format_error_reports(result.errors):
            st.error(message)
        return

    if result.selection_state.selected_node_id is not None:
        if st.button("Clear selection"):
            st.session_state["selected_node_id"] = None
            st.rerun()

    if result.figure is not None:
        event_payload = st.plotly_chart(
            result.figure,
            width="stretch",
            config={"scrollZoom": True},
            on_select="rerun",
            selection_mode=["points"],
            key="graph-viewer-plotly-chart",
        )
        next_selected_node_id = extract_selected_node_id(event_payload)
        if next_selected_node_id and next_selected_node_id != st.session_state.get("selected_node_id"):
            st.session_state["selected_node_id"] = next_selected_node_id
            st.rerun()


if __name__ == "__main__":
    main()
