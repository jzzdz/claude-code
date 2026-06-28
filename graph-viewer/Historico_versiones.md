# Historico_versiones

- 2026-06-27 20:20 CEST - `0.1.0-dev`: Started MVP implementation scope for `001-interactive-graph-viewer` (`T001`-`T031` only).
- 2026-06-27 20:24 CEST - `0.1.0-dev.setup`: Added Python package metadata, package skeleton, test placeholders, and runtime graph schema.
- 2026-06-27 20:28 CEST - `0.1.0-dev.foundation`: Added valid, invalid, and generated-large graph fixtures plus shared test helpers and configuration constants.
- 2026-06-27 20:36 CEST - `0.1.0-dev.us1-tests`: Added US1 unit and integration tests and confirmed red before implementation.
- 2026-06-27 20:53 CEST - `0.1.0-dev.us1-mvp`: Implemented MVP load, validation, graph build, deterministic layout, Plotly render, Streamlit UI, cache boundaries, and green US1 tests.
- 2026-06-27 21:01 CEST - `0.1.0-dev.us1-runtime-note`: Recorded that local Streamlit start is blocked until Python 3.12+ is available.
- 2026-06-27 21:08 CEST - `0.1.0-dev.us1-runtime-env`: Verified user-provided `python311_neo_env` with Streamlit 1.56.0 and green tests.
- 2026-06-27 21:10 CEST - `0.1.0-dev.py311`: Updated package metadata to accept Python 3.11+.
- 2026-06-27 21:12 CEST - `0.1.0-dev.py311-verified`: Verified tests and editable install in `python311_neo_env`.
- 2026-06-27 21:14 CEST - `0.1.0-dev.streamlit-local`: Started local Streamlit MVP server for validation.
- 2026-06-27 21:20 CEST - `0.1.0-dev.nested-subgraph-test`: Added fixture and integration test for a 4-node graph with a 5-node subgraph stored on node 2 metadata.
- 2026-06-27 21:38 CEST - `0.1.0-dev.us2-tests`: Added US2 selection/highlight tests and confirmed red before implementation.
- 2026-06-27 21:46 CEST - `0.1.0-dev.us2-highlight`: Implemented Plotly selection capture, pure neighbor highlighting, focused edge rendering, clear/replace selection behavior, and green US2/full tests.
- 2026-06-27 21:49 CEST - `0.1.0-dev.us2-streamlit-width`: Replaced deprecated Streamlit `use_container_width` usage with `width="stretch"` and revalidated the full suite.
- 2026-06-27 22:06 CEST - `0.1.0-dev.us3-tests`: Added US3 search/centering tests and confirmed red before implementation.
- 2026-06-27 22:13 CEST - `0.1.0-dev.us3-search-center`: Implemented label search, result selection, viewport centering, no-result stability, and green US3/full tests.
- 2026-06-27 22:40 CEST - `0.1.0`: Closed Polish/cross-cutting phase `T051`-`T055`: documented `README.md` and `docs/architecture.md`, recorded full-suite run (45 passed) and quickstart scenario validation in `quickstart.md`, and confirmed the 5,000-node performance gate passes within budget without LOD tuning. Feature `001-interactive-graph-viewer` complete.
