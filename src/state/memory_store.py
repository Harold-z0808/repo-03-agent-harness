"""Cross-session persistent memory store."""

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class MemoryRecord:
    """One persistent memory record."""

    user_id: str
    key: str
    value: str
    created_at: str


class MemoryStore:
    """Tiny JSONL-backed persistent memory store."""

    def __init__(self, path: str | Path):
        """Create a store at a JSONL path."""

        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, user_id: str, key: str, value: str) -> MemoryRecord:
        """Persist one memory record."""

        record = MemoryRecord(
            user_id=user_id,
            key=key,
            value=value,
            created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
        return record

    def search(self, user_id: str, query: str) -> list[MemoryRecord]:
        """Search records for one user by substring match."""

        if not self.path.exists():
            return []
        query_lower = query.lower()
        matches: list[MemoryRecord] = []
        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                payload = json.loads(line)
                record = MemoryRecord(**payload)
                haystack = f"{record.key} {record.value}".lower()
                if record.user_id == user_id and query_lower in haystack:
                    matches.append(record)
        return matches

