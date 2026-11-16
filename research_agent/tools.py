"""Tools the research agent can use to perceive the outside world.

All three are free and need no API key: two read Wikipedia's public API,
one is a local calculator. ADK turns each function into a tool the model
can call, using its name, its type hints and its docstring, so the
docstrings are written for the model. Each returns a dict, and errors come
back as data instead of crashing the run.
"""

import ast
import operator

import httpx

# Wikipedia's robot policy (https://w.wiki/4wJS) blocks requests that don't say who
# they are with a contact URL; without one you get 403 Forbidden. Keep this header.
# The URL is only sent to Wikipedia as identification; nothing here opens it.
HEADERS = {"User-Agent": "AI420-course-agent/1.0 (+https://www.cityu.edu/; educational use)"}
TIMEOUT = 15
API = "https://en.wikipedia.org/w/api.php"


def search_wikipedia(query: str) -> dict:
    """Search Wikipedia and return the titles of the top matching articles.

    Use this first when you don't know the exact article title. Then call
    wikipedia_intro on the most relevant title to read the facts.

    Args:
        query: What to search for, e.g. "Space Needle" or "Mount Rainier".
    """
    try:
        r = httpx.get(API, params={"action": "query", "list": "search", "srsearch": query,
                                   "format": "json", "srlimit": 3},
                      headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        hits = r.json()["query"]["search"]
        return {"status": "ok", "titles": [h["title"] for h in hits]}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def wikipedia_intro(title: str) -> dict:
    """Read the introduction of one Wikipedia article.

    Args:
        title: The exact article title, as returned by search_wikipedia.
    """
    try:
        r = httpx.get(API, params={"action": "query", "prop": "extracts", "exintro": 1,
                                   "explaintext": 1, "redirects": 1, "titles": title,
                                   "format": "json", "formatversion": 2},
                      headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        page = r.json()["query"]["pages"][0]
        if page.get("missing"):
            return {"status": "error", "error": f"No article titled '{title}'. Try search_wikipedia first."}
        return {"status": "ok", "title": page["title"], "intro": page.get("extract", "")}
    except Exception as e:
        return {"status": "error", "error": str(e)}


_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.Mod: operator.mod, ast.FloorDiv: operator.floordiv,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("only numbers and + - * / ** % // are allowed")


def calculate(expression: str) -> dict:
    """Evaluate an arithmetic expression exactly. Use this for every calculation instead of doing math yourself.

    Args:
        expression: Arithmetic only, e.g. "2007 - 1962" or "4392 / 3776".
    """
    try:
        return {"status": "ok", "result": _eval(ast.parse(expression, mode="eval").body)}
    except Exception as e:
        return {"status": "error", "error": f"Could not evaluate '{expression}': {e}"}
