"""Nodos iniciales del grafo."""

from .state import AgentState


def planner_node(state: AgentState) -> AgentState:
    """Nodo planner minimo."""
    state.next_step = "executor"
    return state


def executor_node(state: AgentState) -> AgentState:
    """Nodo executor minimo."""
    state.messages.append("executed")
    state.next_step = "reviewer"
    return state


def reviewer_node(state: AgentState) -> AgentState:
    """Nodo reviewer minimo."""
    state.next_step = "done"
    return state
