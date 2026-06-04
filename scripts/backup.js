#!/usr/bin/env node
// Snapshot all headhunter data to a timestamped JSON file.
// Skips write when content matches the latest backup; prunes to maxKeep files.
// Usage: node backup.js [--out <dir>] [--max-keep N] [--prune-duplicates]
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { DATA_DIR, load } = require("./lib");

const outDir = (() => {
  const idx = process.argv.indexOf("--out");
  return idx !== -1 ? process.argv[idx + 1] : path.join(DATA_DIR, "backups");
})();

const maxKeep = (() => {
  const idx = process.argv.indexOf("--max-keep");
  return idx !== -1 ? Math.max(1, parseInt(process.argv[idx + 1], 10) || 10) : 10;
})();

const pruneDuplicates = process.argv.includes("--prune-duplicates");

const ENTITIES = ["applications", "interviews", "tasks", "contacts", "notes", "events"];

const snapshot = {};
for (const e of ENTITIES) {
  try { snapshot[e] = load(e); } catch (_) { snapshot[e] = []; }
}

const content = JSON.stringify(snapshot, null, 2) + "\n";
const hash = crypto.createHash("sha256").update(content).digest("hex");

if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

function listBackups() {
  return fs.readdirSync(outDir)
    .filter((f) => f.startsWith("headhunter-backup-") && f.endsWith(".json"))
    .map((f) => {
      const p = path.join(outDir, f);
      return { f, p, mtime: fs.statSync(p).mtimeMs, hash: fileHash(p) };
    })
    .sort((a, b) => b.mtime - a.mtime);
}

function fileHash(p) {
  return crypto.createHash("sha256").update(fs.readFileSync(p, "utf8")).digest("hex");
}

function pruneDuplicatesNow(files) {
  const byHash = new Map();
  for (const file of files) {
    if (!byHash.has(file.hash)) byHash.set(file.hash, []);
    byHash.get(file.hash).push(file);
  }
  let removed = 0;
  for (const [, group] of byHash) {
    group.sort((a, b) => b.mtime - a.mtime);
    for (let i = 1; i < group.length; i++) {
      fs.unlinkSync(group[i].p);
      removed++;
    }
  }
  return removed;
}

function pruneToMaxKeep(files) {
  let removed = 0;
  for (let i = maxKeep; i < files.length; i++) {
    fs.unlinkSync(files[i].p);
    removed++;
  }
  return removed;
}

let files = listBackups();

if (pruneDuplicates) {
  const n = pruneDuplicatesNow(files);
  if (n) console.error(`Pruned ${n} duplicate backup(s).`);
  files = listBackups();
}

const latest = files[0];
if (latest && latest.hash === hash) {
  console.error(`Backup skipped (identical to latest): ${latest.f}`);
  console.log(latest.p);
  pruneToMaxKeep(files);
  process.exit(0);
}

const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const file = path.join(outDir, `headhunter-backup-${ts}.json`);
fs.writeFileSync(file, content);

files = listBackups();
const pruned = pruneToMaxKeep(files);

const total = Object.values(snapshot).reduce((s, a) => s + a.length, 0);
console.error(`Backup written: ${file} (${total} records across ${ENTITIES.length} entities)`);
if (pruned) console.error(`Pruned ${pruned} old backup(s); keeping ${maxKeep} most recent.`);
console.log(file);
