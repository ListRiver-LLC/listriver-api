# Examples

Runnable examples for the [ListRiver Business Data API](https://listriver.com/api-docs). Replace `YOUR_KEY` with your key
([get a free one](https://listriver.com/Account/ApiSignUp.aspx): 500 records a month).

| Example | What it does | Python | JavaScript (Node 18+) | curl |
|---|---|---|---|---|
| count_first | How many records a search would use (free) | [py](python/count_first.py) | [mjs](javascript/count_first.mjs) | [sh](curl/count_first.sh) |
| first_page | The first 2 records of a search, with the remaining-records headers | [py](python/first_page.py) | [mjs](javascript/first_page.mjs) | [sh](curl/first_page.sh) |
| county_to_csv | New construction companies (NAICS 23) in Harris County, TX, to a CSV file | [py](python/county_to_csv.py) | [mjs](javascript/county_to_csv.mjs) | [sh](curl/county_to_csv.sh) |
| daily_feed | A per-state feed of new LLCs that saves its position, so it never pays twice | [py](python/daily_feed.py) | [mjs](javascript/daily_feed.mjs) | |
| retry_and_limits | Waiting on 503 (nothing charged) and stopping on 429 | [py](python/retry_and_limits.py) | [mjs](javascript/retry_and_limits.mjs) | |
| with_the_client | The Miami search using the `listriver` Python package | [py](python/with_the_client.py) | | |

Python examples need `pip install requests` (or `pip install listriver` for the last one). The curl `county_to_csv` example needs
[jq](https://jqlang.github.io/jq/). C# and PHP versions of every example are on the [documentation page](https://listriver.com/api-docs#recipes).

Every record returned counts against your records each time it is returned. Run `count_first` before a large pull.
