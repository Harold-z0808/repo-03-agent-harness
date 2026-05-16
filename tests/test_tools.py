import pytest

from src.tools import DEFAULT_TOOLS, ToolRegistry
from src.tools.examples import calculate, search_notes


def test_search_notes_finds_agent_loop_note():
    results = search_notes("agent loop")

    assert results[0]["title"] == "Agent Loop"


def test_calculate_allows_simple_arithmetic():
    assert calculate("2 + 3 * 4")["result"] == 14


def test_calculate_rejects_unsafe_expression():
    with pytest.raises(ValueError):
        calculate("__import__('os')")


def test_tool_registry_runs_default_tool():
    registry = ToolRegistry(DEFAULT_TOOLS)

    result = registry.run("search_notes", query="memory")

    assert result[0]["title"] == "Memory"

