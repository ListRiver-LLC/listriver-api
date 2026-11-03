// ListRiver API example: daily feed. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
// Node 18+ (save as an .mjs file)
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const API = "https://listriver.com/api/data.ashx";
const headers = { "X-Api-Key": "YOUR_KEY" };
const SAVED = "listriver-feed.json";
const filters = { action: "records", entityType: "LLC", preset: "recent", limit: 1000 };
const positions = existsSync(SAVED) ? JSON.parse(readFileSync(SAVED, "utf8")) : {};

for (const state of ["FL", "GA", "TX"]) {             // one state per feed
  const params = { ...filters, states: state };
  if (positions[state]) params.cursor = positions[state];
  while (true) {
    const res = await fetch(`$https://listriver.com/api/data.ashx?${new URLSearchParams(params)}`, { headers });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    for (const row of data.rows) console.log(row.listriverId, row.businessName);   // or save to your CRM
    if (data.resume) {
      positions[state] = data.resume;
      writeFileSync(SAVED, JSON.stringify(positions));   // saved after every page: a crash never pays twice
    }
    if (!data.cursor) break;
    params.cursor = data.cursor;
  }
}
