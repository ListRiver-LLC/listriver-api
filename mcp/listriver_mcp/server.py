"""ListRiver MCP server: lets AI assistants search new and active U.S. businesses from state registries.

Run with `uvx listriver-mcp` and set LISTRIVER_API_KEY (free key: https://listriver.com/Account/ApiSignUp.aspx).
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from listriver import AuthError, BadRequest, Client, ListRiverError, OutOfRecords
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

KEY_URL = "https://listriver.com/Account/ApiSignUp.aspx"
MAX_SEARCH = 100

INSTRUCTIONS = f"""ListRiver has active U.S. businesses from official state business registries (new LLCs, corporations,
nonprofits, partnerships), with address, county, registered agent, formation month and, where available, phone, email,
website, EIN and NAICS industry.

How to use these tools well:
- count_businesses is free. Call it first to see how many businesses match before searching.
- search_businesses uses the user's ListRiver records: every business returned counts, each time it is returned.
  Ask for only as many as the user needs (default 25, at most {MAX_SEARCH} per call), and don't repeat the same search.
  To get more of the same search, pass the cursor from the previous answer.
- city, county and zip need states. Formation dates are month-level (formed_within counts whole calendar months).
- Phone, email, NAICS and county are on file for only part of the records, and coverage varies by state:
  use has_phone / has_email / naics with count_businesses to check before promising them.
- Data is for the user's own business use; it may not be used for credit, insurance, employment or housing decisions."""

READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=True)

server = MCPServer(
    name="ListRiver",
    title="ListRiver business registry data",
    instructions=INSTRUCTIONS,
    website_url="https://listriver.com/api-docs",
    version="0.1.0",
)

_client: Optional[Client] = None


def _get_client() -> Client:
    global _client
    if _client is None:
        key = (os.environ.get("LISTRIVER_API_KEY") or "").strip()
        if not key:
            raise ListRiverError(401, f"LISTRIVER_API_KEY is not set. Get a free key at {KEY_URL} and add it to this MCP server's environment.")
        _client = Client(key)
    return _client


def _filters(states, city, county, zip, naics, entity_type, has_phone, has_email, formed_within, formed_from, formed_to) -> Dict[str, Any]:
    return dict(states=states, city=city, county=county, zip=zip, naics=naics, entity_type=entity_type,
                has_phone=has_phone, has_email=has_email, formed_within=formed_within,
                formed_from=formed_from, formed_to=formed_to)


def _error(e: ListRiverError) -> Dict[str, Any]:
    hint = None
    if isinstance(e, AuthError):
        hint = f"Check LISTRIVER_API_KEY. A free key is at {KEY_URL}."
    elif isinstance(e, OutOfRecords):
        hint = "The user's records are used up. They can buy a pack or plan at https://listriver.com/Account/Api.aspx (count_businesses is still free)."
    elif isinstance(e, BadRequest):
        hint = "Fix the parameter the message names and try again."
    return {"ok": False, "status": e.status, "error": e.message, "hint": hint}


@server.tool(annotations=READ_ONLY)
def list_states() -> Dict[str, Any]:
    """List the states ListRiver covers, with how many businesses each has: formed this month or last ("recent"),
    in the last 12 months ("year"), and every active business ("all"). Free."""
    try:
        return {"ok": True, "states": _get_client().states()}
    except ListRiverError as e:
        return _error(e)


