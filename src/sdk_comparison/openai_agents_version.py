"""Optional standalone reference. The runnable Jupyter example is in Notebook 05.

openai-agents is installed by the normal project setup. Runner.run_sync is for
plain scripts; use await Runner.run(...) inside Jupyter.
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

