// ListRiver API example: retry and limits. Replace YOUR_KEY with your key (free: https://listriver.com/Account/ApiSignUp.aspx).
const API = "https://listriver.com/api/data.ashx";
const headers = { "X-Api-Key": "YOUR_KEY" };

async function getPage(params) {
  for (let attempt = 0; attempt < 5; attempt++) {
    const res = await fetch(`$https://listriver.com/api/data.ashx?${new URLSearchParams(params)}`, { headers });
    if (res.status === 503) {                        // busy: nothing was charged
      const wait = Number(res.headers.get("Retry-After") || 60);
      await new Promise((r) => setTimeout(r, wait * 1000));
      continue;
    }
    const data = await res.json();
    if (res.status === 429) throw new Error(data.error);   // out of records: the message says how to get more
    if (!res.ok) throw new Error(data.error);
    console.log("left:", res.headers.get("X-ListRiver-Monthly-Remaining"), "+ packs:", res.headers.get("X-ListRiver-Credits-Remaining"));
    return data;
  }
  throw new Error("ListRiver stayed busy; try again later");
}
