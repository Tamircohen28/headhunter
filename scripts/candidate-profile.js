#!/usr/bin/env node
// Manage the candidate profile (read, write, show, extract-cv).
// Usage:
//   node candidate-profile.js show
//   node candidate-profile.js set '<json-patch>'
//   node candidate-profile.js extract-cv <file>   (reads PDF/text, stores as .cv.text)
//   node candidate-profile.js reset               (reset to blank template, requires --confirm)
const fs = require("fs");
const path = require("path");
const { DATA_DIR } = require("./lib");

const PROFILE_FILE = path.join(DATA_DIR, "candidate-profile.json");

const BLANK = {
  personal: { name: "", email: "", phone: "", linkedin_url: "", github_url: "", portfolio_url: "", location: "", timezone: "Asia/Jerusalem" },
  cv: { file_path: "", text: "", last_updated: "" },
  experience: { years_total: null, current_title: "", current_company: "", years_at_current: null, summary: "", key_skills: [], specializations: [], open_source_projects: [], certifications: [], education: "" },
  preferences: {
    target_roles: [], target_companies: [], exclude_companies: [], industries: [],
    locations: [], remote_type: "", company_stage: [], company_size: "",
    must_haves: [], deal_breakers: [], why_looking: "", career_goal_3yr: "",
    priority_weights: { comp: 5, growth: 5, wlb: 5, tech: 5, mission: 5 },
  },
  salary: { current_base_ils: null, current_total_ils: null, target_base_ils: null, target_total_ils: null, floor_ils: null, notes: "" },
  availability: { available_from: "", notice_period_days: null, actively_looking: true },
  application_defaults: { cover_letter_template: "", languages: [], visa_status: "Citizen", work_authorization: "IL" },
  past_interview_patterns: [],
  github_imported_at: null,
  linkedin_imported_at: null,
};

function load() {
  if (!fs.existsSync(PROFILE_FILE)) return JSON.parse(JSON.stringify(BLANK));
  return JSON.parse(fs.readFileSync(PROFILE_FILE, "utf8"));
}

function save(profile) {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(PROFILE_FILE, JSON.stringify(profile, null, 2) + "\n");
}

function deepMerge(target, patch) {
  for (const [k, v] of Object.entries(patch)) {
    if (v && typeof v === "object" && !Array.isArray(v) && typeof target[k] === "object" && !Array.isArray(target[k])) {
      deepMerge(target[k], v);
    } else {
      target[k] = v;
    }
  }
}

const [, , cmd, ...args] = process.argv;

switch (cmd) {
  case "show": {
    const p = load();
    console.log(JSON.stringify(p, null, 2));
    break;
  }

  case "set": {
    if (!args[0]) { console.error("Usage: candidate-profile.js set '<json-patch>'"); process.exit(1); }
    const profile = load();
    const patch = JSON.parse(args[0]);
    deepMerge(profile, patch);
    save(profile);
    console.error("Profile updated.");
    console.log(JSON.stringify(profile, null, 2));
    break;
  }

  case "extract-cv": {
    const file = args[0];
    if (!file || !fs.existsSync(file)) { console.error(`File not found: ${file}`); process.exit(1); }
    const ext = path.extname(file).toLowerCase();
    let text = "";
    if (ext === ".pdf") {
      // For PDFs, output a message instructing Claude to read the file with the Read tool
      // and pass the extracted text via `set '{"cv":{"text":"..."}}'`
      console.error(`PDF detected: ${file}`);
      console.error("Use the Read tool to read the PDF, then run:");
      console.error(`  node candidate-profile.js set '{"cv":{"file_path":"${file}","text":"<extracted text>","last_updated":"${new Date().toISOString()}"}}'`);
      process.exit(0);
    } else {
      text = fs.readFileSync(file, "utf8");
    }
    const profile = load();
    profile.cv.file_path = file;
    profile.cv.text = text.trim();
    profile.cv.last_updated = new Date().toISOString();
    save(profile);
    console.error(`CV extracted from ${file} (${text.length} chars). Profile updated.`);
    break;
  }

  case "reset": {
    if (!process.argv.includes("--confirm")) {
      console.error("This will reset your candidate profile to blank. Re-run with --confirm to proceed.");
      process.exit(1);
    }
    save(JSON.parse(JSON.stringify(BLANK)));
    console.error("Candidate profile reset to blank.");
    break;
  }

  default:
    console.error("Commands: show | set '<json>' | extract-cv <file> | reset [--confirm]");
    process.exit(1);
}
