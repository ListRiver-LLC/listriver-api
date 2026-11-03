# ListRiver MCP server

<!-- mcp-name: io.github.ListRiver-LLC/listriver -->

Lets Claude and other AI assistants search **new and active U.S. businesses from official state business registries**
through [ListRiver](https://listriver.com/api-docs): new LLCs, corporations and nonprofits by state, city, county, ZIP,
NAICS industry, entity type, formation month, and whether a phone or email is on file.

Ask things like:

- "How many businesses were formed in Miami-Dade in the last 3 months that have a phone number?"
- "Find 20 new construction companies in Harris County, Texas."
- "List new LLCs in ZIP 80202 formed this month, with their registered agents."

## Tools

| Tool | What it does | Cost |
|---|---|---|
| `list_states` | States covered and their record counts | free |
| `count_businesses` | How many businesses match a search, per state | free |
| `search_businesses` | The matching businesses (25 by default, up to 100 per call; `cursor` for more) | each business returned counts against your ListRiver records |

The assistant is told to count first and to ask only for as many businesses as you need.

## Setup

1. Get a free API key (500 records a month): [listriver.com/Account/ApiSignUp.aspx](https://listriver.com/Account/ApiSignUp.aspx)
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (it runs the server with `uvx`, no other install needed).
3. Add the server to your AI app.

**Claude Desktop** (Settings > Developer > Edit Config, then restart Claude Desktop):

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

**Claude Code:**

```bash
claude mcp add listriver -e LISTRIVER_API_KEY=lr_key_... -- uvx listriver-mcp
```

**Other MCP clients:** run `uvx listriver-mcp` (stdio) with `LISTRIVER_API_KEY` in the environment. Or `pip install listriver-mcp`
and run `listriver-mcp`.

## Notes

- Every business returned counts against your records each time it is returned; repeated or overlapping searches count
  again. Counting is free.
- Phone, email, NAICS and county are on file for only part of the records, and coverage varies by state.
- The data is for your own business use, not for resale or for credit, insurance, employment or housing decisions
  ([ListRiver API agreement](https://listriver.com/legal/listriver-api-eula.txt)).
- More: [API documentation](https://listriver.com/api-docs) - [support@listriver.com](mailto:support@listriver.com)

MIT license.
