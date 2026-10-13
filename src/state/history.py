"""Bounded conversation excerpts; character counts are not token counts."""

from dataclasses import dataclass, field
from src.llm_client import Message


@dataclass
class ConversationHistory:
    """Keep recent messages plus a bounded, lossy excerpt of older content."""

    messages: list[Message] = field(default_factory=list)
    summary: str = ""
    max_characters: int = 4000

    def __post_init__(self) -> None:
        if self.max_characters < 1:
            raise ValueError("max_characters must be positive")
        self.truncate()

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self.truncate()

    def total_characters(self) -> int:
        """Count stored content characters, excluding API role/framing overhead."""
        return len(self.summary) + sum(len(m["content"]) for m in self.messages)

    def truncate(self) -> None:
        summary_budget = self.max_characters // 3
        self.summary = self.summary[-summary_budget:] if summary_budget else ""
        while self.total_characters() > self.max_characters and len(self.messages) > 1:
            removed = self.messages.pop(0)
            excerpt = f"\n{removed['role']}: {removed['content']}"
            self.summary = (self.summary + excerpt)[-summary_budget:] if summary_budget else ""
        if self.messages:
            available = self.max_characters - len(self.summary)
            self.messages[0] = {**self.messages[0], "content": self.messages[0]["content"][:available]}

    def as_messages(self) -> list[Message]:
        # Earlier user text must not be promoted to developer instructions.
        prefix = [{"role": "user", "content": self.summary}] if self.summary else []
        return prefix + [dict(message) for message in self.messages]
