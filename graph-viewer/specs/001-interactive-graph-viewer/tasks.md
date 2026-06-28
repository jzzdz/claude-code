# Tasks: Interactive Graph Viewer

**Input**: Design documents from `/specs/001-interactive-graph-viewer/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: TDD is mandatory. In each user story, test tasks come before
implementation tasks and are expected to fail before the story implementation
starts.

**Organization**: Tasks are grouped by user story so US1 delivers the MVP,
US2 adds neighbor highlighting, and US3 adds search/centering.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on incomplete tasks
- **[Story]**: User story label for story phases only
- Every task includes exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python package, dependency metadata, runtime schema resource, and directory skeleton.

- [X] T001 Create Python package metadata with Streamlit, NetworkX, Plotly, jsonschema, and pytest dependencies in `pyproject.toml`
- [X] T002 Create package skeleton files in `src/graph_viewer/__init__.py`, `src/graph_viewer/parsing/__init__.py`, `src/graph_viewer/validation/__init__.py`, `src/graph_viewer/graph/__init__.py`, `src/graph_viewer/layout/__init__.py`, and `src/graph_viewer/render/__init__.py`
- [X] T003 Create test directory placeholders in `tests/unit/parsing/.gitkeep`, `tests/unit/validation/.gitkeep`, `tests/unit/graph/.gitkeep`, `tests/unit/layout/.gitkeep`, `tests/unit/render/.gitkeep`, `tests/integration/.gitkeep`, `tests/fixtures/valid_small_graph/.gitkeep`, `tests/fixtures/invalid_graphs/.gitkeep`, and `tests/fixtures/generated_large_graphs/.gitkeep`
- [X] T004 Copy the runtime JSON Schema contract from `specs/001-interactive-graph-viewer/contracts/graph-input.schema.json` to `src/graph_viewer/validation/graph-input.schema.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create shared fixtures and app constants required by all user stories.

**Critical**: No user story implementation starts until this phase is complete.

- [X] T005 [P] Create valid graph fixture files in `tests/fixtures/valid_small_graph/graph.py`, `tests/fixtures/valid_small_graph/nodes/node_a.py`, `tests/fixtures/valid_small_graph/nodes/node_b.py`, and `tests/fixtures/valid_small_graph/nodes/node_c.py`
- [X] T006 [P] Create invalid graph fixture files in `tests/fixtures/invalid_graphs/missing_target_graph.py`, `tests/fixtures/invalid_graphs/duplicate_nodes_graph.py`, `tests/fixtures/invalid_graphs/empty_graph.py`, and `tests/fixtures/invalid_graphs/malformed_graph.py`
- [X] T007 [P] Create deterministic large graph fixture generator in `tests/fixtures/generated_large_graphs/generate_large_graph.py`
- [X] T008 Create shared pytest fixture helpers for paths, valid payloads, invalid payloads, and 5,000-node payloads in `tests/conftest.py`
- [X] T009 Create shared constants for layout seeds, render colors, selected-neighbor colors, and dense-edge caps in `src/graph_viewer/config.py`

**Checkpoint**: Foundation ready. User story test tasks can now be written and run red.

---

## Phase 3: User Story 1 - Load and Explore a Valid Graph (Priority: P1, MVP)

**Goal**: User enters a graph Python file path and node directory path, receives validation feedback, and can view a valid graph with automatic layout plus pan/zoom.

**Independent Test**: Load the valid fixture graph, verify nodes and edges render, verify invalid fixtures produce clear errors before render, and verify a 5,000-node fixture can be prepared without recomputing cached parse/layout on unchanged inputs.

### Tests for User Story 1

> Write these tests first and confirm they fail before starting T020.

