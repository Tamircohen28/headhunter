#!/usr/bin/env node
// Compute the JobTrack dashboard metrics deterministically (section 5.1).
// Usage: node dashboard.js [--json]
const { load } = require("./lib");
const { PIPELINE, TERMINAL, ACTIVE_STAGES, STATUS_EMOJI } = require("./enums");

const apps = load("applications");
const interviews = load("interviews");
const tasks = load("tasks");
const now = Date.now();
const DAY = 86400000;

const byStage = {};
for (const s of [...PIPELINE, ...TERMINAL]) byStage[s] = 0;
for (const a of apps) byStage[a.status] = (byStage[a.status] || 0) + 1;

const active = apps.filter((a) => ACTIVE_STAGES.includes(a.status)).length;
const offers = apps.filter((a) => a.status === "Offer" || a.status === "Accepted").length;
const applied = apps.filter((a) => a.status !== "Saved").length;

// Response rate: applications that progressed beyond Applied OR got rejected (any reply).
const responded = apps.filter((a) =>
  ["Phone Screen", "Technical", "Onsite", "Offer", "Accepted", "Rejected"].includes(a.status)).length;
const responseRate = applied ? Math.round((responded / applied) * 100) : 0;

const ghosted = apps.filter((a) => a.status === "Ghosted").length;
const ghostedRate = applied ? Math.round((ghosted / applied) * 100) : 0;

// Interview conversion: apps that reached an interview stage / applied.
const reachedInterview = apps.filter((a) =>
  ["Phone Screen", "Technical", "Onsite", "Offer", "Accepted"].includes(a.status)).length;
const interviewConversion = applied ? Math.round((reachedInterview / applied) * 100) : 0;

// Avg response time (days): applied_date -> updated_date for responded apps.
const responseTimes = apps
  .filter((a) => a.applied_date && responded && a.status !== "Applied" && a.status !== "Saved")
  .map((a) => (new Date(a.updated_date) - new Date(a.applied_date)) / DAY)
  .filter((d) => d >= 0);
const avgResponseDays = responseTimes.length
  ? Math.round(responseTimes.reduce((x, y) => x + y, 0) / responseTimes.length) : null;

// Top source.
const sources = {};
for (const a of apps) if (a.source) sources[a.source] = (sources[a.source] || 0) + 1;
const topSource = Object.entries(sources).sort((a, b) => b[1] - a[1])[0]?.[0] || null;

const appById = Object.fromEntries(apps.map((a) => [a.id, a]));
const upcoming = interviews
  .filter((i) => i.status === "Scheduled" && i.scheduled_at &&
    new Date(i.scheduled_at).getTime() >= now &&
    new Date(i.scheduled_at).getTime() <= now + 14 * DAY)
  .sort((a, b) => new Date(a.scheduled_at) - new Date(b.scheduled_at));

const overdue = tasks.filter((t) => !t.completed && t.due_date && new Date(t.due_date).getTime() < now);
const recent = [...apps].sort((a, b) => new Date(b.updated_date) - new Date(a.updated_date)).slice(0, 5);

const metrics = {
  total: apps.length, active, offers, applied,
  responseRatePct: responseRate, avgResponseDays, ghostedRatePct: ghostedRate,
  interviewConversionPct: interviewConversion, topSource,
  upcomingInterviews14d: upcoming.length, overdueTasks: overdue.length, byStage,
};

if (process.argv.includes("--json")) { console.log(JSON.stringify({ metrics, upcoming, overdue, recent }, null, 2)); process.exit(0); }

const p = (n) => String(n).padStart(3);
console.log("📊 JobTrack Dashboard\n");
console.log(`Total: ${metrics.total}   Active: ${active}   Offers: ${offers}`);
console.log(`Response rate: ${responseRate}%   Interview conversion: ${interviewConversion}%   Ghosted: ${ghostedRate}%`);
console.log(`Avg response time: ${avgResponseDays ?? "—"} days   Top source: ${topSource ?? "—"}\n`);
console.log("Pipeline:");
for (const s of PIPELINE) console.log(`  ${STATUS_EMOJI[s]} ${s.padEnd(13)} ${p(byStage[s])} ${"█".repeat(byStage[s])}`);
const term = TERMINAL.filter((s) => byStage[s]).map((s) => `${STATUS_EMOJI[s]} ${s}:${byStage[s]}`).join("  ");
if (term) console.log(`  ${term}`);
console.log(`\nUpcoming interviews (14d): ${upcoming.length}`);
for (const i of upcoming) console.log(`  • ${new Date(i.scheduled_at).toISOString().slice(0, 16).replace("T", " ")}  ${i.round_type} @ ${appById[i.application_id]?.company ?? "?"}`);
console.log(`\nOverdue tasks: ${overdue.length}`);
for (const t of overdue) console.log(`  • ${t.title}${t.application_id ? ` (${appById[t.application_id]?.company ?? ""})` : ""} — due ${String(t.due_date).slice(0, 10)}`);
console.log("\nRecently updated:");
for (const a of recent) console.log(`  • ${STATUS_EMOJI[a.status]} ${a.company} — ${a.role} (${a.status})`);
