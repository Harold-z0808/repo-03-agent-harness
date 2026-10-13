# Week 3 Assignment: Agent Harness, State, and Memory

## Goal

Extend the same loop and memory components used in the notebooks. Use the notebooks' checkpoints as your baseline, then add one useful behavior per lesson.

## Class 5 — Extend a bounded loop

Start with `src/harness/loop.py`, `src/tools/base.py`, and the Section 1B experiment in Notebook 05.

1. Add one read-only local tool and register its typed Python function and model-facing schema.
2. Demonstrate a task with at least two dependent tool calls followed by a final answer. Do not put the answer or all hidden tool data in the user prompt.
3. Record model/tool/observation/final/error events. State whether the result completed or stopped.
4. Write a scripted-client test for your task and one failure path: invalid arguments, unknown tool, tool exception, incomplete response, or the model-request limit.

`max_steps` counts model requests, including the final-answer request. Tests must invoke the real loop with fake responses, rather than a separate fake agent implementation.

## Class 6 — Make memory survive and change behavior

Start with `src/state/working_memory.py`, `history.py`, `fact_store.py`, and `privacy.py`, plus Notebook 06.

1. Show working notes being added and cleared at a task boundary.
2. Demonstrate the configured history character budget across many turns and one oversized message. Explain what the bounded excerpt loses and how it differs from a semantic summary/token budget.
3. Validate extraction against exact source IDs/text before saving. Demonstrate a rejected candidate and an uncertain candidate routed to review.
4. Save an explicit preference, update it, reconstruct the store from disk, and confirm the old value is superseded and the new one active.
5. In a new Session, compare an answer with no saved facts against an answer with relevant active facts. The original conversation must not be available to that new Session.
6. Add one improvement: expiration, deletion, or retrieval with a small labeled query set. Include a deterministic regression test.
7. Demonstrate that a blocked synthetic sensitive input causes zero Runner calls and leaves stored facts/session items unchanged. Do not use real sensitive data.

The older `MemoryStore` JSONL example remains available for comparing append-only records with versioned facts; it is not a second required memory implementation.

## Required validation

```bash
uv sync --locked --extra dev
uv run --extra dev pytest
```

Tests must not call paid APIs. Cover your new behavior plus relevant invariants: budget, provenance, reload, latest active value, duplicate update, another user's isolation, or zero calls on blocked input.

Manually run both notebooks with **Restart Kernel & Run All** when real API access is available. Report model/package versions and distinguish local scripted experiments from real model outputs.

## Submission

Include:

- Code and offline tests.
- A short explanation of your added tool/memory capability.
- One successful trace and one controlled failure trace, using synthetic data.
- Evidence of persistence after object reconstruction and a new-session answer using the updated fact.
- Remaining limitations; do not claim production safety or comprehensive PII detection.

Do not commit `.env`, local memory/Session databases, or personal data in notebook outputs.

## Optional extensions

- Compare the same task's manual trace and SDK RunResult/dashboard trace.
- Add a semantic-summary strategy and measure retained facts and context cost against excerpts.
- Extend the LangGraph bonus with a durable checkpointer, or a Store spanning two thread IDs.
- Export a trace viewer or add per-tool duration/usage measurements.