- [X] T010 [P] [US1] Add failing tests for source path signatures and cache key stability in `tests/unit/parsing/test_signatures.py`
- [X] T011 [P] [US1] Add failing tests for trusted Python graph and node source extraction in `tests/unit/parsing/test_python_sources.py`
- [X] T012 [P] [US1] Add failing tests for schema loading and jsonschema error collection in `tests/unit/validation/test_schema.py`
- [X] T013 [P] [US1] Add failing tests for duplicate node ids, dangling edges, empty graphs, and warning/error reports in `tests/unit/validation/test_semantic.py`
- [X] T014 [P] [US1] Add failing tests for GraphModel construction, directed graph handling, label index, and neighbor index in `tests/unit/graph/test_builder.py`
- [X] T015 [P] [US1] Add failing tests for deterministic layout output and finite node positions in `tests/unit/layout/test_positions.py`
- [X] T016 [P] [US1] Add failing tests for initial Plotly node/edge render data, WebGL-compatible traces, and node `customdata` ids in `tests/unit/render/test_plotly_renderer.py`
- [X] T017 [P] [US1] Add failing integration tests for valid load, invalid input blocking render, and error display data in `tests/integration/test_load_validate_render_flow.py`
- [X] T018 [P] [US1] Add failing integration tests for Streamlit cache boundaries around parsing, validation, layout, and render preparation in `tests/integration/test_streamlit_cache_boundaries.py`
- [X] T019 [P] [US1] Add failing integration test for the 5,000-node performance fixture parse/layout/render-preparation budget in `tests/integration/test_5000_node_performance_fixture.py`

### Implementation for User Story 1

- [X] T020 [US1] Implement parse error and validation error report types in `src/graph_viewer/parsing/errors.py`
- [X] T021 [US1] Implement deterministic file and directory signatures for Streamlit cache keys in `src/graph_viewer/parsing/signatures.py`
- [X] T022 [US1] Implement trusted Python source loading for `get_graph`, `GRAPH`, `get_node`, and `NODE` exports in `src/graph_viewer/parsing/python_sources.py`
- [X] T023 [US1] Implement JSON Schema loading and jsonschema error normalization in `src/graph_viewer/validation/schema.py`
- [X] T024 [US1] Implement semantic validation for duplicate ids, dangling edges, empty graphs, and label trimming in `src/graph_viewer/validation/semantic.py`
- [X] T025 [US1] Implement GraphNode, GraphEdge, GraphModel, SourcePaths, RawGraphPayload, LayoutPositions, RenderGraphData, SelectionState, SearchState, and ValidationErrorReport in `src/graph_viewer/graph/model.py`
- [X] T026 [US1] Implement payload-to-NetworkX Graph/DiGraph construction with id, label, neighbor, and signature indexes in `src/graph_viewer/graph/builder.py`
- [X] T027 [US1] Implement automatic deterministic layout with ForceAtlas2 first and spring-layout fallback in `src/graph_viewer/layout/positions.py`
- [X] T028 [US1] Implement Plotly figure construction for initial graph render with node `customdata`, node text, WebGL-compatible node trace, and edge level-of-detail in `src/graph_viewer/render/plotly_renderer.py`
- [X] T029 [US1] Implement Streamlit cached load pipeline for signatures, parsing, validation, graph build, layout, and render preparation in `src/graph_viewer/app.py`
- [X] T030 [US1] Implement Streamlit path inputs, load action, validation error display, and initial chart rendering in `src/graph_viewer/app.py`
- [X] T031 [US1] Run and fix the US1 test suite covering `tests/unit/parsing/test_signatures.py`, `tests/unit/parsing/test_python_sources.py`, `tests/unit/validation/test_schema.py`, `tests/unit/validation/test_semantic.py`, `tests/unit/graph/test_builder.py`, `tests/unit/layout/test_positions.py`, `tests/unit/render/test_plotly_renderer.py`, `tests/integration/test_load_validate_render_flow.py`, `tests/integration/test_streamlit_cache_boundaries.py`, and `tests/integration/test_5000_node_performance_fixture.py`

**Checkpoint**: MVP works independently: valid graph loads, invalid graph errors are user-facing, graph renders, and pan/zoom is available.

---

