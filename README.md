# AI 420 — HOS 1: Anatomy of an Agent

Guide: https://clarkngo.github.io/stc-transformation/courses/ai-420-guides/hos-01-agent-anatomy.html

**Already working**
- `research/tools.py`: three tools (Wikipedia search, Wikipedia intro, calculator). Free, no key.
- `research/baseline.py`: one plain LLM call, no tools. The "before" picture.
- `tasks.json` + `compare.py`: five multi-step questions, run through each approach side by side.
- `adk_research_agent/`: the same agent in Google ADK. Run `adk web` here and pick it.

**You build**
- Stage 1: `research/react_loop.py`, an agent loop by hand (the guide gives the prompt).
- Stage 4: `research/plan_execute.py`, by hand.

```bash
cp .env.example .env        # paste your GOOGLE_API_KEY
python -m research.baseline "How many years before the first iPhone was the Space Needle completed?"
python compare.py --verbose # after Stage 1
```
