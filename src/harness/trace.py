"""Trace recording for the agent harness."""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from src.harness.step import AgentStep


class TraceRecorder:
    """Collect and optionally persist agent steps."""

    def __init__(self):
        """Create an empty trace recorder."""

        self.steps: list[AgentStep] = []

    def add(self, step: AgentStep) -> None:
        """Append one step to the trace."""

        self.steps.append(step)

    def to_dicts(self) -> list[dict[str, object]]:
        """Return serializable trace dictionaries."""

        return [asdict(step) for step in self.steps]

    def save_jsonl(self, path: str | Path) -> Path:
        """Save the trace as JSON Lines."""

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as file:
            for step in self.steps:
                payload = asdict(step)
                payload["recorded_at"] = datetime.now(UTC).isoformat(timespec="seconds")
                file.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return destination

