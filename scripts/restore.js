#!/usr/bin/env node
// Restore headhunter data from a timestamped backup file.
// Usage: node restore.js <backup.json> [--confirm]
const fs = require("fs");
const { DATA_DIR, save } = require("./lib");

const file = process.argv[2];
if (!file) { console.error("Usage: restore.js <backup.json> [--confirm]"); process.exit(1); }
if (!fs.existsSync(file)) { console.error(`File not found: ${file}`); process.exit(1); }

if (!process.argv.includes("--confirm")) {
  console.error(`This will overwrite all data in ${DATA_DIR}.`);
  console.error(`Re-run with --confirm to proceed: node restore.js ${file} --confirm`);
  process.exit(1);
}

const snapshot = JSON.parse(fs.readFileSync(file, "utf8"));
const ENTITIES = ["applications", "interviews", "tasks", "contacts", "notes", "events"];

let restored = 0;
for (const entity of ENTITIES) {
  if (!Array.isArray(snapshot[entity])) { console.error(`Skipping ${entity}: not an array in backup`); continue; }
  save(entity, snapshot[entity]);
  console.error(`Restored ${snapshot[entity].length} ${entity}`);
  restored++;
}

console.error(`Restore complete (${restored} entities) from ${file}`);
