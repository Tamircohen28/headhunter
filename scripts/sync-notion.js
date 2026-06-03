#!/usr/bin/env node
// Sync headhunter applications AND tasks to Notion databases. Idempotent via notion_page_id / notion_task_page_id.
// Env: NOTION_TOKEN, NOTION_DATABASE_ID (apps), NOTION_TASKS_DATABASE_ID (tasks, optional)
// Apps DB properties: Company (title), Role, Status, Priority, Location, Source, Job URL, Applied Date.
// Tasks DB properties: Name (title), Status (checkbox), Priority (select), Description (rich_text),
//   Due Date (date), Application (rich_text).
// Usage: node sync-notion.js [--dry-run] [--tasks-only] [--apps-only]
const { load, save } = require("./lib");

const TOKEN = process.env.NOTION_TOKEN;
const DB = process.env.NOTION_DATABASE_ID;
const TASKS_DB = process.env.NOTION_TASKS_DATABASE_ID;
const dry = process.argv.includes("--dry-run");
const tasksOnly = process.argv.includes("--tasks-only");
const appsOnly = process.argv.includes("--apps-only");
const NOTION_VERSION = "2022-06-28";

if (!dry && !tasksOnly && (!TOKEN || !DB)) { console.error("NOTION_TOKEN and NOTION_DATABASE_ID required for app sync. Use --dry-run to preview."); process.exit(1); }
if (!dry && tasksOnly && (!TOKEN || !TASKS_DB)) { console.error("NOTION_TOKEN and NOTION_TASKS_DATABASE_ID required for task sync."); process.exit(1); }

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

function taskProps(t, apps) {
  const rich = (v) => v ? { rich_text: [{ text: { content: String(v) } }] } : { rich_text: [] };
  const app = t.application_id && apps[t.application_id];
  return {
    Name: { title: [{ text: { content: t.title || "(untitled)" } }] },
    Status: { checkbox: !!t.completed },
    Priority: { select: t.priority ? { name: t.priority } : null },
    Description: rich(t.description),
    "Due Date": t.due_date ? { date: { start: String(t.due_date).slice(0, 10) } } : { date: null },
    Application: rich(app ? `${app.company} — ${app.role}` : ""),
  };
}

(async () => {
  const appsArr = load("applications");
  const appsById = Object.fromEntries(appsArr.map((a) => [a.id, a]));

  // Sync applications
  if (!tasksOnly) {
    let created = 0, updated = 0;
    for (const a of appsArr) {
      if (dry) { console.log(`[dry-run] ${a.notion_page_id ? "PATCH" : "POST"} Notion apps: ${a.company} — ${a.role} (${a.status})`); continue; }
      try {
        if (a.notion_page_id) { await notion(`/v1/pages/${a.notion_page_id}`, "PATCH", { properties: props(a) }); updated++; }
        else { const page = await notion("/v1/pages", "POST", { parent: { database_id: DB }, properties: props(a) }); a.notion_page_id = page.id; created++; }
      } catch (e) { console.error(`Notion error for ${a.company}: ${e.message}`); }
    }
    if (!dry) { save("applications", appsArr); console.error(`Notion apps sync: ${created} created, ${updated} updated.`); }
    else console.error(`[dry-run] ${appsArr.length} application(s) would sync.`);
  }

  // Sync tasks
  if (!appsOnly && TASKS_DB) {
    const tasks = load("tasks");
    let tCreated = 0, tUpdated = 0;
    for (const t of tasks) {
      if (dry) { console.log(`[dry-run] ${t.notion_task_page_id ? "PATCH" : "POST"} Notion tasks: ${t.title}`); continue; }
      try {
        if (t.notion_task_page_id) {
          await notion(`/v1/pages/${t.notion_task_page_id}`, "PATCH", { properties: taskProps(t, appsById) });
          tUpdated++;
        } else {
          const page = await notion("/v1/pages", "POST", { parent: { database_id: TASKS_DB }, properties: taskProps(t, appsById) });
          t.notion_task_page_id = page.id;
          tCreated++;
        }
      } catch (e) { console.error(`Notion task error for "${t.title}": ${e.message}`); }
    }
    if (!dry) { save("tasks", tasks); console.error(`Notion tasks sync: ${tCreated} created, ${tUpdated} updated.`); }
    else if (!tasksOnly) console.error(`[dry-run] ${tasks.length} task(s) would sync.`);
    else console.error(`[dry-run] ${tasks.length} task(s) would sync.`);
  } else if (!appsOnly && !TASKS_DB) {
    console.error("NOTION_TASKS_DATABASE_ID not set — skipping task sync. Set it to enable.");
  }
})();
