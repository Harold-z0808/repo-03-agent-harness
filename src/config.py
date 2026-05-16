"""Runtime settings loaded from .env."""

from functools import lru_cache
from os import getenv

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime settings for the agent harness repo."""

    provider: str = Field(default="mock")
    model: str = Field(default="gpt-5.4-mini")
    openai_api_key: str | None = Field(default=None)


@lru_cache
def get_settings() -> Settings:
    """Load .env once and return typed settings."""

    load_dotenv()
    if getenv("OPENAI_BASE_URL") == "":
        import os

        os.environ.pop("OPENAI_BASE_URL", None)

    return Settings(
        provider=getenv("LLM_PROVIDER", "mock"),
        model=getenv("LLM_MODEL", "gpt-5.4-mini"),
        openai_api_key=getenv("OPENAI_API_KEY"),
    )

