"""Tool abstractions for Class 5."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


JSONSchema = dict[str, Any]


@dataclass(frozen=True)
class Tool:
    """A Python function plus model-facing metadata."""

    name: str
    description: str
    parameters: JSONSchema
    function: Callable[..., object]

    def run(self, **arguments: object) -> object:
        """Execute the underlying Python function."""

        return self.function(**arguments)

    def to_openai_tool(self) -> dict[str, object]:
        """Convert this tool into the Responses API tool format."""

        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ToolRegistry:
    """Name-based registry for local tools."""

    def __init__(self, tools: list[Tool] | None = None):
        """Create a registry from optional tools."""

        self._tools: dict[str, Tool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        """Register one tool by name."""

        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """Return a registered tool by name."""

        try:
            return self._tools[name]
        except KeyError as exc:
            raise ValueError(f"Unknown tool: {name}") from exc

    def run(self, name: str, **arguments: object) -> object:
        """Run a registered tool."""

        return self.get(name).run(**arguments)

    def openai_tools(self) -> list[dict[str, object]]:
        """Return all tools in OpenAI Responses API format."""

        return [tool.to_openai_tool() for tool in self._tools.values()]

    def names(self) -> list[str]:
        """Return registered tool names."""

        return sorted(self._tools)

