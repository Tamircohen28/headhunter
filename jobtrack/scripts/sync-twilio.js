#!/usr/bin/env node
// Send a WhatsApp reminder digest via Twilio: interviews in next 24h + overdue tasks.
// Env: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, WHATSAPP_TO
// Usage: node sync-twilio.js [--dry-run]
const { load } = require("./lib");

const { TWILIO_ACCOUNT_SID: SID, TWILIO_AUTH_TOKEN: AUTH, TWILIO_WHATSAPP_FROM: FROM, WHATSAPP_TO: TO } = process.env;
const dry = process.argv.includes("--dry-run");
const now = Date.now(), DAY = 86400000;

const apps = Object.fromEntries(load("applications").map((a) => [a.id, a]));
const interviews = load("interviews").filter((i) =>
  i.status === "Scheduled" && i.scheduled_at &&
  new Date(i.scheduled_at).getTime() >= now && new Date(i.scheduled_at).getTime() <= now + DAY);
const overdue = load("tasks").filter((t) => !t.completed && t.due_date && new Date(t.due_date).getTime() < now);

const lines = ["🔔 JobTrack reminders"];
if (interviews.length) {
  lines.push("\nInterviews in next 24h:");
  for (const i of interviews) lines.push(`• ${i.scheduled_at.slice(11, 16)} ${i.round_type} @ ${apps[i.application_id]?.company ?? "?"}`);
}
if (overdue.length) {
  lines.push("\nOverdue tasks:");
  for (const t of overdue) lines.push(`• ${t.title}`);
}
const body = lines.join("\n");

if (!interviews.length && !overdue.length) { console.error("Nothing to remind about."); process.exit(0); }

if (dry || !(SID && AUTH && FROM && TO)) {
  if (!dry) console.error("Twilio env not fully set — showing message instead of sending:\n");
  console.log(body);
  process.exit(0);
}

(async () => {
  const form = new URLSearchParams({ From: `whatsapp:${FROM}`, To: `whatsapp:${TO}`, Body: body });
  const res = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${SID}/Messages.json`, {
    method: "POST",
    headers: { Authorization: "Basic " + Buffer.from(`${SID}:${AUTH}`).toString("base64"), "Content-Type": "application/x-www-form-urlencoded" },
    body: form,
  });
  if (!res.ok) { console.error(`Twilio error: ${res.status} ${await res.text()}`); process.exit(1); }
  console.error("WhatsApp reminder sent.");
})();
