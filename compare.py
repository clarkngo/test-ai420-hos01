"""Run every task in tasks.json through each approach and print a comparison.

    python compare.py                 # baseline vs. react
    python compare.py --with-plan     # also run plan-and-execute
    python compare.py --only rainier-fuji --verbose

Correctness is judged by you, not by this script: compare each answer with
the "expected" line printed under it.
"""

import argparse
import json
import time
from pathlib import Path

from research import baseline

try:
    from research import react_loop
except ImportError:
    raise SystemExit("research/react_loop.py doesn't exist yet. Build it in Stage 1 of the guide, then rerun.")

parser = argparse.ArgumentParser()
parser.add_argument("--with-plan", action="store_true", help="include plan-and-execute")
parser.add_argument("--only", help="run a single task id")
parser.add_argument("--verbose", action="store_true", help="print every tool call")
parser.add_argument("--pause", type=float, default=2.0, help="seconds between tasks (free-tier rate limits)")
args = parser.parse_args()

approaches = {"baseline": baseline.run, "react": lambda q: react_loop.run(q, verbose=args.verbose)}
if args.with_plan:
    from research import plan_execute
    approaches["plan"] = lambda q: plan_execute.run(q, verbose=args.verbose)

tasks = json.loads(Path(__file__).with_name("tasks.json").read_text())
if args.only:
    tasks = [t for t in tasks if t["id"] == args.only]

rows = []
for task in tasks:
    print(f"\n=== {task['id']}: {task['question']}")
    print(f"    expected: {task['expected']}")
    for name, fn in approaches.items():
        r = fn(task["question"])
        print(f"--- {name}: {r['steps']} steps, {r['tool_calls']} tool calls, {r['tokens']} tokens, {r['seconds']}s")
        print("   ", (r["answer"] or "").strip().replace("\n", " ")[:400])
        rows.append((task["id"], name, r["steps"], r["tool_calls"], r["tokens"], r["seconds"]))
        time.sleep(args.pause)

print("\n| task | approach | steps | tool calls | tokens | seconds |\n|---|---|---|---|---|---|")
for row in rows:
    print("| " + " | ".join(str(c) for c in row) + " |")
