"""Standard LLM inference: one request, one response, no tools, no loop.

This is the "before" picture. The model answers from memory alone, so
multi-step questions come back guessed, stale, or with the arithmetic done
in its head.

    python baseline.py "How many years before the first iPhone was the Space Needle completed?"
"""

import sys
import time

from google import genai

from common import MODEL, require_key


def run(question: str) -> dict:
    """Ask the model once. Returns the answer and what it cost."""
    require_key()
    client = genai.Client()
    start = time.perf_counter()
    response = client.models.generate_content(model=MODEL, contents=question)
    usage = response.usage_metadata
    return {
        "answer": (response.text or "").strip(),
        "model_calls": 1,
        "tool_calls": 0,
        "tokens": (usage.total_token_count or 0) if usage else 0,
        "seconds": round(time.perf_counter() - start, 1),
        "stopped": None,
    }


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "When was the Space Needle completed?"
    result = run(q)
    print(result["answer"])
    print(f"\n(1 model call, {result['tokens']} tokens, {result['seconds']} s)")
