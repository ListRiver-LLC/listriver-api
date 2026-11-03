#!/usr/bin/env bash
# ListRiver API example: first page. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
curl -i -H "X-Api-Key: YOUR_KEY" "https://listriver.com/api/data.ashx?action=records&states=FL&city=MIAMI&hasPhone=1&formedWithin=3&limit=2"
