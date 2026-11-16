"""Run every question in tasks.json through the baseline and your agent(s).

    python compare.py                    # baseline vs research_agent
    python compare.py --verbose          # also show each tool call and result
    python compare.py --with-plan        # add plan_execute as a third column
    python compare.py --max-llm-calls 2  # give each agent run a tiny budget
    python compare.py --only rainier-fuji,seattle-cityu
    python compare.py --pause 5          # wait 5 s between questions (429s)

Don't change this file: it's how everyone's agents are measured the same way.
"""

import argparse
import asyncio
import importlib
import json
import logging
import textwrap
import time
from pathlib import Path

from google.adk.agents.invocation_context import LlmCallsLimitExceededError
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.genai import types

import baseline
from common import require_key

ROOT = Path(__file__).resolve().parent

# ADK logs a full traceback whenever a run stops early (budget spent, API error).
# compare.py catches those and prints a one-line STOPPED reason instead.
for _name in ("google_adk.google.adk.workflow", "google_adk.google.adk.runners"):
    logging.getLogger(_name).setLevel(logging.CRITICAL)


def load_agent(package: str):
    """Return package.agent.root_agent, or None with a hint if it isn't there yet."""
    try:
        module = importlib.import_module(f"{package}.agent")
    except Exception as e:  # a syntax or import error in the student's file
        print(f"\n!! Could not import {package}/agent.py: {type(e).__name__}: {e}\n")
        return None
    agent = getattr(module, "root_agent", None)
    if agent is None:
        print(f"\n!! {package}/agent.py doesn't define root_agent yet, so it is skipped.\n")
    return agent


def _short(value, width=160) -> str:
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


async def _run_agent(agent, question: str, max_llm_calls: int, verbose: bool) -> dict:
    runner = InMemoryRunner(agent=agent, app_name="compare")
    session = await runner.session_service.create_session(app_name="compare", user_id="student")
    message = types.Content(role="user", parts=[types.Part(text=question)])
    result = {"answer": "", "author": "", "model_calls": 0, "tool_calls": 0, "tokens": 0, "stopped": None}
    start = time.perf_counter()
    try:
        async for event in runner.run_async(
            user_id="student",
            session_id=session.id,
            new_message=message,
            run_config=RunConfig(max_llm_calls=max_llm_calls),
        ):
            if event.usage_metadata and not event.partial:
                result["model_calls"] += 1
                result["tokens"] += event.usage_metadata.total_token_count or 0
            calls = event.get_function_calls()
            result["tool_calls"] += len(calls)
            if verbose:
                for call in calls:
                    print(f"      [{event.author}] → {call.name}({_short(dict(call.args or {}), 100)})")
                for resp in event.get_function_responses():
                    print(f"      [{event.author}] ← {resp.name}: {_short(resp.response)}")
            text = "".join(p.text or "" for p in (event.content.parts if event.content else []) if not p.thought)
            if verbose and text.strip() and not event.partial:
                print(f"      [{event.author}] says: {_short(text)}")
            if event.is_final_response() and text.strip():
                result["answer"], result["author"] = text.strip(), event.author
    except LlmCallsLimitExceededError as e:
        result["stopped"] = f"budget of {max_llm_calls} model calls spent ({e})"
    result["seconds"] = round(time.perf_counter() - start, 1)
    return result


def run_agent(agent, question: str, max_llm_calls: int = 20, verbose: bool = False) -> dict:
    """Run one question through an ADK agent and measure it. Importable for later HOS."""
    return asyncio.run(_run_agent(agent, question, max_llm_calls, verbose))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verbose", action="store_true", help="show each tool call and result")
    parser.add_argument("--with-plan", action="store_true", help="also run plan_execute")
    parser.add_argument("--max-llm-calls", type=int, default=20, help="model-call budget per agent run (default 20)")
    parser.add_argument("--only", help="comma-separated task ids to run")
    parser.add_argument("--pause", type=float, default=0, help="seconds to wait between questions")
    args = parser.parse_args()

    require_key()
    tasks = json.loads((ROOT / "tasks.json").read_text())
    if args.only:
        wanted = {t.strip() for t in args.only.split(",")}
        tasks = [t for t in tasks if t["id"] in wanted]
        if not tasks:
            raise SystemExit(f"No task ids match {sorted(wanted)}. Ids are in tasks.json.")

    systems = {"baseline": None}
    for name, package, wanted in [("agent", "research_agent", True), ("plan_execute", "plan_execute", args.with_plan)]:
        if wanted:
            agent = load_agent(package)
            if agent is not None:
                systems[name] = agent

    rows = []
    for i, task in enumerate(tasks):
        if i and args.pause:
            time.sleep(args.pause)
        print("=" * 78)
        print(f"{task['id']}: {task['question']}")
        print(f"  expected: {task['expected']}")
        for name, agent in systems.items():
            print(f"\n  ── {name}")
            try:
                r = baseline.run(task["question"]) if agent is None else run_agent(
                    agent, task["question"], args.max_llm_calls, args.verbose)
            except Exception as e:  # API errors: show them, keep going
                r = {"answer": "", "model_calls": 0, "tool_calls": 0, "tokens": 0, "seconds": 0,
                     "stopped": f"error: {type(e).__name__}: {_short(str(e), 200)}"}
            if r["stopped"]:
                print(f"    STOPPED — {r['stopped']}")
                if r["answer"]:
                    print(f"    last reply before the stop, from {r.get('author') or name}:")
            print(textwrap.indent(textwrap.fill(r["answer"] or "(no final answer)", 74), "    "))
            rows.append((task["id"], name, r))
        print()

    print("=" * 78)
    print("Summary (check each answer against 'expected' yourself — nothing here grades correctness)\n")
    header = f"{'task':<22}{'system':<14}{'model calls':>12}{'tool calls':>12}{'tokens':>9}{'seconds':>9}  stopped"
    print(header)
    print("-" * len(header))
    for task_id, name, r in rows:
        print(f"{task_id:<22}{name:<14}{r['model_calls']:>12}{r['tool_calls']:>12}{r['tokens']:>9}"
              f"{r['seconds']:>9}  {'yes' if r['stopped'] else ''}")
    print()
    for name in systems:
        mine = [r for _, n, r in rows if n == name]
        print(f"{name:<14} total: {sum(r['model_calls'] for r in mine)} model calls, "
              f"{sum(r['tool_calls'] for r in mine)} tool calls, {sum(r['tokens'] for r in mine)} tokens, "
              f"{round(sum(r['seconds'] for r in mine), 1)} s")


if __name__ == "__main__":
    main()
