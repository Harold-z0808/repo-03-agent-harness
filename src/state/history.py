"""Conversation history with simple truncation and summary memory."""

from dataclasses import dataclass, field

from src.llm_client import Message


@dataclass
class ConversationHistory:
    """Conversation state with approximate token-aware truncation."""

    messages: list[Message] = field(default_factory=list)
    summary: str = ""
    max_characters: int = 4000

    def add(self, role: str, content: str) -> None:
        """Append one message and trim if needed."""

        self.messages.append({"role": role, "content": content})
        self.truncate()

    def total_characters(self) -> int:
        """Return approximate context size in characters."""

        return sum(len(message["content"]) for message in self.messages) + len(self.summary)

    def truncate(self) -> None:
        """Trim oldest messages into summary when character budget is exceeded."""

        while self.total_characters() > self.max_characters and len(self.messages) > 1:
            removed = self.messages.pop(0)
            self.summary += f"\n{removed['role']}: {removed['content'][:300]}"

    def as_messages(self) -> list[Message]:
        """Return messages with summary prepended when available."""

        if not self.summary:
            return list(self.messages)
        return [{"role": "developer", "content": f"Conversation summary:{self.summary}"}] + list(
            self.messages
        )

