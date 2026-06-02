#!/usr/bin/env node
// Render scheduled interviews as a calendar/agenda (section 5.5).
// Usage: node calendar.js [--month YYYY-MM] [--json]
const { load } = require("./lib");

const interviews = load("interviews").filter((i) => i.scheduled_at);
const appById = Object.fromEntries(load("applications").map((a) => [a.id, a]));

function arg(name) { const i = process.argv.indexOf(`--${name}`); return i !== -1 ? process.argv[i + 1] : null; }
const month = arg("month"); // YYYY-MM filter

let items = interviews.map((i) => ({
  when: new Date(i.scheduled_at),
  iso: i.scheduled_at,
  company: appById[i.application_id]?.company ?? "?",
  role: appById[i.application_id]?.role ?? "",
  round_type: i.round_type,
  status: i.status,
  duration: i.duration_minutes,
  interviewer: i.interviewer_name,
  application_id: i.application_id,
})).sort((a, b) => a.when - b.when);

if (month) items = items.filter((x) => x.iso.slice(0, 7) === month);

if (process.argv.includes("--json")) { console.log(JSON.stringify(items, null, 2)); process.exit(0); }

console.log(`🗓  Interview calendar${month ? ` — ${month}` : ""}\n`);
if (!items.length) { console.log("(no scheduled interviews)"); process.exit(0); }

let lastDay = "";
for (const x of items) {
  const day = x.iso.slice(0, 10);
  if (day !== lastDay) { console.log(`\n${day}  (${x.when.toLocaleDateString(undefined, { weekday: "long" })})`); lastDay = day; }
  const time = x.iso.slice(11, 16) || "--:--";
  const flag = x.status === "Scheduled" ? "" : ` [${x.status}]`;
  console.log(`  ${time}  ${x.round_type} @ ${x.company} — ${x.role}${x.duration ? ` (${x.duration}m)` : ""}${x.interviewer ? ` w/ ${x.interviewer}` : ""}${flag}`);
}
