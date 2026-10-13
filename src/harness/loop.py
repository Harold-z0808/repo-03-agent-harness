"""A bounded tool loop with injectable responses for deterministic experiments."""

import json
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from openai import OpenAI
from src.config import Settings, get_settings
from src.harness.step import AgentStep, StepKind
from src.harness.trace import TraceRecorder
from src.tools import DEFAULT_TOOLS, ToolRegistry

HARNESS_INSTRUCTIONS = """Use tools to answer from evidence. Never invent a tool result.
For dependent tasks, read the data first, then use the appropriate tool.
When a tool returns an error, correct the request or explain the limitation.
Answer concisely after receiving enough evidence."""


@dataclass(frozen=True)
class AgentResult:
    answer: str
    trace: list[dict[str, object]]
    status: str = "completed"


class AgentHarness:
    def __init__(self, registry: ToolRegistry | None = None,
                 settings: Settings | None = None, client: Any = None):
        self.registry = registry if registry is not None else ToolRegistry(DEFAULT_TOOLS)
        self.settings = settings or get_settings()
        self.client = client

    def run(self, user_request: str, *, max_steps: int = 4) -> AgentResult:
        """max_steps bounds MODEL requests; reaching the limit is not success."""
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        provider = self.settings.provider.lower()
        if provider not in {"mock", "openai"}:
            raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
        if self.client is not None:
            active_client = self.client
        elif provider == "mock":
            active_client = self._mock_client()
        else:
            if not self.settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
            active_client = OpenAI(api_key=self.settings.openai_api_key, timeout=30, max_retries=1)
        return self._run_loop(user_request, active_client, max_steps)

    def _mock_client(self) -> Any:
        """One scripted search, then final; other registries receive a plain reply."""
        def create(**kwargs):
            has_observation = any(isinstance(x, dict) and x.get("type") == "function_call_output"
                                  for x in kwargs["input"])
            if "search_notes" in self.registry.names() and not has_observation:
                output = [SimpleNamespace(type="function_call", name="search_notes",
                    call_id="mock-call", arguments=json.dumps({"query": kwargs["input"][0]["content"]}))]
                text = ""
            else:
                output, text = [], "Mock final answer: inspect the recorded tool evidence."
            return SimpleNamespace(id="mock-response", status="completed", output=output, output_text=text)
        return SimpleNamespace(responses=SimpleNamespace(create=create))

    def _run_loop(self, request: str, client: Any, max_steps: int) -> AgentResult:
        recorder = TraceRecorder()
        conversation: list[Any] = [{"role": "user", "content": request}]

        def stop(message: str, status: str) -> AgentResult:
            recorder.add(AgentStep(StepKind.ERROR, message, {"status": status}))
            return AgentResult(message, recorder.to_dicts(), status)

        for turn in range(1, max_steps + 1):
            try:
                response = client.responses.create(
                    model=self.settings.model, input=conversation,
                    instructions=HARNESS_INSTRUCTIONS, tools=self.registry.openai_tools(),
                    parallel_tool_calls=False, max_output_tokens=600,
                )
            except Exception as exc:
                return stop(f"Model request failed: {type(exc).__name__}", "model_error")
            recorder.add(AgentStep(StepKind.MODEL, response.output_text,
                                  {"response_id": response.id, "turn": turn}))
            if response.status != "completed":
                return stop(f"Model response status: {response.status}", "incomplete")
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                if not response.output_text.strip():
                    return stop("Model returned no final text.", "empty_output")
                recorder.add(AgentStep(StepKind.FINAL, response.output_text))
                return AgentResult(response.output_text, recorder.to_dicts())
            conversation.extend(response.output)
            for call in calls:
                try:
                    arguments = json.loads(call.arguments)
                    if not isinstance(arguments, dict):
                        raise ValueError("Tool arguments must be an object")
                    recorder.add(AgentStep(StepKind.TOOL, f"Requested {call.name}",
                        {"tool": call.name, "arguments": arguments, "call_id": call.call_id}))
                    result = self.registry.run(call.name, **arguments)
                    serialized = json.dumps(result, ensure_ascii=False)
                except Exception as exc:
                    result = {"error": type(exc).__name__,
                              "message": "Tool request failed; check its name, arguments, and allowed inputs."}
                    serialized = json.dumps(result)
                    recorder.add(AgentStep(StepKind.ERROR, "Tool request failed", result))
                recorder.add(AgentStep(StepKind.OBSERVATION, serialized,
                                      {"tool": call.name, "call_id": call.call_id}))
                conversation.append({"type": "function_call_output", "call_id": call.call_id,
                                     "output": serialized})
        return stop("Stopped because the agent reached max_steps.", "max_steps")
