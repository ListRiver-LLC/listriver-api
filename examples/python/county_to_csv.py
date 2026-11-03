# ListRiver API example: county to csv. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
import csv, requests

API = "https://listriver.com/api/data.ashx"
HEADERS = {"X-Api-Key": "YOUR_KEY"}
params = {"action": "records", "limit": 1000, "states": "TX", "county": "HARRIS", "naics": "23", "formedWithin": 6}

with open("harris-construction.csv", "w", newline="", encoding="utf-8") as f:
    writer = None
    while True:
        r = requests.get(API, headers=HEADERS, params=params, timeout=120)
        r.raise_for_status()
        data = r.json()
        for row in data["rows"]:
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=list(row.keys()))
                writer.writeheader()
            writer.writerow(row)
        print("records left:", r.headers.get("X-ListRiver-Monthly-Remaining"))
        if not data["cursor"]:
            break
        params["cursor"] = data["cursor"]   # save this to resume later without paying twice
