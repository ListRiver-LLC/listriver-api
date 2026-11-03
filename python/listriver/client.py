"""ListRiver Business Data API client."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

import requests

DEFAULT_BASE_URL = "https://listriver.com/api/data.ashx"

# Python-style argument names -> the API's parameter names.
_PARAM_NAMES = {
    "states": "states",
    "city": "city",
    "county": "county",
    "zip": "zip",
    "naics": "naics",
    "entity_type": "entityType",
    "has_phone": "hasPhone",
    "has_email": "hasEmail",
    "formed_within": "formedWithin",
    "formed_from": "formedFrom",
    "formed_to": "formedTo",
    "preset": "preset",
    "email": "email",
}

FilterValue = Union[str, int, bool, Iterable[str], None]


class ListRiverError(Exception):
    """An error answer from the API. `status` is the HTTP status code."""

    def __init__(self, status: int, message: str):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message


class AuthError(ListRiverError):
    """401: missing or unknown API key."""


class BadRequest(ListRiverError):
    """400: a parameter is wrong. The message says which."""


class OutOfRecords(ListRiverError):
    """429: your records are used up (or too many count calls). The message says how to get more."""


@dataclass
class Page:
    """One answer from action=records."""

    rows: List[Dict[str, Any]]
    cursor: Optional[str]
    resume: Optional[str]
    monthly_allowance: Optional[int] = None
    monthly_remaining: Optional[int] = None
    allowance_resets: Optional[str] = None
    credits_remaining: Optional[int] = None

    @property
    def has_more(self) -> bool:
        return self.cursor is not None


@dataclass
class Client:
    """
    Client for https://listriver.com/api-docs.

        lr = Client("lr_key_...")
        print(lr.count(states="FL", city="MIAMI", has_phone=True, formed_within=3))
        for business in lr.records(states="FL", city="MIAMI", has_phone=True, formed_within=3):
            print(business["businessName"], business["phone"])

    Every record returned counts against your records each time it is returned. Use count() (free) first,
    and keep page.resume to carry on later without paying twice.
    """

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 120.0
    max_retries: int = 5
    session: requests.Session = field(default_factory=requests.Session, repr=False)
    last_page: Optional[Page] = field(default=None, init=False, repr=False)

    # ------------------------------------------------------------------ calls

    def states(self) -> List[Dict[str, Any]]:
        """Available states and their record counts per window (recent, year, all). Free."""
        return self._get({"action": "states"})["states"]

    def count(self, **filters: FilterValue) -> Dict[str, Any]:
        """How many records match, per state: {'total': n, 'states': [{'code', 'count'}], 'approximate': True}. Free."""
        data = self._get({"action": "count", **self._filters(filters)})
        return {"total": data["total"], "states": data["states"], "approximate": data.get("approximate", True)}

    def page(self, limit: int = 1000, cursor: Optional[str] = None, **filters: FilterValue) -> Page:
        """One page of records (up to 1,000). Pass page.cursor back for the next one."""
        params = {"action": "records", "limit": max(1, min(1000, int(limit))), **self._filters(filters)}
        if cursor:
            params["cursor"] = cursor
        data, headers = self._get(params, with_headers=True)
        page = Page(
            rows=data["rows"],
            cursor=data.get("cursor"),
            resume=data.get("resume"),
            monthly_allowance=_int(headers.get("X-ListRiver-Monthly-Allowance")),
            monthly_remaining=_int(headers.get("X-ListRiver-Monthly-Remaining")),
            allowance_resets=headers.get("X-ListRiver-Allowance-Resets"),
            credits_remaining=_int(headers.get("X-ListRiver-Credits-Remaining")),
        )
        self.last_page = page
        return page

    def records(self, cursor: Optional[str] = None, max_records: Optional[int] = None,
                **filters: FilterValue) -> Iterator[Dict[str, Any]]:
        """
        Every matching record, page by page. Stops at the end, or after max_records.
        After (or during) the loop, client.last_page.resume is the position to save for next time.
        """
        served = 0
        while True:
            want = 1000 if max_records is None else min(1000, max_records - served)
            if want <= 0:
                return
            page = self.page(limit=want, cursor=cursor, **filters)
            for row in page.rows:
                yield row
            served += len(page.rows)
            if not page.cursor:
                return
            cursor = page.cursor

    # ------------------------------------------------------------------ plumbing

    @staticmethod
    def _filters(filters: Dict[str, FilterValue]) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for name, value in filters.items():
            if value is None or value is False:
                continue
            key = _PARAM_NAMES.get(name)
            if key is None:
                raise TypeError(f"Unknown filter '{name}'. Known: {', '.join(sorted(_PARAM_NAMES))}")
            if value is True:
                out[key] = "1"
            elif isinstance(value, (list, tuple, set)):
                out[key] = ",".join(str(v) for v in value)
            else:
                out[key] = str(value)
        return out

    def _get(self, params: Dict[str, Any], with_headers: bool = False):
        for attempt in range(self.max_retries):
            r = self.session.get(self.base_url, params=params, headers={"X-Api-Key": self.api_key},
                                 timeout=self.timeout)
            if r.status_code == 503 and attempt < self.max_retries - 1:
                # Busy (usually just after an update): nothing was charged. Wait and try again.
                time.sleep(_int(r.headers.get("Retry-After")) or 60)
                continue
            try:
                data = r.json()
            except ValueError:
                raise ListRiverError(r.status_code, r.text[:300] or "Not a JSON answer")
            if r.status_code != 200 or not data.get("ok", False):
                message = data.get("error") or f"HTTP {r.status_code}"
                error = {400: BadRequest, 401: AuthError, 429: OutOfRecords}.get(r.status_code, ListRiverError)
                raise error(r.status_code, message)
            return (data, r.headers) if with_headers else data
        raise ListRiverError(503, "ListRiver stayed busy; try again later")


def _int(value: Optional[str]) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None
