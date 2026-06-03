#!/usr/bin/env node
// Classify job-application status from emails and match to an application.
// Usage:
//   node detect-gmail-status.js --fixtures references/email-fixtures.md
//   node detect-gmail-status.js --json '[{"from":..,"subject":..,"body":..}]'
const fs = require("fs");
const path = require("path");
const { load } = require("./lib");

// Ordered most-advanced first; first match wins.
const PATTERNS = [
  ["Offer", /offer letter|pleased to offer|job offer|extend an offer/i],
  ["Onsite", /onsite interview|on-?site|final round|panel interview/i],
  ["Technical", /technical interview|coding challenge|take-?home|hackerrank/i],
  ["Phone Screen", /phone screen|intro call|recruiter call|initial call/i],
  ["Rejected", /unfortunately|not moving forward|regret to inform|decided to (proceed|move forward) with other/i],
];

function classify(email) {
  const hay = `${email.subject || ""}\n${email.body || ""}`;
  for (const [status, re] of PATTERNS) if (re.test(hay)) return status;
  return null;
}

function matchApplication(email, apps) {
  const hay = `${email.subject || ""} ${email.from || ""} ${email.body || ""}`.toLowerCase();
  return apps.find((a) => a.company && hay.includes(a.company.toLowerCase())) || null;
}

function arg(name) {
  const i = process.argv.indexOf(`--${name}`);
  return i !== -1 ? process.argv[i + 1] : null;
}

function loadFixtures(file) {
  const text = fs.readFileSync(file, "utf8");
  const m = text.match(/```json\s*([\s\S]*?)```/);
  if (!m) throw new Error("No ```json block found in fixtures file");
  return JSON.parse(m[1]);
}

let emails;
const fixtures = arg("fixtures");
const jsonArg = arg("json");
if (fixtures) emails = loadFixtures(path.resolve(fixtures));
else if (jsonArg) emails = JSON.parse(jsonArg);
else {
  console.error("Provide --fixtures FILE or --json '[...]'");
  process.exit(1);
}

const apps = load("applications");
const results = emails.map((e) => {
  const status = classify(e);
  const app = matchApplication(e, apps);
  return {
    id: e.id,
    from: e.from,
    detected_status: status,
    matched_company: app ? app.company : null,
    matched_application_id: app ? app.id : null,
  };
});

console.log(JSON.stringify(results, null, 2));
