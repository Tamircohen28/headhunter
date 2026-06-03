#!/usr/bin/env node
// Export applications to CSV or JSON.
// Usage: node export-applications.js --format csv|json [--out FILE]
const fs = require("fs");
const { load } = require("./lib");

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i !== -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

const format = (arg("format", "csv") || "csv").toLowerCase();
const out = arg("out", null);

const COLUMNS = [
  "id", "company", "role", "status", "priority", "applied_date", "source",
  "location", "remote_type", "salary_min", "salary_max", "currency", "job_url",
  "created_date", "updated_date",
];

const apps = load("applications");
let output;

if (format === "json") {
  output = JSON.stringify(apps, null, 2) + "\n";
} else if (format === "csv") {
  const esc = (v) => {
    if (v === null || v === undefined) v = "";
    v = String(v);
    return /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
  };
  output =
    COLUMNS.join(",") + "\n" +
    apps.map((a) => COLUMNS.map((c) => esc(a[c])).join(",")).join("\n") + "\n";
} else {
  console.error(`Unknown format: ${format} (use csv or json)`);
  process.exit(1);
}

if (out) {
  fs.writeFileSync(out, output);
  console.error(`Exported ${apps.length} applications to ${out} (${format}).`);
} else {
  process.stdout.write(output);
}
