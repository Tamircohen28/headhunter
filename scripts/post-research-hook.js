#!/usr/bin/env node
// PostToolUse(Write): when 04_study_guide.md is written, update application research fields.
const fs = require("fs");
const path = require("path");
const { load, save, nowISO, DATA_DIR } = require("./lib");

let input = "";
try { input = fs.readFileSync(0, "utf8"); } catch (_) {}

let payload = {};
try { payload = JSON.parse(input || "{}"); } catch (_) {}

const filePath = (payload.tool_input && (payload.tool_input.file_path || payload.tool_input.path)) || "";
if (!filePath) process.exit(0);

if (!/04_study_guide\.md$/i.test(filePath)) process.exit(0);

let researchDir = null;
let appId = null;

// data/research/<slug>/04_study_guide.md
const slugMatch = filePath.match(/data[\/\\]research[\/\\]([^\/\\]+)[\/\\]04_study_guide\.md$/i);
if (slugMatch) {
  researchDir = `data/research/${slugMatch[1]}`;
  try {
    const manifestPath = path.join(DATA_DIR, "research", slugMatch[1], "00_run.json");
    if (fs.existsSync(manifestPath)) {
      const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
      if (m.application_id) appId = m.application_id;
    }
  } catch (_) { /* ignore */ }
}

// Legacy: data/research/app_<id>/04_study_guide.md
if (!appId) {
  const legacy = filePath.match(/data[\/\\]research[\/\\](app_[^\/\\]+)[\/\\]04_study_guide\.md$/i);
  if (legacy) {
    appId = legacy[1];
    researchDir = `data/research/${appId}`;
  }
}

if (!researchDir) process.exit(0);

try {
  const apps = load("applications");
  const app = appId ? apps.find((a) => a.id === appId) : apps.find((a) => a.research_dir === researchDir);
  if (!app) {
    console.error(`post-research-hook: no application for ${researchDir}`);
    process.exit(0);
  }

  app.research_dir = researchDir;
  app.last_research_at = nowISO();
  app.research_status = "complete";
  app.updated_date = nowISO();
  save("applications", apps);
  console.error(`post-research-hook: updated ${app.id} → research_dir=${researchDir}`);
} catch (e) {
  console.error(`post-research-hook error: ${e.message}`);
}
process.exit(0);
