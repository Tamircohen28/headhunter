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

// Only validate when a headhunter data file was touched.
if (!/data[\/\\][a-z]+\.json$/i.test(filePath)) process.exit(0);

const REQUIRED = {
  applications: ["company", "role"],
  interviews: ["application_id", "round_type"],
  tasks: ["title"],
  contacts: ["application_id", "name"],
  notes: ["application_id", "content"],
};

const entity = (filePath.match(/([a-z_-]+)\.json$/i) || [])[1];

// Special case: candidate-profile.json is an object, not an array.
if (entity === "candidate-profile") {
  try {
    const profile = JSON.parse(require("fs").readFileSync(filePath, "utf8"));
    if (Array.isArray(profile)) {
      console.error("HeadHunter data validation: candidate-profile.json must be an object, not an array.");
    } else if (typeof profile !== "object" || profile === null) {
      console.error("HeadHunter data validation: candidate-profile.json is not a valid JSON object.");
    } else {
      const knownKeys = ["personal", "experience", "preferences", "salary", "cv", "availability"];
      const found = knownKeys.filter(k => k in profile);
      if (found.length === 0) {
        console.error("HeadHunter data validation: candidate-profile.json has no recognized top-level keys (expected: personal, experience, preferences, salary, cv, availability).");
      }
    }
  } catch (e) {
    console.error(`HeadHunter data validation: ${e.message}`);
  }
  process.exit(0);
}

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
    console.error("HeadHunter data validation warnings:\n  - " + problems.join("\n  - "));
  }
} catch (e) {
  console.error(`HeadHunter data validation: ${e.message}`);
}
process.exit(0);
