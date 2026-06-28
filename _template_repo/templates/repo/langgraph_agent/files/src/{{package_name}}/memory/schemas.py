"""Schemas simples de memoria."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryItem:
    """Elemento minimo de memoria."""

    value: str
    source: str
