# Decisions

## 2026-06-27 20:20 CEST - Keep US1 implementation layered and pure below Streamlit

- What: Parsing, validation, graph building, layout, and render preparation will be implemented as importable pure modules; `app.py` only wires Streamlit UI and cache boundaries.
- Why: The constitution requires isolated testability and explicit layer boundaries, and US1 tests need to verify core behavior without mounting Streamlit.
- Alternatives discarded: A Streamlit-first implementation was rejected because it would couple validation/render logic to UI reruns and weaken TDD coverage.

## 2026-06-27 20:20 CEST - Use the global `implementador` role as non-writing review support

- What: A subagent with role `implementador` was started for an acotated read-only risk/test-coverage review while the main thread owns edits.
- Why: The user requested identification of the subagent, and centralizing writes avoids conflicts in `tasks.md` and `progress/`.
- Alternatives discarded: Parallel code editing was rejected because the project is being initialized from scratch and most files are interdependent during TDD.

## 2026-06-27 20:45 CEST - Use deterministic circular layout for large graphs in US1

- What: `compute_layout()` uses a deterministic circular layout for graphs at or above the large-graph threshold, and uses ForceAtlas2 when available or spring layout for smaller graphs.
- Why: The 5,000-node performance gate is part of the constitution; NetworkX force-directed layouts can be too slow for MVP-scale large fixtures without adding new dependencies.
- Alternatives discarded: Always using spring/ForceAtlas2 was rejected as a performance risk; adding a new layout dependency was rejected because the plan does not justify one for US1.

## 2026-06-27 21:10 CEST - Accept Python 3.11 runtime

- What: Project metadata now declares `requires-python = ">=3.11"`.
- Why: The available maintained runtime for this repo is `python311_neo_env`, and the full US1 suite passes on Python 3.11.0.
- Alternatives discarded: Keeping `>=3.12` was rejected because it blocks local install/run in the provided environment without adding value for the current code.

## 2026-06-27 21:32 CEST - Keep US2 selection logic outside Streamlit

- What: Plotly event parsing, selected-node state, neighbor calculation, and trace recoloring will live in pure render modules; Streamlit only stores session state and passes event data through.
- Why: The constitution requires isolated testability, and the render interaction contract explicitly separates Streamlit event capture from pure selection/render preparation.
- Alternatives discarded: Computing neighbors directly in `app.py` was rejected because it would couple UI reruns to graph logic and make selection behavior harder to test.

## 2026-06-27 22:01 CEST - Represent search centering as Plotly axis ranges

- What: US3 will calculate viewport ranges in a pure `render.viewport` module and store them in `RenderGraphData.viewport`; `build_figure()` will apply those ranges to Plotly axes.
- Why: This keeps search centering testable without Streamlit and matches the render interaction contract's viewport boundary.
- Alternatives discarded: Calling Plotly/Streamlit imperative camera APIs from `app.py` was rejected because it would be less testable and more fragile under reruns.

## 2026-06-27 22:40 CEST - Close Polish without changing edge level-of-detail defaults

- What: `T055` left `DENSE_EDGE_CAP` and other `config.py` LOD defaults unchanged, and the feature was declared complete after documenting README/architecture and recording quickstart validation.
- Why: `tests/integration/test_5000_node_performance_fixture.py` passes in ~0.03s against a 5.0s budget, so the performance gate shows no miss; `T055` is conditional on a miss.
- Alternatives discarded: Pre-emptively lowering the edge cap was rejected as premature optimization with no measured need; it could degrade visual fidelity on dense graphs that already render within budget.
