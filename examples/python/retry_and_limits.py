# ListRiver API example: retry and limits. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
import time, requests

API = "https://listriver.com/api/data.ashx"
HEADERS = {"X-Api-Key": "YOUR_KEY"}

def get_page(params):
    for attempt in range(5):
        r = requests.get(API, headers=HEADERS, params=params, timeout=120)
        if r.status_code == 503:                       # busy: nothing was charged
            time.sleep(int(r.headers.get("Retry-After", "60")))
            continue
        if r.status_code == 429:                       # out of records (or too many count calls)
            raise SystemExit(r.json()["error"])          # the message says how to get more
        r.raise_for_status()
        print("left:", r.headers.get("X-ListRiver-Monthly-Remaining"), "+ packs:", r.headers.get("X-ListRiver-Credits-Remaining"))
        return r.json()
    raise RuntimeError("ListRiver stayed busy; try again later")
