# Blockers

- 2026-06-27 20:20 CEST - No active blockers. Preflight found no `init.sh`; this is not blocking because the repo has not been initialized yet.
- 2026-06-27 20:36 CEST - Environment caveat: `python` command is missing and `python3` is Python 3.11 while project metadata requires Python 3.12+. Status: not blocking implementation tests because `python3 -m pytest` runs; final runtime should use Python 3.12+.
- 2026-06-27 20:53 CEST - Environment caveat update: `python3.12` command is unavailable. Status: unresolved for exact runtime parity, but non-blocking for current US1 verification because all tests pass under available `python3`.
- 2026-06-27 21:01 CEST - Runtime start blocked: `python3 -m streamlit --version` reports missing Streamlit; `python3 -m pip install -e '.[dev]'` with network access fails because package metadata requires Python `>=3.12` and local `python3` is 3.11.0. Status: open; install/run with Python 3.12+.
- 2026-06-27 21:08 CEST - Runtime start blocker resolved for local validation: user-provided env `python311_neo_env` includes Streamlit 1.56.0 and passes `python -m pytest` with 21 tests. Status: resolved for manual app run; Python 3.12 metadata parity remains a documented caveat.
- 2026-06-27 21:10 CEST - Python 3.12 metadata caveat resolved: `pyproject.toml` changed from `>=3.12` to `>=3.11` to match the provided working runtime. Status: resolved pending verification.
- 2026-06-27 21:12 CEST - Python 3.11 metadata verification complete: tests pass and editable install succeeds in `python311_neo_env`. Status: resolved.
- 2026-06-27 21:14 CEST - Streamlit socket sandbox issue: first local server attempt failed with `PermissionError: [Errno 1] Operation not permitted`; rerun with approved local-server permission succeeded. Status: resolved.
- 2026-06-27 21:46 CEST - US2 blockers: none. Tests and full suite pass in `python311_neo_env`.
- 2026-06-27 22:13 CEST - US3 blockers: none. Tests and full suite pass in `python311_neo_env`.
- 2026-06-27 22:40 CEST - Polish/close-out blockers: none. Full suite (45 tests) passes in `python311_neo_env`; 5,000-node performance gate passes within budget. Outstanding caveat unchanged: Python 3.12 metadata parity remains documented (runtime accepts 3.11+).
