"""Independent provider abstraction for normal text generation."""

from typing import Protocol

from openai import OpenAI

from src.config import Settings, get_settings


Message = dict[str, str]


class ChatProvider(Protocol):
    """Common interface for chat providers."""

    def chat(self, messages: list[Message]) -> str:
        """Return one assistant message for a message list."""


class MockProvider:
    """Deterministic provider for tests and offline demos."""

    def chat(self, messages: list[Message]) -> str:
        """Return a predictable response from the latest user message."""

        last_user_message = next(
            (message["content"] for message in reversed(messages) if message["role"] == "user"),
            "",
        )
        return f"Mock response: {last_user_message}"


class OpenAIProvider:
    """OpenAI Responses API provider."""

    def __init__(self, settings: Settings):
        """Create an OpenAI provider from settings."""

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.model

    def chat(self, messages: list[Message]) -> str:
        """Send messages to the OpenAI Responses API and return output text."""

        response = self._client.responses.create(
            model=self._model,
            input=messages,
        )
        return response.output_text


def build_provider(settings: Settings | None = None) -> ChatProvider:
    """Create a chat provider from settings."""

    active_settings = settings or get_settings()
    provider = active_settings.provider.lower()
    if provider == "mock":
        return MockProvider()
    if provider == "openai":
        return OpenAIProvider(active_settings)
    raise ValueError(f"Unsupported LLM_PROVIDER: {active_settings.provider}")


def chat(messages: list[Message], provider: ChatProvider | None = None) -> str:
    """Convenience wrapper around the active provider."""

    active_provider = provider or build_provider()
    return active_provider.chat(messages)

