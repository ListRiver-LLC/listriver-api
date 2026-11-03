import asyncio
import json

import pytest

from listriver import OutOfRecords, Page
import listriver_mcp.server as srv


class FakeClient:
    def __init__(self):
        self.calls = []

    def states(self):
        self.calls.append(("states", {}))
        return [{"code": "FL", "name": "Florida", "recent": 10, "year": 100, "all": 1000}]

    def count(self, **f):
        self.calls.append(("count", f))
        return {"total": 7, "states": [{"code": "FL", "count": 7}], "approximate": True}

    def page(self, limit, cursor=None, **f):
        self.calls.append(("page", dict(f, limit=limit, cursor=cursor)))
        return Page(rows=[{"businessName": "A LLC"}], cursor="FL.5", resume="FL.5", monthly_remaining=499, credits_remaining=0)


@pytest.fixture
def fake(monkeypatch):
    c = FakeClient()
    monkeypatch.setattr(srv, "_client", c)
    return c


def call(name, args):
    result = asyncio.run(srv.server.call_tool(name, args))
    text = result.content[0].text
    return json.loads(text)


def test_tools_are_listed_and_read_only():
    tools = {t.name: t for t in asyncio.run(srv.server.list_tools())}
    assert set(tools) == {"list_states", "count_businesses", "search_businesses"}
    assert all(t.annotations.read_only_hint for t in tools.values())
    assert "USES THE USER'S RECORDS" in tools["search_businesses"].description


def test_count_passes_filters(fake):
    out = call("count_businesses", {"states": "FL", "city": "MIAMI", "has_phone": True, "formed_within": 3})
    assert out["ok"] and out["total"] == 7
    name, f = fake.calls[0]
    assert name == "count" and f["states"] == "FL" and f["city"] == "MIAMI" and f["has_phone"] is True and f["formed_within"] == 3


def test_any_formation_date_uses_preset_all(fake):
    call("count_businesses", {"states": "FL", "formed_within": 0})
    assert fake.calls[0][1]["preset"] == "all" and fake.calls[0][1]["formed_within"] is None


def test_search_caps_the_limit_and_returns_cursor(fake):
    out = call("search_businesses", {"states": "FL", "limit": 5000, "cursor": "FL.1"})
    assert out["count"] == 1 and out["cursor"] == "FL.5" and out["more"] is True and out["records_left_this_period"] == 499
    assert fake.calls[0][1]["limit"] == 100 and fake.calls[0][1]["cursor"] == "FL.1"


def test_out_of_records_gives_a_hint(monkeypatch):
    class Broke(FakeClient):
        def page(self, limit, cursor=None, **f):
            raise OutOfRecords(429, "Your free 500 records for this month are used up.")
    monkeypatch.setattr(srv, "_client", Broke())
    out = call("search_businesses", {"states": "FL"})
    assert out["ok"] is False and out["status"] == 429 and "Account/Api.aspx" in out["hint"]


def test_missing_key_explains_how_to_get_one(monkeypatch):
    monkeypatch.setattr(srv, "_client", None)
    monkeypatch.delenv("LISTRIVER_API_KEY", raising=False)
    out = call("list_states", {})
    assert out["ok"] is False and "ApiSignUp.aspx" in out["error"]
