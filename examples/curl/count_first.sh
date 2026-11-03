#!/usr/bin/env bash
# ListRiver API example: count first. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
curl -H "X-Api-Key: YOUR_KEY" "https://listriver.com/api/data.ashx?action=count&states=FL&city=MIAMI&hasPhone=1&formedWithin=3"
