"""Shared setup: API client, model name, and token accounting."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

SYSTEM = (
    "You are a careful research assistant. Answer using facts you look up, not memory. "
    "Use wiki_search to find article titles, wiki_summary to read them, and calculator "
    "for every piece of arithmetic. When you have enough information, reply with a short "
    "final answer and the key facts it relies on."
)


def get_client() -> genai.Client:
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit("GOOGLE_API_KEY is not set. Copy .env.example to .env and paste your key.")
    return genai.Client()


def count_tokens(response) -> int:
    """Total tokens (input + output) reported for one model call."""
    usage = getattr(response, "usage_metadata", None)
    return (usage.total_token_count or 0) if usage else 0
