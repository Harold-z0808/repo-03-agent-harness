"""Sketch of the same task with the OpenAI Agents SDK.

This file is intentionally dependency-light. Install the Agents SDK separately
before turning this sketch into executable code.
"""


AGENTS_SDK_SKETCH = """
from agents import Agent, Runner, function_tool

@function_tool
def search_notes(query: str) -> str:
    return "Search result..."

agent = Agent(
    name="Class Notes Agent",
    instructions="Use tools to answer from class notes.",
    tools=[search_notes],
)

result = Runner.run_sync(agent, "What is working memory?")
print(result.final_output)
"""

