"""Tools the research agent can use to perceive the outside world.

All three are free and need no API key: two read Wikipedia's public API,
one is a local calculator. Each returns a plain dict so the result can be
sent straight back to the model as a function response.
"""

import ast
import operator

import httpx

# Wikipedia asks API clients to identify themselves.
HEADERS = {"User-Agent": "AI420-course-agent/1.0 (https://github.com/clarkngo/stc-transformation; educational use)"}
TIMEOUT = 15


def wiki_search(query: str) -> dict:
    """Search Wikipedia and return the titles of the top matching articles.

    Use this first when you don't know the exact article title. Follow up
    with wiki_summary on the most relevant title to read the facts.

    Args:
        query: What to search for, e.g. "Space Needle" or "Mount Rainier elevation".
    """
    try:
        r = httpx.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": query,
                    "format": "json", "srlimit": 3},
            headers=HEADERS, timeout=TIMEOUT,
        )
        r.raise_for_status()
        hits = r.json()["query"]["search"]
        return {"status": "ok", "titles": [h["title"] for h in hits]}
    except Exception as e:  # return errors to the model instead of crashing the loop
        return {"status": "error", "error": str(e)}


def wiki_summary(title: str) -> dict:
    """Read the introduction section of one Wikipedia article.

    Args:
        title: The exact article title, as returned by wiki_search.
    """
    try:
        r = httpx.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "prop": "extracts", "exintro": 1, "explaintext": 1,
                    "redirects": 1, "titles": title, "format": "json", "formatversion": 2},
            headers=HEADERS, timeout=TIMEOUT,
        )
        r.raise_for_status()
        page = r.json()["query"]["pages"][0]
        if page.get("missing"):
            return {"status": "error", "error": f"No article titled '{title}'. Try wiki_search first."}
        return {"status": "ok", "title": page["title"], "summary": page.get("extract", "")}
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


def calculator(expression: str) -> dict:
    """Evaluate an arithmetic expression exactly. Use this for any math instead of guessing.

    Args:
        expression: Arithmetic only, e.g. "2007 - 1962" or "4392 / 3776".
    """
    try:
        return {"status": "ok", "result": _eval(ast.parse(expression, mode="eval").body)}
    except Exception as e:
        return {"status": "error", "error": f"Could not evaluate '{expression}': {e}"}


TOOLS = [wiki_search, wiki_summary, calculator]
TOOLS_BY_NAME = {f.__name__: f for f in TOOLS}
