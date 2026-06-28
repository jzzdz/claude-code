"""Aristas y routing inicial del grafo."""

from .state import AgentState


def route_next(state: AgentState) -> str:
    """Devuelve el siguiente paso declarado en el estado."""
    return state.next_step or "planner"
