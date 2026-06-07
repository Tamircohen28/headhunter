#!/usr/bin/env node
// PreToolUse(Write|Edit) guard: blocks direct edits to data/*.json.
// Enforces the write-through-CRUD rule — all data writes must go through crud.js.
// Reads the hook payload from stdin. Exits 1 (blocking) if a data/*.json file is targeted.
const fs = require("fs");
const path = require("path");
const { DATA_DIR } = require("./lib");

let input = "";
try { input = fs.readFileSync(0, "utf8"); } catch (_) {}

let payload = {};
try { payload = JSON.parse(input || "{}"); } catch (_) {}

const filePath =
  (payload.tool_input && (payload.tool_input.file_path || payload.tool_input.path)) || "";

if (!filePath) process.exit(0);

// Check if the target file is inside DATA_DIR and ends in .json
const absDataDir = path.resolve(DATA_DIR);
const absFilePath = path.resolve(filePath);
if (!absFilePath.startsWith(absDataDir + path.sep) || !absFilePath.endsWith(".json")) process.exit(0);

// Allow events.json writes only from crud.js (it appends directly via save())
// and candidate-profile.json writes from candidate-profile.js.
// Block everything else — use `node scripts/crud.js` instead.
const allowed = ["events.json", "candidate-profile.json"];
const base = filePath.split(/[/\\]/).pop();
if (allowed.includes(base)) process.exit(0);

console.error(
  `\n⛔  Direct write to ${filePath} blocked.\n` +
  `   HeadHunter data files must be written through the CRUD CLI:\n` +
  `     node scripts/crud.js add|update|move|delete <entity> ...\n` +
  `   This ensures IDs, timestamps, and the event log stay consistent.\n` +
  `   See AGENTS.md for the full command reference.\n`
);
process.exit(1);
