// ListRiver API example: county to csv. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
// Node 18+ (save as an .mjs file)
import { writeFileSync, appendFileSync } from "node:fs";

const API = "https://listriver.com/api/data.ashx";
const headers = { "X-Api-Key": "YOUR_KEY" };
const params = { action: "records", limit: 1000, states: "TX", county: "HARRIS", naics: "23", formedWithin: 6 };
const cell = (v) => (v === null ? "" : `"${String(v).replace(/"/g, '""')}"`);

let header = null;
while (true) {
  const res = await fetch(`$https://listriver.com/api/data.ashx?${new URLSearchParams(params)}`, { headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  for (const row of data.rows) {
    if (!header) {
      header = Object.keys(row);
      writeFileSync("harris-construction.csv", header.join(",") + "\n");
    }
    appendFileSync("harris-construction.csv", header.map((k) => cell(row[k])).join(",") + "\n");
  }
  console.log("records left:", res.headers.get("X-ListRiver-Monthly-Remaining"));
  if (!data.cursor) break;
  params.cursor = data.cursor;   // save this to resume later without paying twice
}
