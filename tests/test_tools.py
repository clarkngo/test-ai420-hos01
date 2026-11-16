"""Offline checks for the three tools. No API key or network needed.

    pytest
"""

import httpx
import pytest

from research_agent import tools


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


@pytest.mark.parametrize("expression, expected", [
    ("2007 - 1962", 45),
    ("4392 / 3776", 4392 / 3776),
    ("2 ** 10", 1024),
    ("-(3 + 4) * 2", -14),
    ("17 // 5", 3),
])
def test_calculate_arithmetic(expression, expected):
    assert tools.calculate(expression) == {"status": "ok", "result": expected}


@pytest.mark.parametrize("expression", ["__import__('os')", "open('x')", "2 +", "1 / 0"])
def test_calculate_returns_errors_as_data(expression):
    result = tools.calculate(expression)
    assert result["status"] == "error" and result["error"]


def test_search_wikipedia_returns_titles(monkeypatch):
    seen = {}

    def fake_get(url, params, headers, timeout):
        seen.update(params=params, headers=headers)
        return FakeResponse({"query": {"search": [{"title": "Space Needle"}, {"title": "Seattle Center"}]}})

    monkeypatch.setattr(httpx, "get", fake_get)
    assert tools.search_wikipedia("Space Needle") == {"status": "ok", "titles": ["Space Needle", "Seattle Center"]}
    assert seen["params"]["srsearch"] == "Space Needle"
    assert "User-Agent" in seen["headers"]


def test_wikipedia_intro_reads_extract(monkeypatch):
    payload = {"query": {"pages": [{"title": "Space Needle", "extract": "Completed in 1962."}]}}
    monkeypatch.setattr(httpx, "get", lambda *a, **k: FakeResponse(payload))
    assert tools.wikipedia_intro("Space Needle") == {
        "status": "ok", "title": "Space Needle", "intro": "Completed in 1962."}


def test_wikipedia_intro_missing_page(monkeypatch):
    payload = {"query": {"pages": [{"title": "Nope", "missing": True}]}}
    monkeypatch.setattr(httpx, "get", lambda *a, **k: FakeResponse(payload))
    result = tools.wikipedia_intro("Nope")
    assert result["status"] == "error" and "search_wikipedia" in result["error"]


def test_network_errors_come_back_as_data(monkeypatch):
    def boom(*a, **k):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "get", boom)
    assert tools.search_wikipedia("x")["status"] == "error"
    assert tools.wikipedia_intro("x")["status"] == "error"


def test_tools_have_docstrings_for_the_model():
    for fn in (tools.search_wikipedia, tools.wikipedia_intro, tools.calculate):
        assert fn.__doc__ and "Args:" in fn.__doc__, fn.__name__
