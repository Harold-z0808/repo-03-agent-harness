"""Sketch of the same agent as a LangGraph state graph.

This file is intentionally dependency-light. LangGraph is installed with the dev extra; supply the missing node functions before
turning this sketch into executable code.
"""


LANGGRAPH_SKETCH = """
from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: list
    tool_trace: list

graph = StateGraph(AgentState)
graph.add_node("model", call_model)
graph.add_node("tools", run_tools)
graph.add_conditional_edges("model", should_continue, {"tools": "tools", "end": END})
graph.add_edge("tools", "model")
app = graph.compile()
"""

