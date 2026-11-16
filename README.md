# AI 420 · HOS 1 — Agent Anatomy

Starter repo for Hands-On Session 1 of AI 420 (Agentic AI). The full instructions are in the
HOS 1 guide on the course site (Module 1); this README only covers setup. Everything a coding
agent needs for this HOS is in this repo and in the prompts the guide gives you, so it has no
reason to open a web page.

## What's here

| Path | What it is |
|---|---|
| `research_agent/tools.py` | Three working tools: `search_wikipedia`, `wikipedia_intro`, `calculate` (free, no key) |
| `research_agent/agent.py` | **Empty except for a TODO.** You build `root_agent` here in Create, Part B |
| `baseline.py` | One model call, no tools — the "before" picture |
| `tasks.json` | Five multi-step questions with expected answers |
| `compare.py` | Runs every question through the baseline and your agent, then prints a summary table. Don't change it |
| `plan_execute/agent.py` | **TODO.** The plan-and-execute agent you write by hand in Understand & Refine |
| `common.py` | Loads `.env` and sets `MODEL = "gemini-3.8-flash"` |
| `tests/` | Offline tests for the tools (`pytest`) |
| `NOTES.md` | Your written work, one heading per CEAU stage |
| `screenshots/` | Your screenshots |

## Setup

You need a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

**On your own computer (recommended — open the folder in Antigravity):**

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then paste your key into .env
pytest                           # the tool tests should pass before you write any agent
```

**In GitHub Codespaces (fallback):** open the repo in a Codespace. The dev container installs
everything and creates `.env`; paste your key into it.

## Running things

All commands run from this top folder.

```bash
python baseline.py "How many years before the first iPhone was the Space Needle completed?"
adk web                          # Codespaces: adk web --allow_origins "*"; then pick research_agent
python compare.py --verbose
python compare.py --max-llm-calls 2
python compare.py --with-plan
```

There is one `.env`, in this top folder. `adk web` finds it by looking upward from the agent's folder,
and the scripts load it through `common.py`. Never commit it — `.gitignore` already excludes it.

`adk web` lists the agent folders here. Picking one whose `agent.py` doesn't define `root_agent` yet gives an error.
