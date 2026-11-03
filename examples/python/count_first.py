# ListRiver API example: count first. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
import requests

r = requests.get(
    "https://listriver.com/api/data.ashx",
    headers={"X-Api-Key": "YOUR_KEY"},
    params={"action": "count", "states": "FL", "city": "MIAMI", "hasPhone": 1, "formedWithin": 3},
    timeout=120,
)
r.raise_for_status()
print(r.json())
