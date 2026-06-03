#!/usr/bin/env node
// Deterministic pre-scoring helper for the job scanner.
// Counts skill overlaps, checks salary range, checks remote/location match.
// Outputs a pre-score JSON that the job-scorer agent uses as an anchor.
// Usage: node score-job.js <job-metadata.json> [--profile <candidate-profile.json>]
const fs = require("fs");
const path = require("path");
const { DATA_DIR } = require("./lib");

const metaArg = process.argv[2];
const profileIdx = process.argv.indexOf("--profile");
const profileArg = profileIdx !== -1 ? process.argv[profileIdx + 1] : null;

if (!metaArg) { console.error("Usage: score-job.js <job-metadata.json> [--profile <candidate-profile.json>]"); process.exit(1); }
if (!fs.existsSync(metaArg)) { console.error(`File not found: ${metaArg}`); process.exit(1); }

const meta = JSON.parse(fs.readFileSync(metaArg, "utf8"));
const profileFile = profileArg || path.join(DATA_DIR, "candidate-profile.json");
const profile = fs.existsSync(profileFile) ? JSON.parse(fs.readFileSync(profileFile, "utf8")) : null;

if (!profile) {
  console.log(JSON.stringify({ error: "No candidate profile found. Run /jobtrack:setup first.", pre_score: null }));
  process.exit(0);
}

// ── Skill overlap (max 35 pts) ──────────────────────────────────────────────
const candidateSkills = (profile.experience?.key_skills || []).map(s => s.toLowerCase());
const requiredSkills = (meta.required_skills || []).map(s => s.toLowerCase());
const preferredSkills = (meta.preferred_skills || []).map(s => s.toLowerCase());
const niceSkills = (meta.nice_to_have_skills || []).map(s => s.toLowerCase());

const reqMatches = requiredSkills.filter(s => candidateSkills.some(c => c.includes(s) || s.includes(c)));
const prefMatches = preferredSkills.filter(s => candidateSkills.some(c => c.includes(s) || s.includes(c)));

const skillPct = requiredSkills.length > 0 ? reqMatches.length / requiredSkills.length : 0.5;
const prefPct = preferredSkills.length > 0 ? prefMatches.length / preferredSkills.length : 0.5;
const skillScore = Math.round(skillPct * 28 + prefPct * 7);

const missingRequired = requiredSkills.filter(s => !reqMatches.includes(s));
const matchedRequired = reqMatches;

// ── Experience level (max 25 pts) ──────────────────────────────────────────
const candidateYears = profile.experience?.years_total || 0;
const jobTitle = (meta.job_title || "").toLowerCase();
const isSenior = /senior|staff|principal|lead|sr\./.test(jobTitle);
const isJunior = /junior|jr\.|entry|associate/.test(jobTitle);
const isManager = /manager|director|head of|vp/.test(jobTitle);

let expScore = 15; // default medium
if (isSenior && candidateYears >= 5) expScore = 25;
else if (isSenior && candidateYears >= 3) expScore = 18;
else if (isSenior && candidateYears < 3) expScore = 8;
else if (isJunior && candidateYears <= 2) expScore = 25;
else if (isJunior && candidateYears <= 4) expScore = 20;
else if (!isSenior && !isJunior && candidateYears >= 2) expScore = 20;

// ── Location / remote (max 20 pts) ─────────────────────────────────────────
const candidateRemote = (profile.preferences?.remote_type || "").toLowerCase();
const jobRemote = (meta.location || "").toLowerCase();
const isRemoteJob = /remote/.test(jobRemote);
const isHybridJob = /hybrid/.test(jobRemote);

let locationScore = 10; // default unknown
if (candidateRemote === "remote" && isRemoteJob) locationScore = 20;
else if (candidateRemote === "hybrid" && (isHybridJob || isRemoteJob)) locationScore = 18;
else if (candidateRemote === "on-site" && !isRemoteJob && !isHybridJob) locationScore = 20;
else if (candidateRemote === "" || candidateRemote === "no preference") locationScore = 15;
else if (candidateRemote === "remote" && !isRemoteJob) locationScore = 5;

// ── Salary overlap (max 20 pts) ────────────────────────────────────────────
const targetBase = profile.salary?.target_base_ils || 0;
const floor = profile.salary?.floor_ils || 0;
// Job metadata doesn't always have salary; agent will fill this
let salaryScore = 10; // unknown = neutral
let salaryNote = "Job salary range not in metadata — agent will research";

// ── Assemble pre-score ─────────────────────────────────────────────────────
const preMatchScore = skillScore + expScore + locationScore + salaryScore;

const result = {
  pre_match_score: preMatchScore,
  breakdown: {
    skills: skillScore,
    experience: expScore,
    location: locationScore,
    salary: salaryScore,
  },
  skill_detail: {
    required_total: requiredSkills.length,
    required_matched: reqMatches.length,
    required_missing: missingRequired,
    preferred_total: preferredSkills.length,
    preferred_matched: prefMatches.length,
    match_pct: Math.round(skillPct * 100),
  },
  candidate_context: {
    years: candidateYears,
    title: profile.experience?.current_title || "",
    remote_pref: profile.preferences?.remote_type || "",
    target_base_ils: targetBase,
    floor_ils: floor,
    key_skills: candidateSkills,
    target_roles: profile.preferences?.target_roles || [],
    priority_weights: profile.preferences?.priority_weights || {},
  },
  salary_note: salaryNote,
  notes: [
    requiredSkills.length === 0 ? "No required skills parsed — agent should infer from description" : null,
    missingRequired.length > 0 ? `Missing required: ${missingRequired.slice(0, 3).join(", ")}` : "All required skills matched",
  ].filter(Boolean),
};

console.log(JSON.stringify(result, null, 2));
