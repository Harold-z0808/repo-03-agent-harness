from src.state.history import ConversationHistory
from src.state.memory_store import MemoryStore
from src.state.working_memory import WorkingMemory


def test_working_memory_renders_notes():
    memory = WorkingMemory()
    memory.add("Need to inspect tool result.")

    assert "- Need to inspect tool result." in memory.render()


def test_conversation_history_truncates_into_summary():
    history = ConversationHistory(max_characters=40)
    history.add("user", "a" * 50)
    history.add("assistant", "b" * 50)

    assert history.summary
    assert history.total_characters() <= history.max_characters


def test_memory_store_persists_and_searches(tmp_path):
    store = MemoryStore(tmp_path / "memory.jsonl")
    store.add("u1", "preference", "likes concise answers")

    results = store.search("u1", "concise")

    assert results[0].key == "preference"

