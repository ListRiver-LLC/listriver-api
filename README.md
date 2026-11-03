# ListRiver Business Data API

**New and active U.S. businesses from official state business registries (Secretary of State filings), as JSON.**
New LLCs, corporations, nonprofits and partnerships, filtered by state, city, county, ZIP, NAICS industry, entity type,
formation month, and whether a phone or email is on file.

- **Free key: 500 records a month**, no card needed: [get one here](https://listriver.com/Account/ApiSignUp.aspx)
- **Full documentation** with a live "Try it" panel and examples in cURL, Python, JavaScript, C# and PHP: [listriver.com/api-docs](https://listriver.com/api-docs)
- **Python client:** `pip install listriver` ([source](python/))
- **OpenAPI 3 spec:** [openapi.yaml](openapi.yaml) (import into Postman, Insomnia, Swagger UI or an AI agent)
- **MCP server** for Claude and other AI assistants, source in [`mcp/`](mcp/): `uvx listriver-mcp`

Typical uses: lead lists of brand-new businesses (formed this month), CRM enrichment, sales territory research,
KYB and business verification, market sizing, and B2B prospecting by industry and place.

---

## Quick start (2 minutes)

1. [Create a free API account](https://listriver.com/Account/ApiSignUp.aspx) and click the link in the confirmation email.
2. On the API page, click **Get my free API key** and copy it.
3. Count a search (free), then pull the records:

```bash
# How many businesses formed in Miami in the last few months have a phone number? (free)
curl -H "X-Api-Key: YOUR_KEY" "https://listriver.com/api/data.ashx?action=count&states=FL&city=MIAMI&hasPhone=1&formedWithin=3"

# The first 10 of them
curl -H "X-Api-Key: YOUR_KEY" "https://listriver.com/api/data.ashx?action=records&states=FL&city=MIAMI&hasPhone=1&formedWithin=3&limit=10"
```

```json
{
  "ok": true,
  "rows": [
    {
      "businessName": "ANGELI TRAVEL LLC",
      "entityType": "LIMITED LIABILITY COMPANY",
      "status": "ACTIVE",
      "formed": "2026-08",
      "registrationState": "FL",
      "stateFilingNumber": "L26000446708",
      "address": "2125 BISCAYNE BLVD, STE 204 #27572",
      "city": "MIAMI",
      "zip": "33137",
      "county": "MIAMI-DADE",
      "phone": "(786) 298-9566",
      "website": "HTTPS://ANGELITRAVELS.COM",
      "registeredAgent": "ULLOA SANCHEZ YUDELSA",
      "listriverId": "FL-L26000446708",
      "...": "35 fields in all"
    }
  ],
  "cursor": "FL.6604750",
  "resume": "FL.6604750"
}
```

### Python

```python
from listriver import Client

lr = Client("YOUR_KEY")
search = dict(states="FL", city="MIAMI", has_phone=True, formed_within=3)

print(lr.count(**search))                      # free
for business in lr.records(**search, max_records=100):
    print(business["businessName"], business["phone"])
```

More: [examples/](examples/) (Python, JavaScript, curl) and the [recipes](https://listriver.com/api-docs#recipes) (also C# and PHP).

---

## MCP server (source in this repo)

This repository contains a **Model Context Protocol server** for ListRiver, written in Python:
[`mcp/listriver_mcp/server.py`](mcp/listriver_mcp/server.py) (package [`mcp/`](mcp/), tests in [`mcp/tests/`](mcp/tests/),
MIT license). It runs over stdio and gives AI assistants (Claude Desktop, Claude Code, Cursor and other MCP clients) three tools:

| Tool | What it does | Cost |
|---|---|---|
| `list_states` | States covered and their record counts | free |
| `count_businesses` | How many businesses match a search (state, city, county, ZIP, NAICS, entity type, formation month, phone/email on file) | free |
| `search_businesses` | The matching businesses, 25 by default and up to 100 per call, with a cursor for more | counts against your records |

The server tells the assistant to count first and to fetch only what you need.

**Install from PyPI** (published from this repo's `mcp/` folder) and add it to Claude Desktop (Settings > Developer > Edit Config):

```json
{
  "mcpServers": {
    "listriver": {
      "command": "uvx",
      "args": ["listriver-mcp"],
      "env": { "LISTRIVER_API_KEY": "lr_key_..." }
    }
  }
}
```

**Or run it from source:**

```bash
git clone https://github.com/ListRiver-LLC/listriver-api && cd listriver-api
pip install ./python ./mcp
LISTRIVER_API_KEY=lr_key_... listriver-mcp

# or with Docker, using the Dockerfile in this repo
docker build -t listriver-mcp .
docker run -i --rm -e LISTRIVER_API_KEY=lr_key_... listriver-mcp
```

Setup for other clients: [mcp/README.md](mcp/). Listed in the official MCP Registry as `io.github.ListRiver-LLC/listriver`.

---

## Calls

Every call is an HTTPS `GET` to `https://listriver.com/api/data.ashx` with your key in the `X-Api-Key` header.

| `action` | What it returns | Cost |
|---|---|---|
| `states` | Available states and record counts per formation window | free |
| `count` | How many records match your filters, per state | free (20 calls a minute) |
| `records` | Up to 1,000 matching records per call; pass `cursor` back for the next page | each record returned counts |

## Filters

`records` and `count` take the same filters. A record must match all of them; where a filter takes several
comma-separated values, any one of them matches.

| Parameter | Example | What it does |
|---|---|---|
| `states` | `FL,TX` | Registration states (leave out for all) |
| `city` | `MIAMI,DORAL` | Business city (needs `states`) |
| `county` | `MIAMI-DADE` or `FL:MIAMI-DADE` | Business county (needs `states`) |
| `zip` | `33139,33140` or `331` | 5-digit ZIPs or 3-digit prefixes (needs `states`) |
| `naics` | `23`, `2361`, `236115` | NAICS industry prefix, 2 to 6 digits |
| `entityType` | `LLC,CORP` | `LLC`, `CORP`, `LP`, `LLP`, `NONPROFIT`, `OTHER` |
| `hasPhone` / `hasEmail` | `1` | Only businesses with a phone / email on file |
| `formedWithin` | `3` | Formed this month or in the N months before it |
| `formedFrom` / `formedTo` | `2026-06` / `2026-09` | Formed in this range of months |
| `preset` | `recent` (default), `year`, `all` | Shortcut windows |

Formation dates are month-level (registries publish the month), so windows are whole calendar months.

## Pricing

| Plan | Records | Price |
|---|---|---|
| Free | 500 / month | $0 |
| Prepaid packs | 5,000 / 7,500 / 10,000 (use within 12 months) | $50 / $75 / $100 |
| Monthly plans | 5,000 / 12,000 / 28,000 / 75,000 per month | $50 / $100 / $200 / $450 |
| AWS Marketplace | larger volumes, billed on your AWS invoice | see listing |

Only records returned count, and **each record counts every time it is returned**: overlapping or repeated searches
count again. Count first (free), save the `cursor` or `resume` position to carry on later, and use `listriverId` to
de-duplicate. Packs and plans are on your [API page](https://listriver.com/Account/Api.aspx). Current prices are always
on [listriver.com/api-docs](https://listriver.com/api-docs).

## Keeping a feed up to date

Every `records` answer includes `resume`: the position after the last record returned, even on the last page. Save it per
state, and pass it as `cursor` next time to get only the businesses ListRiver has added since. See
[examples/python/daily_feed.py](examples/python/daily_feed.py).

## Sample data

[sample-data/](sample-data/) has a small sample of recent Florida formations (CSV and JSON, no emails) so you can judge the
data before signing up. It is a sample, not a full file.

## Data and terms

Records come from official state business registries, with addresses standardized and contact details, NAICS codes and
EINs added where available. A field is `null` when the state doesn't publish it or ListRiver doesn't have it; nothing is
estimated. Coverage and update schedules: [listriver.com/methodology](https://listriver.com/methodology).

The code in this repository is MIT-licensed. The data (including `sample-data/`) is covered by the
[ListRiver API agreement](https://listriver.com/legal/listriver-api-eula.txt): for your own business use, not for resale,
and not for credit, insurance, employment or housing decisions.

Questions: [support@listriver.com](mailto:support@listriver.com)
