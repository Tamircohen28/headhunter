#!/usr/bin/env node
// Sync headhunter tasks to Todoist (REST v2). Idempotent via todoist_task_id.
// --all also re-syncs tasks that already have a todoist_task_id (updates them).
// Todoist REST v2 uses POST /tasks for create and POST /tasks/{id} for update (same verb).
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
  let created = 0, updated = 0;
  for (const t of pending) {
    const company = t.application_id && apps[t.application_id] ? apps[t.application_id].company : null;
    const content = company ? `[${company}] ${t.title}` : t.title;
    const payload = {
      content,
      priority: PRIORITY[t.priority] || 3,
      ...(t.due_date ? { due_date: String(t.due_date).slice(0, 10) } : {}),
      ...(t.description ? { description: t.description } : {}),
    };

    // Todoist REST v2: POST /tasks creates a new task; POST /tasks/{id} updates an existing one.
    const isUpdate = !!t.todoist_task_id;
    const url = isUpdate
      ? `https://api.todoist.com/rest/v2/tasks/${t.todoist_task_id}`
      : "https://api.todoist.com/rest/v2/tasks";

    if (dry) {
      console.log(`[dry-run] ${isUpdate ? "UPDATE" : "CREATE"} Todoist: ${JSON.stringify(payload)}`);
      continue;
    }

    const res = await fetch(url, {
      method: "POST",
      headers: { Authorization: `Bearer ${TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) { console.error(`Todoist error for "${content}": ${res.status} ${await res.text()}`); continue; }

    if (isUpdate) {
      updated++;
    } else {
      const result = await res.json();
      t.todoist_task_id = result.id;
      created++;
    }
  }

  if (!dry) {
    save("tasks", tasks);
    console.error(`Todoist sync: ${created} created, ${updated} updated.`);
  } else {
    console.error(`[dry-run] ${pending.length} task(s) would sync.`);
  }
})();
