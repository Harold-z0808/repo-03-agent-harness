"""Single-process JSON fact store with provenance checks and version history."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class MemoryCandidate(BaseModel):
    source_id: str
    source_text: str
    decision: Literal["store", "drop"]
    category: Literal["preference", "profile", "current_project"] | None
    key: str | None
    value: str | None
    confidence: float = Field(ge=0, le=1)
    reason: str

    @model_validator(mode="after")
    def check_decision(self):
        fields = (self.category, self.key, self.value)
        if self.decision == "store" and not all(fields):
            raise ValueError("Store requires category, key, value")
        if self.decision == "drop" and any(x is not None for x in fields):
            raise ValueError("Drop must have null category, key, value")
        return self


class MemoryExtraction(BaseModel):
    candidates: list[MemoryCandidate]


ALLOWED_KEYS = {
    "preferred_programming_language": "preference",
    "response_style": "preference",
    "current_project": "current_project",
}


def canonicalize(candidate: MemoryCandidate) -> MemoryCandidate:
    if candidate.decision == "drop":
        return candidate
    if ALLOWED_KEYS.get(candidate.key) != candidate.category:
        raise ValueError("Unsupported category/key pair")
    value = candidate.value.strip()
    if not value:
        raise ValueError("Empty memory value")
    if candidate.key == "preferred_programming_language":
        languages = {x.casefold(): x for x in ["Python", "Go", "Rust", "Java", "JavaScript", "TypeScript"]}
        if value.casefold() not in languages:
            raise ValueError("Unsupported language in this classroom schema")
        value = languages[value.casefold()]
    elif candidate.key == "response_style":
        value = value.casefold()
        if value not in {"concise", "detailed"}:
            raise ValueError("Unsupported response style")
    return candidate.model_copy(update={"value": value})


def validate_extraction(extraction: MemoryExtraction, sources: dict[str, str]) -> list[MemoryCandidate]:
    """Model schema validity is separate from correspondence to input sources."""
    ids = [c.source_id for c in extraction.candidates]
    if len(ids) != len(set(ids)) or set(ids) != set(sources):
        raise ValueError("Expected exactly one candidate per source ID")
    accepted = []
    for candidate in extraction.candidates:
        if candidate.source_text != sources[candidate.source_id]:
            raise ValueError("Candidate source text does not match original input")
        accepted.append(canonicalize(candidate))
    return accepted


class MemoryFact(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    user_id: str
    category: str
    key: str
    value: str
    confidence: float = Field(ge=0, le=1)
    source_id: str
    source_text: str
    status: Literal["active", "superseded"] = "active"
    supersedes: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds"))


class FactStore:
    """Atomic file replacement for one process; not a concurrent database."""

    def __init__(self, path: str | Path, *, min_confidence: float = 0.8):
        if not 0 <= min_confidence <= 1:
            raise ValueError("min_confidence must be between 0 and 1")
        self.path = Path(path)
        self.min_confidence = min_confidence
        self.records = ([MemoryFact.model_validate(r) for r in json.loads(self.path.read_text())]
                        if self.path.exists() else [])

    def active(self, user_id: str) -> list[MemoryFact]:
        return [r for r in self.records if r.user_id == user_id and r.status == "active"]

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                    prefix=".facts-", delete=False) as file:
                temporary = Path(file.name)
                json.dump([r.model_dump() for r in self.records], file, ensure_ascii=False, indent=2)
            os.replace(temporary, self.path)
        finally:
            if temporary and temporary.exists():
                temporary.unlink()

    def apply(self, user_id: str, raw_candidate: MemoryCandidate, *, sources: dict[str, str]) -> dict:
        if sources.get(raw_candidate.source_id) != raw_candidate.source_text:
            raise ValueError("Unverified memory provenance")
        candidate = canonicalize(raw_candidate)
        if candidate.decision == "drop":
            return {"event": "dropped", "reason": candidate.reason}
        if candidate.confidence < self.min_confidence:
            return {"event": "needs_review", "reason": "Below the classroom confidence threshold"}
        current = next((r for r in self.active(user_id) if r.key == candidate.key), None)
        if current and current.value.casefold() == candidate.value.casefold():
            return {"event": "duplicate", "fact_id": current.id}
        fact = MemoryFact(user_id=user_id, category=candidate.category, key=candidate.key,
            value=candidate.value, confidence=candidate.confidence,
            source_id=candidate.source_id, source_text=candidate.source_text,
            supersedes=current.id if current else None)
        if current:
            current.status = "superseded"
        self.records.append(fact)
        self._save()
        return {"event": "superseded" if current else "inserted",
                "old_value": current.value if current else None,
                "new_value": fact.value, "key": fact.key, "fact_id": fact.id}
