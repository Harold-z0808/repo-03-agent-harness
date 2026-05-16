"""Working memory for one agent run."""

from dataclasses import dataclass, field


@dataclass
class WorkingMemory:
    """Scratchpad-style notes for the current task."""

    notes: list[str] = field(default_factory=list)

    def add(self, note: str) -> None:
        """Add one working note."""

        clean_note = note.strip()
        if clean_note:
            self.notes.append(clean_note)

    def render(self) -> str:
        """Render notes as a prompt-ready scratchpad."""

        if not self.notes:
            return "No working notes yet."
        return "\n".join(f"- {note}" for note in self.notes)

    def clear(self) -> None:
        """Clear all working notes."""

        self.notes.clear()

