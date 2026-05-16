"""Example local tools for Class 5 and Class 6."""

from datetime import UTC, datetime

from src.tools.base import Tool


NOTES = [
    {
        "title": "Agent Loop",
        "body": "A ReAct loop alternates between model reasoning, tool actions, observations, and final answers.",
    },
    {
        "title": "State",
        "body": "Agent state includes current task, intermediate steps, working memory, and conversation history.",
    },
    {
        "title": "Memory",
        "body": "Memory can be short-term working notes, summarized history, or persistent cross-session records.",
    },
]


def search_notes(query: str, max_results: int = 3) -> list[dict[str, str]]:
    """Search a small local note collection."""

    terms = set(query.lower().split())
    scored = []
    for note in NOTES:
        title = note["title"].lower()
        haystack = f"{note['title']} {note['body']}".lower()
        score = sum(3 for term in terms if term in title)
        score += sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, note))
    return [note for _, note in sorted(scored, key=lambda item: item[0], reverse=True)[:max_results]]


def calculate(expression: str) -> dict[str, object]:
    """Evaluate a tiny arithmetic expression safely for demos."""

    allowed = set("0123456789+-*/(). ")
    if not expression or any(char not in allowed for char in expression):
        raise ValueError("Only simple arithmetic expressions are allowed")
    return {"expression": expression, "result": eval(expression, {"__builtins__": {}}, {})}


def get_current_utc_time() -> dict[str, str]:
    """Return the current UTC time."""

    return {"utc_time": datetime.now(UTC).isoformat(timespec="seconds")}


DEFAULT_TOOLS = [
    Tool(
        name="search_notes",
        description="Search local class notes about agent loops, state, and memory.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
                "max_results": {"type": "integer", "description": "Maximum number of results."},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        function=search_notes,
    ),
    Tool(
        name="calculate",
        description="Evaluate a simple arithmetic expression.",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Arithmetic expression."},
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        function=calculate,
    ),
    Tool(
        name="get_current_utc_time",
        description="Get the current UTC time.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        function=get_current_utc_time,
    ),
]