## Phase 4: User Story 2 - Highlight Direct Neighbors (Priority: P2)

**Goal**: User selects a Plotly-rendered node and sees the selected node plus direct NetworkX neighbors highlighted while unrelated graph elements are de-emphasized.

**Independent Test**: With a known adjacency fixture, simulate the `st.plotly_chart` selection payload, extract the node id from `customdata`, compute direct neighbors through the graph model, and verify rebuilt Plotly traces recolor selected, neighbor, and unrelated nodes correctly.

### Tests for User Story 2

> Write these tests first and confirm they fail before starting T037.

- [X] T032 [P] [US2] Add failing tests for extracting the selected node id from a Streamlit `st.plotly_chart` Plotly selection event payload in `tests/unit/render/test_selection_event.py`
- [X] T033 [P] [US2] Add failing tests for calculating selected node direct neighbors from the NetworkX-backed GraphModel in `tests/unit/render/test_selection.py`
- [X] T034 [P] [US2] Add failing tests for rebuilding/recoloring Plotly node and edge traces for selected, neighbor, and dimmed states in `tests/unit/render/test_plotly_selection_render.py`
- [X] T035 [P] [US2] Add failing integration test for selection rerun flow from Plotly event payload to highlighted graph output in `tests/integration/test_plotly_selection_flow.py`

### Implementation for User Story 2

- [X] T036 [US2] Implement Plotly selection payload parsing from `st.plotly_chart(..., on_select="rerun", selection_mode=["points"])` return data in `src/graph_viewer/render/selection_event.py`
- [X] T037 [US2] Implement selected-node state and direct-neighbor calculation using the NetworkX-backed GraphModel in `src/graph_viewer/render/selection.py`
- [X] T038 [US2] Update Plotly trace preparation to recolor/rebuild selected nodes, direct neighbors, dimmed nodes, selected edges, and focused edge segments in `src/graph_viewer/render/plotly_renderer.py`
- [X] T039 [US2] Integrate `st.plotly_chart` selection capture, selected node session state, and rerun-safe highlight updates in `src/graph_viewer/app.py`
- [X] T040 [US2] Implement clear-selection and replace-selection behavior when selecting another node or loading another graph in `src/graph_viewer/app.py`
- [X] T041 [US2] Run and fix the US2 test suite covering `tests/unit/render/test_selection_event.py`, `tests/unit/render/test_selection.py`, `tests/unit/render/test_plotly_selection_render.py`, and `tests/integration/test_plotly_selection_flow.py`

**Checkpoint**: Selecting a node highlights that node and its direct neighbors with explicit Plotly event handling and trace rebuilding.

---

## Phase 5: User Story 3 - Search and Center a Node by Label (Priority: P3)

**Goal**: User searches by node label, chooses among multiple matches when needed, and the view centers on the selected result without disrupting current graph state on no-result searches.

**Independent Test**: Load a known graph, run exact and partial label searches, verify result ordering, verify no-result behavior, and verify viewport ranges center the active node.

### Tests for User Story 3

> Write these tests first and confirm they fail before starting T046.

- [X] T042 [P] [US3] Add failing tests for exact, case-insensitive, partial, multiple-match, and no-result label search in `tests/unit/graph/test_queries.py`
- [X] T043 [P] [US3] Add failing tests for SearchState result ordering and no-result messages in `tests/unit/render/test_search_state.py`
- [X] T044 [P] [US3] Add failing tests for viewport axis range calculation that centers a node from layout positions in `tests/unit/render/test_viewport.py`
- [X] T045 [P] [US3] Add failing integration test for label search, result selection, centering, and no-result stability in `tests/integration/test_search_center_flow.py`

### Implementation for User Story 3

