# ListRiver API example: daily feed. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
import json, os, requests

API = "https://listriver.com/api/data.ashx"
HEADERS = {"X-Api-Key": "YOUR_KEY"}
SAVED = "listriver-feed.json"
filters = {"action": "records", "entityType": "LLC", "preset": "recent", "limit": 1000}

positions = json.load(open(SAVED)) if os.path.exists(SAVED) else {}

for state in ["FL", "GA", "TX"]:                       # one state per feed
    params = dict(filters, states=state)
    if positions.get(state):
        params["cursor"] = positions[state]
    while True:
        r = requests.get(API, headers=HEADERS, params=params, timeout=120)
        r.raise_for_status()
        data = r.json()
        for row in data["rows"]:
            print(row["listriverId"], row["businessName"])   # or save to your CRM, keyed by listriverId
        if data["resume"]:
            positions[state] = data["resume"]
            json.dump(positions, open(SAVED, "w"))     # saved after every page: a crash never pays twice
        if not data["cursor"]:
            break
        params["cursor"] = data["cursor"]
