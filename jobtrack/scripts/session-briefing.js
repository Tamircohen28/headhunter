#!/usr/bin/env node
// SessionStart briefing: counts by stage, interviews in next 48h, overdue tasks.
// Prints a short summary (<15 lines). Safe no-op if there's no data.
const { load } = require("./lib");

try {
  const apps = load("applications");
  if (!apps.length) {
    console.log("JobTrack: no applications yet. Run `crud.js seed` for demo data or `/jobtrack:add-application`.");
    process.exit(0);
  }

  const PIPELINE = ["Saved", "Applied", "Phone Screen", "Technical", "Onsite", "Offer", "Accepted"];
  const counts = {};
  for (const a of apps) counts[a.status] = (counts[a.status] || 0) + 1;
  const stageLine = PIPELINE.filter((s) => counts[s]).map((s) => `${s}:${counts[s]}`).join("  ");

  const now = Date.now();
  const in48h = now + 48 * 3600 * 1000;
  const interviews = load("interviews").filter(
    (i) => i.status === "Scheduled" && i.scheduled_at &&
      new Date(i.scheduled_at).getTime() >= now &&
      new Date(i.scheduled_at).getTime() <= in48h
  );
  const appById = Object.fromEntries(apps.map((a) => [a.id, a]));

  const overdue = load("tasks").filter(
    (t) => !t.completed && t.due_date && new Date(t.due_date).getTime() < now
  );

  console.log("=== JobTrack briefing ===");
  console.log(`Pipeline: ${stageLine || "(none active)"}`);
  console.log(`Total applications: ${apps.length}`);
  if (interviews.length) {
    console.log(`Interviews in next 48h: ${interviews.length}`);
    for (const i of interviews) {
      const a = appById[i.application_id];
      console.log(`  • ${i.round_type} @ ${a ? a.company : "?"} — ${i.scheduled_at}`);
    }
  } else {
    console.log("Interviews in next 48h: none");
  }
  console.log(`Overdue tasks: ${overdue.length}`);
  for (const t of overdue.slice(0, 5)) console.log(`  • ${t.title} (due ${t.due_date})`);
} catch (e) {
  // Never block session start on a briefing error.
  console.log(`JobTrack briefing unavailable: ${e.message}`);
}
