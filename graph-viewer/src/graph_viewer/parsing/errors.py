from __future__ import annotations

from dataclasses import dataclass

from graph_viewer.graph.model import ValidationErrorReport, ValidationResult


@dataclass(frozen=True)
class SourceLoadResult:
    payload: dict | None = None
    errors: tuple[ValidationErrorReport, ...] = ()
    warnings: tuple[ValidationErrorReport, ...] = ()

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


def error_report(code: str, path: str, message: str) -> ValidationErrorReport:
    return ValidationErrorReport(code=code, path=path, message=message, severity="error")


def warning_report(code: str, path: str, message: str) -> ValidationErrorReport:
    return ValidationErrorReport(code=code, path=path, message=message, severity="warning")


__all__ = [
    "SourceLoadResult",
    "ValidationErrorReport",
    "ValidationResult",
    "error_report",
    "warning_report",
]

