# Week 3 Assignment: Agent Harness, State, and Memory

## Goal

Build a small agent harness from scratch, then extend it with state and memory.

## Learning Objectives

By the end of this assignment, you should be able to:

- Explain the core ReAct loop.
- Represent an agent step.
- Record traces for debugging.
- Execute local tools from model-selected function calls.
- Separate working memory, conversation history, and persistent memory.
- Add truncation or summary memory when context grows.
- Compare a handwritten harness with an SDK-managed agent/session.

## Required Tasks

### 1. Extend the Agent Harness

Modify `src/harness/loop.py` or add a new harness variant that:

- records model/tool/final steps
- executes at least two tools
- stops safely after a maximum number of steps
- returns a final answer and trace

### 2. Add a Tool

Add one local tool under `src/tools/` and register it.

Examples:

- file lookup
- structured note search
- task checklist manager
- simple planner

### 3. Add State

Use or extend:

- `WorkingMemory`
- `ConversationHistory`
- `MemoryStore`

Show how state changes across at least two turns.

### 4. Add Tests

Automated tests should not call paid APIs.

Cover:

- tool registry behavior
- harness mock path
- trace recording
- working memory
- history truncation
- persistent memory store

## Stretch Goals

- Turn the OpenAI Agents SDK sketch into runnable code.
- Turn the LangGraph sketch into runnable code.
- Add a trace viewer or trace export.
- Add memory deletion and privacy controls.

