from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any

from jsonschema import Draft202012Validator

from graph_viewer.graph.model import ValidationResult
from graph_viewer.parsing.errors import error_report


@lru_cache(maxsize=1)
def load_graph_schema() -> dict[str, Any]:
    schema_path = resources.files("graph_viewer.validation").joinpath("graph-input.schema.json")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_payload_schema(payload: dict[str, Any]) -> ValidationResult:
    schema = load_graph_schema()
    validator = Draft202012Validator(schema)
    reports = tuple(
        error_report(
            "schema_validation_error",
            _format_json_path(error.absolute_path),
            error.message,
        )
        for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path))
    )
    if reports:
        return ValidationResult(payload=None, errors=reports)
    return ValidationResult(payload=payload)


def _format_json_path(parts) -> str:
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path

