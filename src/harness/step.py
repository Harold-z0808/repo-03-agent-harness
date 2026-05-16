"""Single-step abstractions for the hand-written agent loop."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class StepKind(StrEnum):
    """Types of steps in an agent loop."""

    MODEL = "model"
    TOOL = "tool"
    OBSERVATION = "observation"
    FINAL = "final"
    ERROR = "error"


@dataclass(frozen=True)
class AgentStep:
    """One auditable step in an agent execution."""

    kind: StepKind
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

