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
        "HeadHunter: no applications yet. Run `crud.js seed` for demo data, " +
        "`/headhunter:add-application` to add one, or `/headhunter:research <url>` to research a posting.",
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

  const ACTIVE_STAGES = ["Applied", "Phone Screen", "Technical", "Onsite", "Offer"];
  const staleThreshold = 7;
  const staleCutoff = now - staleThreshold * 86400000;
  const stale = apps.filter(
    (a) => ACTIVE_STAGES.includes(a.status) && new Date(a.updated_date).getTime() < staleCutoff
  );

  const lines = ["=== HeadHunter briefing ==="];
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
  if (stale.length) {
    lines.push(`Stale applications (${staleThreshold}+ days without update): ${stale.length}`);
    for (const a of stale.slice(0, 3)) {
      const days = Math.floor((now - new Date(a.updated_date).getTime()) / 86400000);
      lines.push(`  • ${a.company} – ${a.role} (${a.status}, ${days}d)`);
    }
    if (stale.length > 3) lines.push(`  … and ${stale.length - 3} more`);
  }

  const active = apps.filter((a) => PIPELINE.indexOf(a.status) > 0 && PIPELINE.indexOf(a.status) < 6).length;
  emit({
    context: lines.join("\n"),
    title: `HeadHunter · ${apps.length} apps · ${active} active${overdue.length ? ` · ${overdue.length} overdue` : ""}${stale.length ? ` · ${stale.length} stale` : ""}`,
  });
} catch (e) {
  // Never block session start on a briefing error.
  emit({ context: `HeadHunter briefing unavailable: ${e.message}` });
}
