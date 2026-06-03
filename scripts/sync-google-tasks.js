#!/usr/bin/env node
// Sync headhunter tasks to Google Tasks (REST v1). Idempotent via google_task_id.
// Env: GOOGLE_OAUTH_TOKEN (Bearer), GOOGLE_TASKS_LIST_ID (default '@default')
// Usage: node sync-google-tasks.js [--dry-run] [--all]
const { load, save } = require("./lib");

const TOKEN = process.env.GOOGLE_OAUTH_TOKEN;
const LIST_ID = process.env.GOOGLE_TASKS_LIST_ID || "@default";
const dry = process.argv.includes("--dry-run");
const all = process.argv.includes("--all");

if (!TOKEN && !dry) { console.error("GOOGLE_OAUTH_TOKEN not set. Use --dry-run to preview."); process.exit(1); }

const tasks = load("tasks");
const apps = Object.fromEntries(load("applications").map((a) => [a.id, a]));
const pending = tasks.filter((t) => !t.completed && (all || !t.google_task_id));

if (!pending.length) { console.error("No tasks to sync."); process.exit(0); }

function buildPayload(t) {
  const app = t.application_id && apps[t.application_id];
  const title = app ? `[${app.company}] ${t.title}` : t.title;
  return {
    title,
    notes: t.description || undefined,
    status: "needsAction",
    ...(t.due_date ? { due: new Date(t.due_date).toISOString().slice(0, 10) + "T00:00:00.000Z" } : {}),
  };
}

async function gtasks(method, pathSuffix, body) {
  const url = `https://tasks.googleapis.com/tasks/v1/lists/${encodeURIComponent(LIST_ID)}/tasks${pathSuffix}`;
  const res = await fetch(url, {
    method,
    headers: { Authorization: `Bearer ${TOKEN}`, "Content-Type": "application/json" },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

(async () => {
  let created = 0, updated = 0;
  for (const t of pending) {
    const payload = buildPayload(t);

    if (dry) {
      const action = t.google_task_id ? "PATCH" : "POST";
      console.log(`[dry-run] ${action} Google Tasks: ${payload.title}`);
      continue;
    }

    try {
      if (t.google_task_id) {
        await gtasks("PATCH", `/${t.google_task_id}`, payload);
        updated++;
      } else {
        const result = await gtasks("POST", "", payload);
        t.google_task_id = result.id;
        created++;
      }
    } catch (e) {
      console.error(`Google Tasks error for "${t.title}": ${e.message}`);
    }
  }

  if (!dry) {
    save("tasks", tasks);
    console.error(`Google Tasks sync: ${created} created, ${updated} updated.`);
  } else {
    console.error(`[dry-run] ${pending.length} task(s) would sync.`);
  }
})();