@server.tool(annotations=READ_ONLY)
def count_businesses(
    states: Optional[str] = None,
    city: Optional[str] = None,
    county: Optional[str] = None,
    zip: Optional[str] = None,
    naics: Optional[str] = None,
    entity_type: Optional[str] = None,
    has_phone: bool = False,
    has_email: bool = False,
    formed_within: Optional[int] = 1,
    formed_from: Optional[str] = None,
    formed_to: Optional[str] = None,
) -> Dict[str, Any]:
    """Count businesses matching the filters, per state. Free: use it before search_businesses.

    Args:
        states: Comma-separated two-letter registration states, e.g. "FL" or "FL,TX". Required with city, county or zip.
        city: Comma-separated business cities, e.g. "MIAMI".
        county: Comma-separated counties, e.g. "MIAMI-DADE" (or "FL:MIAMI-DADE").
        zip: Comma-separated 5-digit ZIP codes or 3-digit ZIP prefixes, e.g. "33139,331".
        naics: Comma-separated NAICS prefixes, 2-6 digits, e.g. "23" (construction) or "722511".
        entity_type: Comma-separated of LLC, CORP, LP, LLP, NONPROFIT, OTHER.
        has_phone: Only businesses with a phone number on file.
        has_email: Only businesses with an email on file.
        formed_within: Formed in the current month or the N months before it (1 = this month or last). Set 0 for any formation date.
        formed_from: First formation month, "YYYY-MM" (overrides formed_within).
        formed_to: Last formation month, "YYYY-MM" (overrides formed_within).
    """
    try:
        f = _filters(states, city, county, zip, naics, entity_type, has_phone, has_email,
                     _window(formed_within, formed_from, formed_to), formed_from, formed_to)
        if f["formed_within"] is None and not formed_from and not formed_to:
            f["preset"] = "all"
        return {"ok": True, **_get_client().count(**f)}
    except ListRiverError as e:
        return _error(e)


@server.tool(annotations=READ_ONLY)
def search_businesses(
    states: Optional[str] = None,
    city: Optional[str] = None,
    county: Optional[str] = None,
    zip: Optional[str] = None,
    naics: Optional[str] = None,
    entity_type: Optional[str] = None,
    has_phone: bool = False,
    has_email: bool = False,
    formed_within: Optional[int] = 1,
    formed_from: Optional[str] = None,
    formed_to: Optional[str] = None,
    limit: int = 25,
    cursor: Optional[str] = None,
) -> Dict[str, Any]:
    """Get businesses matching the filters (same filters as count_businesses). USES THE USER'S RECORDS: each business
    returned counts, every time it is returned, so ask only for what the user needs.

    Args:
        states: Comma-separated two-letter registration states. Required with city, county or zip.
        city: Comma-separated business cities.
        county: Comma-separated counties.
        zip: Comma-separated 5-digit ZIP codes or 3-digit prefixes.
        naics: Comma-separated NAICS prefixes, 2-6 digits.
        entity_type: Comma-separated of LLC, CORP, LP, LLP, NONPROFIT, OTHER.
        has_phone: Only businesses with a phone number on file.
        has_email: Only businesses with an email on file.
        formed_within: Formed in the current month or the N months before it (1 = this month or last; 0 = any date).
        formed_from: First formation month, "YYYY-MM".
        formed_to: Last formation month, "YYYY-MM".
        limit: How many businesses to return, 1-100 (default 25).
        cursor: The cursor from a previous search_businesses answer, to get the next businesses of the same search.
    """
    try:
        f = _filters(states, city, county, zip, naics, entity_type, has_phone, has_email,
                     _window(formed_within, formed_from, formed_to), formed_from, formed_to)
        if f["formed_within"] is None and not formed_from and not formed_to:
            f["preset"] = "all"
        page = _get_client().page(limit=max(1, min(MAX_SEARCH, int(limit))), cursor=cursor, **f)
        return {
            "ok": True,
            "count": len(page.rows),
            "businesses": page.rows,
            "cursor": page.cursor,
            "more": page.has_more,
            "records_left_this_period": page.monthly_remaining,
            "pack_records_left": page.credits_remaining,
        }
    except ListRiverError as e:
        return _error(e)


def _window(formed_within: Optional[int], formed_from: Optional[str], formed_to: Optional[str]) -> Optional[int]:
    if formed_from or formed_to:
        return None
    if formed_within is None or int(formed_within) <= 0:
        return None
    return int(formed_within)


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
