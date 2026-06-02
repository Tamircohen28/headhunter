#!/usr/bin/env node
// Sync jobtrack tasks to Todoist (REST v2). Idempotent via todoist_task_id.
// Env: TODOIST_API_TOKEN
// Usage: node sync-todoist.js [--dry-run] [--all]
const { load, save } = require("./lib");

const TOKEN = process.env.TODOIST_API_TOKEN;
const dry = process.argv.includes("--dry-run");
const all = process.argv.includes("--all");
const PRIORITY = { High: 4, Medium: 3, Low: 2 };

if (!TOKEN && !dry) { console.error("TODOIST_API_TOKEN not set. Use --dry-run to preview."); process.exit(1); }

const tasks = load("tasks");
const apps = Object.fromEntries(load("applications").map((a) => [a.id, a]));
const pending = tasks.filter((t) => !t.completed && (all || !t.todoist_task_id));

if (!pending.length) { console.error("No tasks to sync."); process.exit(0); }

(async () => {
  let synced = 0;
  for (const t of pending) {
    const company = t.application_id && apps[t.application_id] ? apps[t.application_id].company : null;
    const content = company ? `[${company}] ${t.title}` : t.title;
    const payload = {
      content,
      priority: PRIORITY[t.priority] || 3,
      ...(t.due_date ? { due_date: String(t.due_date).slice(0, 10) } : {}),
      ...(t.description ? { description: t.description } : {}),
    };
    if (dry) { console.log(`[dry-run] POST Todoist: ${JSON.stringify(payload)}`); continue; }
    const res = await fetch("https://api.todoist.com/rest/v2/tasks", {
      method: "POST",
      headers: { Authorization: `Bearer ${TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) { console.error(`Todoist error for "${content}": ${res.status} ${await res.text()}`); continue; }
    const created = await res.json();
    t.todoist_task_id = created.id;
    synced++;
  }
  if (!dry) { save("tasks", tasks); console.error(`Synced ${synced} task(s) to Todoist.`); }
  else console.error(`[dry-run] ${pending.length} task(s) would sync.`);
})();
