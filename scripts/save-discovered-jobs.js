#!/usr/bin/env node
// Save discovered job leads to applications.json, deduplicating by URL.
// Usage: node save-discovered-jobs.js '<json-array>' [--dry-run]
// Or:    echo '<json>' | node save-discovered-jobs.js --stdin [--dry-run]
const fs = require("fs");
const { load, save, genId, nowISO } = require("./lib");

const dry = process.argv.includes("--dry-run");
const stdin = process.argv.includes("--stdin");

let raw = "";
if (stdin) {
  try { raw = fs.readFileSync(0, "utf8"); } catch (_) {}
} else {
  const jsonIdx = process.argv.findIndex((a, i) => i >= 2 && !a.startsWith("--"));
  raw = jsonIdx !== -1 ? process.argv[jsonIdx] : "[]";
}

let leads = [];
try { leads = JSON.parse(raw); } catch (e) { console.error(`Invalid JSON: ${e.message}`); process.exit(1); }

if (!Array.isArray(leads) || leads.length === 0) {
  console.error("No leads to save.");
  process.exit(0);
}

const existing = load("applications");
const existingUrls = new Set(existing.map(a => a.job_url).filter(Boolean));

const toAdd = [];
const skipped = [];

for (const lead of leads) {
  if (!lead.company || !lead.role) { skipped.push(`missing company/role: ${JSON.stringify(lead)}`); continue; }
  if (lead.url && existingUrls.has(lead.url)) { skipped.push(`duplicate URL: ${lead.url}`); continue; }

  const app = {
    id: genId("app"),
    company: lead.company,
    role: lead.role,
    job_url: lead.url || "",
    status: "Saved",
    priority: "Medium",
    currency: "ILS",
    location: lead.location || "",
    source: lead.source || "Discovery",
    match_score: lead.relevance_score || null,
    scanner_notes: lead.relevance_reason || `Discovered via ${lead.source || "job board"}`,
    created_date: nowISO(),
    updated_date: nowISO(),
  };
  // Store salary hint as notes if present
  if (lead.salary_hint) app.notes_preview = lead.salary_hint;

  toAdd.push(app);
  if (lead.url) existingUrls.add(lead.url);
}

if (dry) {
  console.log(JSON.stringify({ would_add: toAdd.length, skipped: skipped.length, jobs: toAdd }, null, 2));
  console.error(`[dry-run] Would add ${toAdd.length} job(s), skip ${skipped.length} duplicate(s).`);
  process.exit(0);
}

save("applications", existing.concat(toAdd));
console.error(`Saved ${toAdd.length} discovered job(s). Skipped ${skipped.length} duplicate(s).`);
if (skipped.length) console.error("Skipped:\n" + skipped.map(s => "  • " + s).join("\n"));
console.log(JSON.stringify(toAdd.map(a => ({ id: a.id, company: a.company, role: a.role })), null, 2));
