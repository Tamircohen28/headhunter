#!/usr/bin/env node
// Snapshot all jobtrack data to a timestamped JSON file.
// Usage: node backup.js [--out <dir>]
const fs = require("fs");
const path = require("path");
const { DATA_DIR, load } = require("./lib");

const outDir = (() => {
  const idx = process.argv.indexOf("--out");
  return idx !== -1 ? process.argv[idx + 1] : path.join(DATA_DIR, "backups");
})();

const ENTITIES = ["applications", "interviews", "tasks", "contacts", "notes", "events"];

const snapshot = {};
for (const e of ENTITIES) {
  try { snapshot[e] = load(e); } catch (_) { snapshot[e] = []; }
}

if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const file = path.join(outDir, `jobtrack-backup-${ts}.json`);
fs.writeFileSync(file, JSON.stringify(snapshot, null, 2) + "\n");

const total = Object.values(snapshot).reduce((s, a) => s + a.length, 0);
console.error(`Backup written: ${file} (${total} records across ${ENTITIES.length} entities)`);
console.log(file);
