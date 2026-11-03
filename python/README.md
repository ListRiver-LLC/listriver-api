# listriver (Python)

Python client for the [ListRiver Business Data API](https://listriver.com/api-docs): active U.S. businesses from official state business registries.

```
pip install listriver
```

```python
from listriver import Client

lr = Client("lr_key_...")          # free key: https://listriver.com/Account/ApiSignUp.aspx

# Free: how many records a search would use
print(lr.count(states="FL", city="MIAMI", has_phone=True, formed_within=3))

# Every matching record, paged for you (each record returned counts against your records)
for b in lr.records(states="FL", city="MIAMI", has_phone=True, formed_within=3, max_records=100):
    print(b["businessName"], b["phone"], b["listriverId"])

print("left this month:", lr.last_page.monthly_remaining)
print("save this to carry on later:", lr.last_page.resume)
```

Filters: `states`, `city`, `county`, `zip` (the last three need `states`), `naics`, `entity_type`, `has_phone`, `has_email`,
`formed_within` (months), `formed_from` / `formed_to` (`"YYYY-MM"`), `preset` (`"recent"`, `"year"`, `"all"`).
Lists are accepted anywhere several values are: `states=["FL", "GA"]`.

Errors raise `AuthError` (401), `BadRequest` (400), `OutOfRecords` (429) or `ListRiverError`. A busy answer (503, nothing charged)
is retried automatically.

MIT license. The data you receive is covered by the [ListRiver API agreement](https://listriver.com/legal/listriver-api-eula.txt).
