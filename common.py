"""Shared setup: loads .env and names the model, so it lives in one place.

The agents, baseline.py and compare.py all import MODEL from here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

MODEL = "gemini-3.8-flash"


def require_key() -> None:
    """Stop with a clear message if the Gemini key isn't in .env yet."""
    key = os.getenv("GOOGLE_API_KEY", "")
    if not key or key.startswith("paste-"):
        raise SystemExit("GOOGLE_API_KEY is not set. Copy .env.example to .env and paste your key.")
