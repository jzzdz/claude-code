"""Utilidades de rutas del paquete."""

from pathlib import Path


def package_root() -> Path:
    """Devuelve la raiz del paquete."""
    return Path(__file__).resolve().parents[1]
