#!/usr/bin/env node
// PostToolUse(Write) validator: checks data/*.json parse and required fields.
// Reads the hook payload from stdin; only acts when a data/*.json file was written.
// Exit 0 always (advisory) but print warnings to stderr.
const fs = require("fs");
const { load } = require("./lib");

let input = "";
try { input = fs.readFileSync(0, "utf8"); } catch (_) {}

let payload = {};
try { payload = JSON.parse(input || "{}"); } catch (_) {}

const filePath =
  (payload.tool_input && (payload.tool_input.file_path || payload.tool_input.path)) || "";

// Only validate when a jobtrack data file was touched.
if (!/data[\/\\][a-z]+\.json$/i.test(filePath)) process.exit(0);

const REQUIRED = {
  applications: ["company", "role"],
  interviews: ["application_id", "round_type"],
  tasks: ["title"],
  contacts: ["application_id", "name"],
  notes: ["application_id", "content"],
};

const entity = (filePath.match(/([a-z]+)\.json$/i) || [])[1];
if (!entity || !REQUIRED[entity]) process.exit(0);

try {
  const records = load(entity);
  const problems = [];
  if (!Array.isArray(records)) problems.push(`${entity}.json is not an array`);
  else {
    records.forEach((r, i) => {
      for (const f of REQUIRED[entity]) {
        if (r[f] === undefined || r[f] === null || r[f] === "")
          problems.push(`${entity}[${i}] (${r.id || "no-id"}) missing required field: ${f}`);
      }
    });
  }
  if (problems.length) {
    console.error("JobTrack data validation warnings:\n  - " + problems.join("\n  - "));
  }
} catch (e) {
  console.error(`JobTrack data validation: ${e.message}`);
}
process.exit(0);
