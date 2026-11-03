# ListRiver API example: first page. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
import requests

r = requests.get(
    "https://listriver.com/api/data.ashx",
    headers={"X-Api-Key": "YOUR_KEY"},
    params={"action": "records", "states": "FL", "city": "MIAMI", "hasPhone": 1, "formedWithin": 3, "limit": 2},
    timeout=120,
)
r.raise_for_status()
print("left:", r.headers.get("X-ListRiver-Monthly-Remaining"))
print(r.json())
