"""Escritura minima de memoria."""


def format_memory_update(item: str, reason: str) -> dict[str, str]:
    """Prepara una actualizacion de memoria sin persistirla."""
    return {
        "item": item,
        "reason": reason,
    }
