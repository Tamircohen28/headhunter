#!/usr/bin/env node
// SessionStart briefing: counts by stage, interviews in next 48h, overdue tasks.
// Emits structured SessionStart JSON (additionalContext + sessionTitle) per the
// v2.1.152 hook output contract. Safe no-op if there's no data.
const { load } = require("./lib");

function emit({ context, title }) {
  process.stdout.write(
    JSON.stringify({
      reloadSkills: false,
      hookSpecificOutput: {
        hookEventName: "SessionStart",
        additionalContext: context,
        ...(title ? { sessionTitle: title } : {}),
      },
    })
  );
}

try {
  const apps = load("applications");
  if (!apps.length) {
    emit({
      context:
        "JobTrack: no applications yet. Run `crud.js seed` for demo data, " +
        "`/jobtrack:add-application` to add one, or `/jobtrack:research <url>` to research a posting.",
    });
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

  const lines = ["=== JobTrack briefing ==="];
  lines.push(`Pipeline: ${stageLine || "(none active)"}`);
  lines.push(`Total applications: ${apps.length}`);
  if (interviews.length) {
    lines.push(`Interviews in next 48h: ${interviews.length}`);
    for (const i of interviews) {
      const a = appById[i.application_id];
      lines.push(`  • ${i.round_type} @ ${a ? a.company : "?"} — ${i.scheduled_at}`);
    }
  } else {
    lines.push("Interviews in next 48h: none");
  }
  lines.push(`Overdue tasks: ${overdue.length}`);
  for (const t of overdue.slice(0, 5)) lines.push(`  • ${t.title} (due ${t.due_date})`);

  const active = apps.filter((a) => PIPELINE.indexOf(a.status) > 0 && PIPELINE.indexOf(a.status) < 6).length;
  emit({
    context: lines.join("\n"),
    title: `JobTrack · ${apps.length} apps · ${active} active${overdue.length ? ` · ${overdue.length} overdue` : ""}`,
  });
} catch (e) {
  // Never block session start on a briefing error.
  emit({ context: `JobTrack briefing unavailable: ${e.message}` });
}
