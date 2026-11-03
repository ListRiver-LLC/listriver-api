import json

import pytest

from listriver import AuthError, BadRequest, Client, OutOfRecords


class FakeResponse:
    def __init__(self, status, body, headers=None):
        self.status_code = status
        self._body = body
        self.text = json.dumps(body)
        self.headers = headers or {}

    def json(self):
        return self._body


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append(dict(params))
        return self.responses.pop(0)


def client(*responses):
    return Client("lr_key_test", session=FakeSession(responses))


def test_filters_are_translated():
    c = client(FakeResponse(200, {"ok": True, "total": 5, "states": [{"code": "FL", "count": 5}], "approximate": True}))
    assert c.count(states=["FL", "GA"], has_phone=True, has_email=False, formed_within=3, entity_type="LLC")["total"] == 5
    assert c.session.calls[0] == {"action": "count", "states": "FL,GA", "hasPhone": "1", "formedWithin": "3", "entityType": "LLC"}


def test_unknown_filter_is_refused():
    with pytest.raises(TypeError):
        client().count(colour="blue")


def test_records_follows_the_cursor_and_keeps_resume():
    c = client(
        FakeResponse(200, {"ok": True, "rows": [{"n": 1}, {"n": 2}], "cursor": "FL.2", "resume": "FL.2"},
                     {"X-ListRiver-Monthly-Remaining": "498"}),
        FakeResponse(200, {"ok": True, "rows": [{"n": 3}], "cursor": None, "resume": "FL.3"},
                     {"X-ListRiver-Monthly-Remaining": "497"}),
    )
    assert [r["n"] for r in c.records(states="FL")] == [1, 2, 3]
    assert c.session.calls[1]["cursor"] == "FL.2"
    assert c.last_page.resume == "FL.3"
    assert c.last_page.monthly_remaining == 497


def test_max_records_limits_the_page_size():
    c = client(FakeResponse(200, {"ok": True, "rows": [{"n": 1}] * 10, "cursor": "FL.10", "resume": "FL.10"}))
    assert len(list(c.records(states="FL", max_records=10))) == 10
    assert c.session.calls[0]["limit"] == 10


def test_busy_is_retried(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    c = client(FakeResponse(503, {"ok": False, "error": "busy"}, {"Retry-After": "1"}),
               FakeResponse(200, {"ok": True, "states": []}))
    assert c.states() == []


@pytest.mark.parametrize("status,error", [(400, BadRequest), (401, AuthError), (429, OutOfRecords)])
def test_errors_raise_the_right_exception(status, error):
    c = client(FakeResponse(status, {"ok": False, "error": "nope"}))
    with pytest.raises(error) as e:
        c.states()
    assert e.value.message == "nope"
