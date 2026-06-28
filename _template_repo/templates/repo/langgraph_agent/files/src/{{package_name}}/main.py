"""Punto de entrada minimo de {{project_name}}."""

from .graph.builder import build_graph


def run() -> str:
    """Construye el runtime minimo y devuelve un mensaje de smoke test."""
    graph = build_graph()
    return f"{{project_name}} ready: {graph['name']}"


if __name__ == "__main__":
    print(run())
