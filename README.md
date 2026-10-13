# repo-03-agent-harness

Week 3 of the AI Agent bootcamp: build a bounded tool loop, then add state and useful memory across conversations.

## Lessons and checkpoints

| Lesson | Core experiments | Completion checkpoint |
| --- | --- | --- |
| 05 Agent Loop / Harness | One tool round in five stages; inspect the reusable loop; two dependent tools; limits/errors; SDK comparison | Read exercise data, calculate 59, return an answer; distinguish success from stopped/failed runs |
| 06 State and Memory | Working notes; bounded history; SQLiteSession; selective writes; durable facts; retrieval; conflicts; new-session recall; privacy guard | Reload Go preference from disk and use it in a new session; block synthetic sensitive input before Runner |

LangGraph is an optional final comparison. It is not required to complete the core memory lesson.

## Setup

Python 3.11+ is declared; this revision was verified with Python 3.12. Use the committed `uv.lock` for classroom reproducibility.

```bash
uv sync --locked --extra dev
cp .env.example .env
```

Copy the environment template only on first setup. Keep your existing `.env` when updating the course. Set a real `OPENAI_API_KEY` and optionally `LLM_MODEL` (default `gpt-5.4-mini`). Never commit credentials.

```bash
uv run python check_env.py
uv run --extra dev python -m ipykernel install --user \
  --name repo-03-agent-harness \
  --display-name "Python (.venv: repo-03-agent-harness)"
uv run --extra dev jupyter notebook
```

Open the notebooks in order and select this repo's kernel. The setup cells print `sys.executable`, package versions, root directory, and whether a key is present. They never print the key.

**Restart Kernel & Run All** is the reference run order. For the staged Class 5 experiment, repeat from “Task and Initial State”; executing only the tool-output cell twice appends duplicate observations.

The notebooks make real API calls. `LLM_PROVIDER=mock` applies to source demos and tests, not to the notebooks' SDK/API calls. Their scripted failure labs run locally without paid calls. API availability, model access, and network access are required for the live sections.

SDK tracing may export prompts, model outputs, and tool data. Use synthetic examples only. To disable trace export, set `OPENAI_AGENTS_DISABLE_TRACING=1` before launching the kernel. The local trace and RunResult inspection remain available; dashboard visibility must be checked separately in your OpenAI project.

## Structure and assignment mapping

```text
src/
  config.py, llm_client.py     settings and plain-text provider abstraction
  harness/
    loop.py                   repeated model requests, termination, error observations
    step.py, trace.py          observable events and JSONL trace export
  tools/
    base.py, examples.py      typed argument validation and local example tools
  state/
    working_memory.py         task-local visible notes
    history.py                bounded, lossy conversation excerpts
    fact_store.py             source validation, versioning, atomic JSON save/load
    privacy.py                shared pre-ingestion guard
    memory_store.py           simpler append-only JSONL example
  sdk_comparison/             optional standalone SDK reference
  bonus_langgraph/            optional graph reference sketch
notebooks/
  05_agent_loop_from_scratch.ipynb
  06_state_and_memory.ipynb
assignments/week-3-agent-harness.md
tests/
```

The notebooks import the same tested implementation that students extend for homework. Class 5 displays the reusable loop source; Class 6 displays the write-policy source. Read the linked modules for the supporting implementation.

## Runtime boundaries

- `max_steps` counts model requests, including the final-answer request. Two dependent tool rounds normally need three requests. A stopped run returns `status=max_steps`, not a successful answer.
- Tool exceptions become structured observations. Incomplete or empty model output is not treated as success. Automated tests inject a fake client into the same loop.
- History's character budget covers stored content, not API framing, tool schemas, or exact tokens. Its “summary” field is a bounded excerpt, not an LLM-generated semantic summary. Compaction can lose facts.
- The fact store atomically replaces a JSON file and reloads versions. It supports one process; it does not coordinate concurrent writers. Confidence thresholds are policy choices, not proof that a fact is true.
- The privacy regex is a classroom detector, not a comprehensive PII/compliance system. The lesson proves that a blocked sample never reaches Runner or persistence.
- The arithmetic tool accepts a restricted syntax; it is not a resource-limited sandbox.

## Local artifacts and tests

Class 6 creates a fresh `.notebook_artifacts/lesson06-.../` directory per setup run. It contains the Session SQLite database and fact JSON file. Existing classroom artifacts remain on disk for inspection; use synthetic data and remove the directory when no longer needed. These files are ignored by Git.

```bash
uv run --extra dev pytest
```

Tests do not use paid APIs. They cover repeated tool rounds, recovery, termination, history budgets, provenance, reload/version history, duplicate writes, user isolation, and guard behavior.

Read [the Week 3 assignment](assignments/week-3-agent-harness.md).

## Suggested classroom pacing

- Class 5: 15 minutes on the staged round, 20 on the reusable loop and local failure lab, 15 on SDK/trace comparison, then questions and the assignment bridge.
- Class 6: 10 minutes on working state/history, 10 on Session storage, 20 on extraction/save/reload/conflicts, 10 on memory-assisted recall and guard checks. Use the LangGraph bonus only if time remains.

Each important experiment has an expected result and an assertion. A failed assertion is a debugging checkpoint; inspect the trace/source mapping instead of silently replacing model output with a canned answer.
