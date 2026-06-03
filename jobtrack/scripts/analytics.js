#!/usr/bin/env node
// Pipeline funnel analytics: conversion rates, avg time per stage, top sources, offer rate.
// Usage: node analytics.js [--json]
const { load } = require("./lib");

const json = process.argv.includes("--json");

const apps = load("applications");
const interviews = load("interviews");

if (!apps.length) { console.error("No applications yet. Add some with /jobtrack:add-application."); process.exit(0); }

const PIPELINE = ["Saved", "Applied", "Phone Screen", "Technical", "Onsite", "Offer", "Accepted"];
const TERMINAL = ["Rejected", "Declined", "Ghosted"];
const ACTIVE = ["Applied", "Phone Screen", "Technical", "Onsite", "Offer"];

// ── Funnel counts ────────────────────────────────────────────────────────────
const counts = {};
for (const s of [...PIPELINE, ...TERMINAL]) counts[s] = 0;
for (const a of apps) counts[a.status] = (counts[a.status] || 0) + 1;

const applied = apps.filter(a => PIPELINE.indexOf(a.status) >= 1 || TERMINAL.includes(a.status)).length;
const screened = apps.filter(a => PIPELINE.indexOf(a.status) >= 2 || TERMINAL.includes(a.status)).length;
const technical = apps.filter(a => PIPELINE.indexOf(a.status) >= 3 || TERMINAL.includes(a.status)).length;
const onsite = apps.filter(a => PIPELINE.indexOf(a.status) >= 4 || TERMINAL.includes(a.status)).length;
const offers = apps.filter(a => PIPELINE.indexOf(a.status) >= 5).length;
const accepted = counts["Accepted"] || 0;

function pct(num, den) { return den > 0 ? `${Math.round(num / den * 100)}%` : "—"; }

// ── Avg days per stage ───────────────────────────────────────────────────────
const daysBetween = (d1, d2) => Math.round((new Date(d2) - new Date(d1)) / 86400000);

const stageTime = {};
for (const a of apps) {
  if (!a.applied_date || !a.updated_date) continue;
  const stageIdx = PIPELINE.indexOf(a.status);
  if (stageIdx < 1) continue;
  const total = daysBetween(a.applied_date, a.updated_date);
  if (total > 0 && total < 365) {
    if (!stageTime[a.status]) stageTime[a.status] = [];
    stageTime[a.status].push(total);
  }
}

// ── Source analysis ──────────────────────────────────────────────────────────
const sourceMap = {};
for (const a of apps) {
  const src = a.source || "Unknown";
  if (!sourceMap[src]) sourceMap[src] = { total: 0, reached_screen: 0, offers: 0 };
  sourceMap[src].total++;
  if (PIPELINE.indexOf(a.status) >= 2) sourceMap[src].reached_screen++;
  if (PIPELINE.indexOf(a.status) >= 5) sourceMap[src].offers++;
}

// ── Scanner score averages (if any) ─────────────────────────────────────────
const scored = apps.filter(a => a.match_score != null);
const avgMatch = scored.length ? Math.round(scored.reduce((s, a) => s + a.match_score, 0) / scored.length) : null;
const avgSuccess = scored.length ? Math.round(scored.filter(a => a.success_score != null).reduce((s, a) => s + (a.success_score || 0), 0) / scored.length) : null;

// ── Interview stats ──────────────────────────────────────────────────────────
const scheduled = interviews.filter(i => i.status === "Scheduled").length;
const completed = interviews.filter(i => i.status === "Completed").length;
const passedRounds = interviews.filter(i => i.outcome === "Passed").length;
const roundConversion = completed > 0 ? pct(passedRounds, completed) : "—";

// ── Ghosted / response rate ──────────────────────────────────────────────────
const ghosted = counts["Ghosted"] || 0;
const responseRate = applied > 0 ? pct(screened, applied) : "—";
const offerRate = applied > 0 ? pct(offers, applied) : "—";
const ghostRate = applied > 0 ? pct(ghosted, applied) : "—";

// ── Output ───────────────────────────────────────────────────────────────────
if (json) {
  console.log(JSON.stringify({
    totals: { total: apps.length, applied, screened, technical, onsite, offers, accepted },
    rates: { response_rate: responseRate, offer_rate: offerRate, ghost_rate: ghostRate, round_pass_rate: roundConversion },
    scanner: { applications_scored: scored.length, avg_match_score: avgMatch, avg_success_score: avgSuccess },
    sources: sourceMap,
    counts,
  }, null, 2));
  process.exit(0);
}

// Human-readable output
const bar = (n, max, width = 20) => {
  const filled = max > 0 ? Math.round(n / max * width) : 0;
  return "█".repeat(filled) + "░".repeat(width - filled);
};

const total = apps.length;
console.log("\n=== JobTrack Pipeline Analytics ===\n");

console.log("Funnel:");
console.log(`  Saved          ${String(counts.Saved || 0).padStart(3)}`);
console.log(`  Applied        ${String(applied).padStart(3)}  ${bar(applied, total)}  ${pct(applied, total)} of total`);
console.log(`  Phone Screen   ${String(screened).padStart(3)}  ${bar(screened, applied)}  ${pct(screened, applied)} of applied`);
console.log(`  Technical      ${String(technical).padStart(3)}  ${bar(technical, screened)}  ${pct(technical, screened)} of screened`);
console.log(`  Onsite         ${String(onsite).padStart(3)}  ${bar(onsite, technical)}  ${pct(onsite, technical)} of technical`);
console.log(`  Offer          ${String(offers).padStart(3)}  ${bar(offers, onsite)}  ${pct(offers, onsite)} of onsite`);
console.log(`  Accepted       ${String(accepted).padStart(3)}`);
console.log(`  Rejected       ${String(counts.Rejected || 0).padStart(3)}`);
console.log(`  Ghosted        ${String(ghosted).padStart(3)}`);

console.log("\nKey rates:");
console.log(`  Response rate (applied → screen):  ${responseRate}`);
console.log(`  Offer rate   (applied → offer):    ${offerRate}`);
console.log(`  Ghost rate   (applied → ghosted):  ${ghostRate}`);
console.log(`  Round pass   (completed → passed): ${roundConversion}`);

if (scored.length > 0) {
  console.log("\nScanner scores (applied applications):");
  console.log(`  Avg match score:   ${avgMatch}/100`);
  console.log(`  Avg success score: ${avgSuccess}/100`);
  console.log(`  (${scored.length}/${apps.length} applications scored)`);
}

if (Object.keys(sourceMap).length > 1) {
  console.log("\nTop sources by screen rate:");
  const sorted = Object.entries(sourceMap).sort((a, b) =>
    (b[1].reached_screen / b[1].total) - (a[1].reached_screen / a[1].total)
  );
  for (const [src, d] of sorted.slice(0, 5)) {
    console.log(`  ${src.padEnd(20)} ${d.total} apps  ${pct(d.reached_screen, d.total)} screen  ${pct(d.offers, d.total)} offer`);
  }
}

console.log(`\nTotal: ${apps.length} applications  |  ${scheduled} interviews scheduled  |  ${completed} completed\n`);
