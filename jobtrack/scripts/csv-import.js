#!/usr/bin/env node
// Import applications from CSV using column alias mapping.
// Usage: node csv-import.js <input.csv> [--write]
// Without --write, prints normalized JSON (dry run). With --write, appends to data/applications.json.
const fs = require("fs");
const { parseCsv, load, save, nowISO, genId } = require("./lib");

const FIELD_MAP = {
  company: ["company", "company name", "employer", "organization"],
  role: ["role", "position", "title", "job title", "job role"],
  status: ["status", "stage"],
  priority: ["priority"],
  applied_date: ["applied date", "applied_date", "date applied", "date"],
  source: ["source", "channel", "platform"],
  location: ["location", "city"],
  remote_type: ["remote", "remote type", "work type"],
  salary_min: ["salary min", "salary_min", "min salary", "pay min"],
  salary_max: ["salary max", "salary_max", "max salary", "pay max"],
  job_url: ["url", "job url", "link", "job link"],
};

const file = process.argv[2];
const write = process.argv.includes("--write");
if (!file) { console.error("Usage: csv-import.js <input.csv> [--write]"); process.exit(1); }

const rows = parseCsv(fs.readFileSync(file, "utf8"));
if (rows.length < 2) { console.error("CSV has no data rows"); process.exit(1); }

const header = rows[0].map((h) => h.trim().toLowerCase());

// Build header index -> canonical field
const colToField = {};
for (const [field, aliases] of Object.entries(FIELD_MAP)) {
  const idx = header.findIndex((h) => aliases.includes(h));
  if (idx !== -1) colToField[idx] = field;
}

const records = rows.slice(1).map((row) => {
  const rec = {
    id: genId("app"), status: "Saved", priority: "Medium", currency: "USD",
    created_date: nowISO(), updated_date: nowISO(),
  };
  row.forEach((val, i) => {
    const field = colToField[i];
    if (!field || val === "") return;
    if (field === "salary_min" || field === "salary_max") {
      const n = Number(String(val).replace(/[^0-9.]/g, ""));
      if (!Number.isNaN(n)) rec[field] = n;
    } else {
      rec[field] = val.trim();
    }
  });
  return rec;
}).filter((r) => r.company && r.role);

if (write) {
  const existing = load("applications");
  save("applications", existing.concat(records));
  console.error(`Imported ${records.length} applications into data/applications.json.`);
} else {
  console.log(JSON.stringify(records, null, 2));
  console.error(`(dry run) Parsed ${records.length} applications. Re-run with --write to persist.`);
}
