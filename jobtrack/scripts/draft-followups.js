#!/usr/bin/env node
// Identify applications needing follow-up and output structured drafts.
// Scenarios: post-apply silence, post-interview silence, offer deadline.
// Usage: node draft-followups.js [--dry-run] [--json]
const { load } = require("./lib");

const dry = process.argv.includes("--dry-run");
const json = process.argv.includes("--json");

const now = Date.now();
const DAY = 86400000;

const apps = load("applications");
const interviews = load("interviews");
const contacts = load("contacts");
const events = load("events");

const appById = Object.fromEntries(apps.map(a => [a.id, a]));
const contactsByApp = {};
for (const c of contacts) {
  if (!contactsByApp[c.application_id]) contactsByApp[c.application_id] = [];
  contactsByApp[c.application_id].push(c);
}
const interviewsByApp = {};
for (const i of interviews) {
  if (!interviewsByApp[i.application_id]) interviewsByApp[i.application_id] = [];
  interviewsByApp[i.application_id].push(i);
}

const followups = [];

for (const app of apps) {
  const appContacts = contactsByApp[app.id] || [];
  const recruiter = appContacts.find(c => /recruiter|hr|talent/i.test(c.role_at_company || "")) || appContacts[0];
  const appInterviews = interviewsByApp[app.id] || [];

  // Scenario 1: Post-apply silence (Applied 7+ days, no screen yet)
  if (app.status === "Applied" && app.applied_date) {
    const daysSince = Math.floor((now - new Date(app.applied_date).getTime()) / DAY);
    if (daysSince >= 7) {
      followups.push({
        application_id: app.id,
        company: app.company,
        role: app.role,
        scenario: "post-apply-silence",
        days: daysSince,
        contact_name: recruiter?.name || null,
        contact_email: recruiter?.email || null,
        subject: `Following up — ${app.role} application`,
        body: `Hi ${recruiter?.name?.split(" ")[0] || "there"},\n\nI wanted to follow up on my application for the ${app.role} role${app.applied_date ? ` submitted on ${String(app.applied_date).slice(0, 10)}` : ""}. I remain very interested in ${app.company}${app.job_url ? " and the position" : ""}. Please let me know if you need any additional information or have any questions.\n\nThank you for your time.\n\nBest regards`,
      });
    }
  }

  // Scenario 2: Post-interview silence (Completed interview 3+ days ago, no next step)
  const completedInterviews = appInterviews.filter(i => i.status === "Completed");
  const scheduledInterviews = appInterviews.filter(i => i.status === "Scheduled");
  if (completedInterviews.length > 0 && scheduledInterviews.length === 0 && app.status !== "Offer" && !["Rejected", "Declined", "Ghosted", "Accepted"].includes(app.status)) {
    const lastCompleted = completedInterviews.sort((a, b) => new Date(b.scheduled_at) - new Date(a.scheduled_at))[0];
    if (lastCompleted.scheduled_at) {
      const daysSince = Math.floor((now - new Date(lastCompleted.scheduled_at).getTime()) / DAY);
      if (daysSince >= 3) {
        followups.push({
          application_id: app.id,
          company: app.company,
          role: app.role,
          scenario: "post-interview-silence",
          days: daysSince,
          round_type: lastCompleted.round_type,
          contact_name: recruiter?.name || null,
          contact_email: recruiter?.email || null,
          subject: `Following up — ${app.role} interview`,
          body: `Hi ${recruiter?.name?.split(" ")[0] || "there"},\n\nThank you again for the ${lastCompleted.round_type} interview${lastCompleted.scheduled_at ? ` on ${String(lastCompleted.scheduled_at).slice(0, 10)}` : ""}. I really enjoyed learning more about the team and the role. I remain enthusiastic about the opportunity and wanted to check in on next steps.\n\nPlease don't hesitate to reach out if you need anything further from me.\n\nBest regards`,
        });
      }
    }
  }

  // Scenario 3: Offer deadline (status=Offer, no action in 2+ days)
  if (app.status === "Offer") {
    const offerEvents = events.filter(e => e.application_id === app.id && e.type === "status_change" && e.meta?.to === "Offer");
    if (offerEvents.length > 0) {
      const offerDate = new Date(offerEvents[offerEvents.length - 1].ts);
      const daysSince = Math.floor((now - offerDate.getTime()) / DAY);
      if (daysSince >= 2 && daysSince < 14) {
        followups.push({
          application_id: app.id,
          company: app.company,
          role: app.role,
          scenario: "offer-deadline",
          days: daysSince,
          contact_name: recruiter?.name || null,
          contact_email: recruiter?.email || null,
          subject: `Offer for ${app.role} — follow-up`,
          body: `Hi ${recruiter?.name?.split(" ")[0] || "there"},\n\nThank you for the offer for the ${app.role} role — I'm very excited about the opportunity. I'm in the process of reviewing the details carefully. Would it be possible to have until [preferred date] to give you a final answer? I want to make sure I'm fully prepared to commit.\n\nThank you for your patience.\n\nBest regards`,
        });
      }
    }
  }
}

if (!followups.length) {
  console.error("No follow-ups needed right now.");
  process.exit(0);
}

if (json || dry) {
  console.log(JSON.stringify(followups, null, 2));
  if (dry) console.error(`[dry-run] ${followups.length} follow-up(s) identified.`);
  process.exit(0);
}

// Human-readable output
console.log(`\n=== Follow-ups ready (${followups.length}) ===\n`);
for (let i = 0; i < followups.length; i++) {
  const f = followups[i];
  const scenario = { "post-apply-silence": "POST-APPLY SILENCE", "post-interview-silence": "POST-INTERVIEW SILENCE", "offer-deadline": "OFFER DEADLINE" }[f.scenario];
  console.log(`${i + 1}. [${f.company} — ${f.role}] — ${scenario} (${f.days}d)`);
  if (f.contact_email) console.log(`   To: ${f.contact_email}`);
  console.log(`   Subject: ${f.subject}`);
  console.log(`   ---`);
  console.log(f.body.split("\n").map(l => `   ${l}`).join("\n"));
  console.log();
}
