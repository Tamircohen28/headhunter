#!/usr/bin/env node
// PostToolUse(Write) hook: when 04_study_guide.md is written, update the application's
// last_research_at and research_dir fields automatically.
// Reads the hook payload (tool_input) from stdin.
const fs = require("fs");
const path = require("path");
const { load, save, nowISO } = require("./lib");

let input = "";
try { input = fs.readFileSync(0, "utf8"); } catch (_) {}

let payload = {};
try { payload = JSON.parse(input || "{}"); } catch (_) {}

const filePath = (payload.tool_input && (payload.tool_input.file_path || payload.tool_input.path)) || "";

// Only act when a study guide file is written.
if (!/data[\/\\]research[\/\\]([^\/\\]+)[\/\\]04_study_guide\.md$/i.test(filePath)) process.exit(0);

const match = filePath.match(/data[\/\\]research[\/\\]([^\/\\]+)[\/\\]04_study_guide\.md$/i);
const appId = match && match[1];
if (!appId) process.exit(0);

try {
  const apps = load("applications");
  const app = apps.find((a) => a.id === appId);
  if (!app) { console.error(`post-research-hook: no application found for id ${appId}`); process.exit(0); }

  const researchDir = path.dirname(filePath).replace(/^.*?(data[\/\\]research)/, "$1");
  app.research_dir = researchDir;
  app.last_research_at = nowISO();
  app.research_status = "complete";
  app.updated_date = nowISO();
  save("applications", apps);
  console.error(`post-research-hook: updated ${appId} → research_dir=${researchDir}, research_status=complete`);
} catch (e) {
  console.error(`post-research-hook error: ${e.message}`);
}
process.exit(0);
