"""Estado base del agente."""

from dataclasses import dataclass, field


@dataclass
class AgentState:
    """Estado minimo para empezar a definir el grafo."""

    messages: list[str] = field(default_factory=list)
    next_step: str | None = None
