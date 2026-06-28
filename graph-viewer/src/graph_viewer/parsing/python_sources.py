from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

from graph_viewer.parsing.errors import SourceLoadResult, error_report, warning_report


def load_graph_payload(graph_path: str | Path, nodes_path: str | Path) -> SourceLoadResult:
    graph_resolved = Path(graph_path).expanduser()
    nodes_resolved = Path(nodes_path).expanduser()
    path_errors = _validate_source_paths(graph_resolved, nodes_resolved)
    if path_errors:
        return SourceLoadResult(errors=tuple(path_errors))

    graph_resolved = graph_resolved.resolve()
    nodes_resolved = nodes_resolved.resolve()

    graph_module_result = _load_module(graph_resolved)
    if isinstance(graph_module_result, SourceLoadResult):
        return graph_module_result
    graph_payload, graph_errors = _extract_dict_export(
        graph_module_result,
        getter_name="get_graph",
        constant_name="GRAPH",
        missing_code="graph_export_missing",
        invalid_code="graph_export_invalid",
        source_path=graph_resolved,
    )
    if graph_errors:
        return SourceLoadResult(errors=tuple(graph_errors))

    node_payloads: list[dict[str, Any]] = []
    warnings = []
    errors = []
    for node_file in sorted(nodes_resolved.glob("*.py"), key=lambda item: item.name):
        node_module_result = _load_module(node_file)
        if isinstance(node_module_result, SourceLoadResult):
            errors.extend(node_module_result.errors)
            continue
        node_payload, node_errors = _extract_dict_export(
            node_module_result,
            getter_name="get_node",
            constant_name="NODE",
            missing_code="node_export_missing",
            invalid_code="node_export_invalid",
            source_path=node_file,
            missing_is_warning=True,
        )
        if node_errors and node_errors[0].severity == "warning":
            warnings.extend(node_errors)
            continue
        if node_errors:
            errors.extend(node_errors)
            continue
        if node_payload is not None:
            node_payloads.append(node_payload)

    if errors:
        return SourceLoadResult(errors=tuple(errors), warnings=tuple(warnings))

    combined = dict(graph_payload or {})
    graph_nodes = list(combined.get("nodes", []))
    combined["nodes"] = graph_nodes + node_payloads
    combined.setdefault("directed", True)
    return SourceLoadResult(payload=combined, warnings=tuple(warnings))


def _validate_source_paths(graph_path: Path, nodes_path: Path):
    errors = []
    if not graph_path.exists():
        errors.append(error_report("graph_path_missing", str(graph_path), "Graph source path does not exist."))
    elif not graph_path.is_file():
        errors.append(error_report("graph_path_not_file", str(graph_path), "Graph source path must be a file."))
    elif graph_path.suffix != ".py":
        errors.append(error_report("graph_path_not_python", str(graph_path), "Graph source must be a .py file."))

    if not nodes_path.exists():
        errors.append(error_report("nodes_path_missing", str(nodes_path), "Node source directory does not exist."))
    elif not nodes_path.is_dir():
        errors.append(error_report("nodes_path_not_directory", str(nodes_path), "Node source path must be a directory."))
    return errors


def _load_module(path: Path) -> ModuleType | SourceLoadResult:
    module_name = "graph_viewer_source_" + hashlib.sha256(str(path).encode("utf-8")).hexdigest()
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return SourceLoadResult(
            errors=(error_report("python_source_load_error", str(path), "Could not load Python source."),)
        )
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # Trusted local source, but user-facing errors should be stable.
        return SourceLoadResult(
            errors=(
                error_report(
                    "python_source_execution_error",
                    str(path),
                    f"Python source failed while loading: {exc}",
                ),
            )
        )
    return module


def _extract_dict_export(
    module: ModuleType,
    *,
    getter_name: str,
    constant_name: str,
    missing_code: str,
    invalid_code: str,
    source_path: Path,
    missing_is_warning: bool = False,
) -> tuple[dict[str, Any] | None, list]:
    if hasattr(module, getter_name) and callable(getattr(module, getter_name)):
        try:
            value = getattr(module, getter_name)()
        except Exception as exc:
            return None, [
                error_report(
                    invalid_code,
                    str(source_path),
                    f"{getter_name}() failed while extracting data: {exc}",
                )
            ]
    elif hasattr(module, constant_name):
        value = getattr(module, constant_name)
    else:
        report_factory = warning_report if missing_is_warning else error_report
        return None, [
            report_factory(
                missing_code,
                str(source_path),
                f"Expected {getter_name}() or {constant_name} export.",
            )
        ]

    if not isinstance(value, dict):
        return None, [
            error_report(
                invalid_code,
                str(source_path),
                f"Expected {getter_name}() or {constant_name} to produce a dictionary.",
            )
        ]
    return value, []

