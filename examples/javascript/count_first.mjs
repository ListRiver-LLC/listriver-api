// ListRiver API example: count first. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
// Node 18+ (save as an .mjs file) or a browser console
const params = new URLSearchParams({ action: "count", states: "FL", city: "MIAMI", hasPhone: 1, formedWithin: 3 });
const res = await fetch(`https://listriver.com/api/data.ashx?${params}`, {
  headers: { "X-Api-Key": "YOUR_KEY" },
});
const data = await res.json();
if (!res.ok) throw new Error(data.error);
console.log(data);
