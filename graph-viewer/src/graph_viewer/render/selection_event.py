from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def extract_selected_node_id(event_payload: Any) -> str | None:
    points = _get_path(event_payload, ("selection", "points"))
    if not points:
        return None
    first_point = points[0]
    customdata = _get_value(first_point, "customdata")
    if customdata is None:
        return None
    if isinstance(customdata, str):
        return customdata or None
    if isinstance(customdata, Sequence) and customdata and not isinstance(customdata, bytes):
        first_value = customdata[0]
        return str(first_value) if first_value is not None else None
    return str(customdata)


def _get_path(value: Any, path: tuple[str, ...]) -> Any:
    current = value
    for part in path:
        current = _get_value(current, part)
        if current is None:
            return None
    return current


def _get_value(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)

