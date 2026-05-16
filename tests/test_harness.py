from src.config import Settings
from src.harness.loop import AgentHarness
from src.harness.step import StepKind
from src.harness.trace import TraceRecorder
from src.harness.step import AgentStep


def test_agent_harness_mock_path_returns_trace():
    harness = AgentHarness(settings=Settings(provider="mock"))

    result = harness.run("What is agent state?")

    assert "Mock final answer" in result.answer
    assert result.trace[-1]["kind"] == StepKind.FINAL


def test_trace_recorder_collects_steps(tmp_path):
    recorder = TraceRecorder()
    recorder.add(AgentStep(StepKind.MODEL, "thinking"))

    path = recorder.save_jsonl(tmp_path / "trace.jsonl")

    assert path.exists()
    assert "thinking" in path.read_text()

