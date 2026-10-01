"""Standard LLM inference: one request, one response, no tools, no loop.

This is the "before" picture. The model has to answer from memory alone,
so multi-step questions come back guessed, stale, or with arithmetic done
in its head.
"""

import sys
import time

from .common import MODEL, count_tokens, get_client


def run(question: str) -> dict:
    client = get_client()
    start = time.perf_counter()
    response = client.models.generate_content(model=MODEL, contents=question)
    return {
        "answer": response.text,
        "steps": 1,
        "tool_calls": 0,
        "tokens": count_tokens(response),
        "seconds": round(time.perf_counter() - start, 2),
        "log": [],
    }


if __name__ == "__main__":
    print(run(" ".join(sys.argv[1:]) or "When was the Space Needle built?")["answer"])
