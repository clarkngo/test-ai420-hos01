"""The same research agent, rebuilt in Google ADK.

Same model, same three tools, same instructions as research/react_loop.py,
but ADK runs the loop for you. Run it with `adk web` from the HOS folder and
open the Events tab to find the loop you wrote by hand.
Pattern follows agent-development's hos01/hos02 examples.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from research.common import SYSTEM  # noqa: E402
from research.tools import calculator, wiki_search, wiki_summary  # noqa: E402

root_agent = Agent(
    name="research_agent",
    model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    description="Answers multi-step factual questions using Wikipedia and a calculator.",
    instruction=SYSTEM,
    tools=[wiki_search, wiki_summary, calculator],
)
