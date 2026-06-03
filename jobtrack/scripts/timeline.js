#!/usr/bin/env node
// Chronological timeline for one application (section 5.4 Timeline tab):
// merges logged events, interviews, and notes into one ordered stream.
// Usage: node timeline.js <appId> [--json]
const { load } = require("./lib");

const appId = process.argv[2];
if (!appId || appId.startsWith("--")) { console.error("Usage: timeline.js <appId> [--json]"); process.exit(1); }

const app = load("applications").find((a) => a.id === appId);
if (!app) { console.error(`No application ${appId}`); process.exit(1); }

const events = load("events").filter((e) => e.application_id === appId)
  .map((e) => ({ ts: e.ts, kind: e.type, text: e.summary }));

const interviews = load("interviews").filter((i) => i.application_id === appId && i.scheduled_at)
  .map((i) => ({ ts: i.scheduled_at, kind: "interview", text: `${i.round_type} round — ${i.status}${i.outcome ? ` (${i.outcome})` : ""}` }));

const notes = load("notes").filter((n) => n.application_id === appId)
  .map((n) => ({ ts: n.created_date || app.created_date, kind: "note", text: `${n.note_type || "Note"}: ${String(n.content).slice(0, 80)}` }));

const stream = [...events, ...interviews, ...notes]
  .filter((x) => x.ts)
  .sort((a, b) => new Date(a.ts) - new Date(b.ts));

if (process.argv.includes("--json")) { console.log(JSON.stringify({ application: { id: app.id, company: app.company, role: app.role }, stream }, null, 2)); process.exit(0); }

const ICON = { application_created: "➕", status_change: "↗", interview_added: "📅", interview: "🎤", task_added: "✓", task_completed: "✅", note_added: "📝", note: "📝" };
console.log(`🧭 Timeline — ${app.company} — ${app.role}\n`);
if (!stream.length) { console.log("(no events yet)"); process.exit(0); }
for (const e of stream) console.log(`  ${String(e.ts).slice(0, 16).replace("T", " ")}  ${ICON[e.kind] || "•"} ${e.text}`);