- [X] T046 [US3] Implement exact-first and partial label search over the GraphModel label index in `src/graph_viewer/graph/queries.py`
- [X] T047 [US3] Implement SearchState creation, multiple-match result selection, and no-result messaging in `src/graph_viewer/render/search.py`
- [X] T048 [US3] Implement viewport centering and axis range calculation from layout positions in `src/graph_viewer/render/viewport.py`
- [X] T049 [US3] Integrate search input, result selector, active search result state, and viewport updates in `src/graph_viewer/app.py`
- [X] T050 [US3] Run and fix the US3 test suite covering `tests/unit/graph/test_queries.py`, `tests/unit/render/test_search_state.py`, `tests/unit/render/test_viewport.py`, and `tests/integration/test_search_center_flow.py`

**Checkpoint**: Search by label locates and centers nodes, handles multiple matches, and reports no-result searches without destabilizing the current view.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the whole feature, document operation, and tune performance without changing story scope.

- [X] T051 [P] Document local setup, test commands, and Streamlit run command in `README.md`
- [X] T052 [P] Add developer notes for module boundaries, cache strategy, and Plotly selection flow in `docs/architecture.md`
- [X] T053 Run full pytest suite from `pyproject.toml` and record any remaining failures in `specs/001-interactive-graph-viewer/quickstart.md`
- [X] T054 Run the quickstart validation scenarios from `specs/001-interactive-graph-viewer/quickstart.md`
- [X] T055 Tune 5,000-node edge level-of-detail defaults in `src/graph_viewer/config.py` only if `tests/integration/test_5000_node_performance_fixture.py` shows a performance miss (no tuning needed; perf test passes ~0.03s vs 5.0s budget)

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 Setup: no dependencies.
- Phase 2 Foundational: depends on Phase 1.
- Phase 3 US1 MVP: depends on Phase 2 and blocks US2/US3 because it creates the load, validation, graph, layout, and initial render pipeline.
- Phase 4 US2: depends on US1 because it reuses GraphModel, Plotly render data, and the Streamlit chart.
- Phase 5 US3: depends on US1 and can run in parallel with US2 after the MVP pipeline exists.
- Phase 6 Polish: depends on the selected delivery scope being complete.

### User Story Dependencies

- US1: independent MVP.
- US2: depends on US1 render data and GraphModel.
- US3: depends on US1 GraphModel, layout positions, and app state.

### TDD Order Within Each User Story

- US1: T010-T019 must be written and observed failing before T020-T031.
- US2: T032-T035 must be written and observed failing before T036-T041.
- US3: T042-T045 must be written and observed failing before T046-T050.

---

## Parallel Opportunities

- Setup tasks T002, T003, and T004 can run in parallel after T001.
- Foundational fixture tasks T005, T006, and T007 can run in parallel.
- US1 test tasks T010-T019 can run in parallel once fixtures exist.
- US2 test tasks T032-T035 can run in parallel after US1 render contracts exist.
- US3 test tasks T042-T045 can run in parallel after US1 graph/layout contracts exist.
- Documentation tasks T051 and T052 can run in parallel after implementation stabilizes.

## Parallel Example: User Story 2

```bash
Task: "T032 Add failing tests for extracting the selected node id from a Streamlit st.plotly_chart Plotly selection event payload in tests/unit/render/test_selection_event.py"
Task: "T033 Add failing tests for calculating selected node direct neighbors from the NetworkX-backed GraphModel in tests/unit/render/test_selection.py"
Task: "T034 Add failing tests for rebuilding/recoloring Plotly node and edge traces for selected, neighbor, and dimmed states in tests/unit/render/test_plotly_selection_render.py"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 tests T010-T019 and confirm red.
3. Complete US1 implementation T020-T031.
4. Validate the MVP through `tests/integration/test_load_validate_render_flow.py` and `tests/integration/test_5000_node_performance_fixture.py`.

### Incremental Delivery

1. Deliver US1: path input, validation, graph model, layout, initial Plotly render, pan/zoom, caching.
2. Deliver US2: `st.plotly_chart` selection event, NetworkX neighbor lookup, trace recolor/rebuild.
3. Deliver US3: label search, multiple/no-result handling, viewport centering.
4. Run polish tasks T051-T055 before declaring the feature complete.
