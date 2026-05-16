"""A small hand-written ReAct-style agent harness."""

import json
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from src.config import Settings, get_settings
from src.harness.step import AgentStep, StepKind
from src.harness.trace import TraceRecorder
from src.tools import DEFAULT_TOOLS, ToolRegistry


HARNESS_INSTRUCTIONS = """You are a tool-using assistant.
Use tools when they can answer more accurately than memory.
When tool results are available, produce a concise final answer."""


@dataclass(frozen=True)
class AgentResult:
    """Final answer and execution trace."""

    answer: str
    trace: list[dict[str, object]]


class AgentHarness:
    """Minimal agent loop with tool execution and trace recording."""

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        settings: Settings | None = None,
    ):
        """Create an agent harness."""

        self.registry = registry or ToolRegistry(DEFAULT_TOOLS)
        self.settings = settings or get_settings()

    def run(self, user_request: str, *, max_steps: int = 4) -> AgentResult:
        """Run the agent until final answer or max_steps."""

        if self.settings.provider.lower() != "openai":
            return self._run_mock(user_request)
        return self._run_openai(user_request, max_steps=max_steps)

    def _run_mock(self, user_request: str) -> AgentResult:
        """Run a deterministic offline path for tests."""

        recorder = TraceRecorder()
        recorder.add(AgentStep(StepKind.MODEL, "Mock model selected search_notes."))
        result = self.registry.run("search_notes", query=user_request)
        recorder.add(
            AgentStep(
                StepKind.TOOL,
                "Ran search_notes.",
                {"tool": "search_notes", "result": result},
            )
        )
        answer = f"Mock final answer from tool result: {result}"
        recorder.add(AgentStep(StepKind.FINAL, answer))
        return AgentResult(answer=answer, trace=recorder.to_dicts())

    def _run_openai(self, user_request: str, *, max_steps: int) -> AgentResult:
        """Run a Responses API function-calling loop."""

        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

        client = OpenAI(api_key=self.settings.openai_api_key)
        recorder = TraceRecorder()
        conversation: list[dict[str, Any] | Any] = [{"role": "user", "content": user_request}]

        for _ in range(max_steps):
            response = client.responses.create(
                model=self.settings.model,
                input=conversation,
                instructions=HARNESS_INSTRUCTIONS,
                tools=self.registry.openai_tools(),
                temperature=0.2,
                max_output_tokens=300,
            )
            recorder.add(AgentStep(StepKind.MODEL, response.output_text, {"response_id": response.id}))
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                recorder.add(AgentStep(StepKind.FINAL, response.output_text))
                return AgentResult(answer=response.output_text, trace=recorder.to_dicts())

            conversation.extend(response.output)
            for call in calls:
                arguments = json.loads(call.arguments)
                result = self.registry.run(call.name, **arguments)
                recorder.add(
                    AgentStep(
                        StepKind.TOOL,
                        f"Ran {call.name}.",
                        {"tool": call.name, "arguments": arguments, "result": result},
                    )
                )
                conversation.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": json.dumps(result, ensure_ascii=False),
                    }
                )

        answer = "Stopped because the agent reached max_steps."
        recorder.add(AgentStep(StepKind.ERROR, answer, {"max_steps": max_steps}))
        return AgentResult(answer=answer, trace=recorder.to_dicts())

