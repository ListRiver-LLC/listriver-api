#!/usr/bin/env bash
# ListRiver API example: county to csv. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
# bash + jq: every page goes to records.jsonl, then one CSV
API="https://listriver.com/api/data.ashx"
cursor=""
: > records.jsonl
while :; do
  page=$(curl -s -H "X-Api-Key: YOUR_KEY" "$API?action=records&limit=1000&states=TX&county=HARRIS&naics=23&formedWithin=6${cursor:+&cursor=$cursor}")
  echo "$page" | jq -c '.rows[]' >> records.jsonl
  cursor=$(echo "$page" | jq -r '.cursor // empty')   # save this to resume later without paying twice
  [ -z "$cursor" ] && break
done
jq -r -s '(.[0] | keys_unsorted) as $k | ($k | @csv), (.[] | [.[$k[]]] | @csv)' records.jsonl > harris-construction.csv
