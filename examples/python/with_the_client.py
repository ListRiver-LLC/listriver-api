# ListRiver API example: the same search with the `listriver` package (pip install listriver).
# Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
import csv

from listriver import Client

lr = Client("YOUR_KEY")
search = dict(states="FL", city="MIAMI", has_phone=True, formed_within=3)

print(lr.count(**search)["total"], "matching records (counting is free)")

with open("miami.csv", "w", newline="", encoding="utf-8") as f:
    writer = None
    for business in lr.records(**search, max_records=500):
        if writer is None:
            writer = csv.DictWriter(f, fieldnames=list(business.keys()))
            writer.writeheader()
        writer.writerow(business)

print("records left this month:", lr.last_page.monthly_remaining)
print("save this to carry on later without paying twice:", lr.last_page.resume)
