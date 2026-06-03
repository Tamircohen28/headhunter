#!/usr/bin/env node
// Sync jobtrack applications to a Notion database. Idempotent via notion_page_id.
// Env: NOTION_TOKEN, NOTION_DATABASE_ID
// The target DB must have properties: Company (title), Role, Status, Priority,
// Location, Source, Job URL, Applied Date.
// Usage: node sync-notion.js [--dry-run]
const { load, save } = require("./lib");

const TOKEN = process.env.NOTION_TOKEN;
const DB = process.env.NOTION_DATABASE_ID;
const dry = process.argv.includes("--dry-run");
const NOTION_VERSION = "2022-06-28";

if (!dry && (!TOKEN || !DB)) { console.error("NOTION_TOKEN and NOTION_DATABASE_ID required. Use --dry-run to preview."); process.exit(1); }

function props(a) {
  const rich = (v) => v ? { rich_text: [{ text: { content: String(v) } }] } : { rich_text: [] };
  return {
    Company: { title: [{ text: { content: a.company || "(untitled)" } }] },
    Role: rich(a.role),
    Status: { select: a.status ? { name: a.status } : null },
    Priority: { select: a.priority ? { name: a.priority } : null },
    Location: rich(a.location),
    Source: rich(a.source),
    "Job URL": a.job_url ? { url: a.job_url } : { url: null },
    "Applied Date": a.applied_date ? { date: { start: String(a.applied_date).slice(0, 10) } } : { date: null },
  };
}

async function notion(pathUrl, method, body) {
  const res = await fetch(`https://api.notion.com${pathUrl}`, {
    method,
    headers: { Authorization: `Bearer ${TOKEN}`, "Notion-Version": NOTION_VERSION, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

(async () => {
  const apps = load("applications");
  let created = 0, updated = 0;
  for (const a of apps) {
    if (dry) { console.log(`[dry-run] ${a.notion_page_id ? "PATCH" : "POST"} Notion: ${a.company} — ${a.role} (${a.status})`); continue; }
    try {
      if (a.notion_page_id) { await notion(`/v1/pages/${a.notion_page_id}`, "PATCH", { properties: props(a) }); updated++; }
      else { const page = await notion("/v1/pages", "POST", { parent: { database_id: DB }, properties: props(a) }); a.notion_page_id = page.id; created++; }
    } catch (e) { console.error(`Notion error for ${a.company}: ${e.message}`); }
  }
  if (!dry) { save("applications", apps); console.error(`Notion sync: ${created} created, ${updated} updated.`); }
  else console.error(`[dry-run] ${apps.length} application(s) would sync.`);
})();
