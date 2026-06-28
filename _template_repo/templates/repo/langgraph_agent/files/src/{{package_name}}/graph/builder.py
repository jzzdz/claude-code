"""Builder minimo del grafo.

Este stub evita acoplar el bootstrap a dependencias externas. Una feature
posterior puede sustituirlo por un grafo real.
"""


def build_graph() -> dict[str, str]:
    """Devuelve una representacion minima del grafo."""
    return {
        "name": "{{project_name}}",
        "template_id": "{{template_id}}",
    }
