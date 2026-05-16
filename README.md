# repo-03-agent-harness

Week 3 lesson repo for agent loops, harnesses, state, and memory. Class 5 focuses on building a small ReAct-style agent loop from scratch. Class 6 focuses on state and memory, including working memory, history truncation, summary memory, persistent memory, and comparisons with SDK-managed sessions.

## Structure

```text
repo-03-agent-harness/
  src/
    config.py
    llm_client.py
    tools/
      base.py
      examples.py
    harness/
      loop.py
      step.py
      trace.py
    state/
      working_memory.py
      history.py
      memory_store.py
    sdk_comparison/
      openai_agents_version.py
    bonus_langgraph/
      langgraph_version.py
  notebooks/
    05_agent_loop_from_scratch.ipynb
    06_state_and_memory.ipynb
  tests/
  assignments/
    week-3-agent-harness.md
```

## Setup

```bash
uv sync --extra dev
cp .env.example .env
```

For class demos:

```bash
OPENAI_API_KEY=...
LLM_MODEL=gpt-5.4-mini
```

Never commit `.env`.

## Check Environment

```bash
uv run python check_env.py
```

## Run Tests

```bash
uv run --extra dev pytest
```

## Notebooks

Register the repo `.venv` as a Jupyter kernel:

```bash
uv run --extra dev python -m ipykernel install --user \
  --name repo-03-agent-harness \
  --display-name "Python (.venv: repo-03-agent-harness)"
```

Start Jupyter:

```bash
uv run --extra dev jupyter notebook
```

Then open:

```text
notebooks/05_agent_loop_from_scratch.ipynb
notebooks/06_state_and_memory.ipynb
```

## Notes for Students

- Class 5 teaches the ownership boundary in an agent loop: model chooses, program executes, trace records.
- Class 6 teaches why state is not one thing. Working memory, conversation history, summary memory, and persistent memory solve different problems.
- Tests should not call paid APIs. Use the mock provider and local tools.

