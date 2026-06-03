#!/usr/bin/env node
// Find stale applications (ACTIVE_STAGES, not updated in staleThresholdDays) and
// send a WhatsApp digest via Twilio, or print to stdout if Twilio is not configured.
// Env: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, WHATSAPP_TO
// Usage: node send-stale-reminders.js [--dry-run]
//
// Recommended daily cron (edit with `crontab -e`):
//   0 9 * * * node /path/to/headhunter/scripts/send-stale-reminders.js >> ~/.headhunter/stale-reminders.log 2>&1
const path = require("path");
const fs = require("fs");
const { load } = require("./lib");

const dry = process.argv.includes("--dry-run");
const { TWILIO_ACCOUNT_SID: SID, TWILIO_AUTH_TOKEN: AUTH, TWILIO_WHATSAPP_FROM: FROM, WHATSAPP_TO: TO } = process.env;

const settingsPath = path.join(process.env.CLAUDE_PLUGIN_ROOT || path.join(__dirname, ".."), "settings.json");
let staleThreshold = 7;
try {
  const cfg = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
  staleThreshold = cfg.headhunter?.staleThresholdDays ?? 7;
} catch (_) {}

const ACTIVE_STAGES = ["Applied", "Phone Screen", "Technical", "Onsite", "Offer"];
const cutoff = Date.now() - staleThreshold * 86400000;

const apps = load("applications").filter(
  (a) => ACTIVE_STAGES.includes(a.status) && new Date(a.updated_date).getTime() < cutoff
).sort((a, b) => new Date(a.updated_date) - new Date(b.updated_date));

if (!apps.length) { console.error("No stale applications — nothing to send."); process.exit(0); }

const daysStale = (a) => Math.floor((Date.now() - new Date(a.updated_date).getTime()) / 86400000);

const lines = [`🔔 HeadHunter: ${apps.length} stale application(s) (${staleThreshold}+ days without update)`];
for (const a of apps) lines.push(`• ${a.company} – ${a.role} (${a.status}, ${daysStale(a)}d stale)`);

const body = lines.join("\n");

if (dry || !(SID && AUTH && FROM && TO)) {
  if (!dry) console.error("Twilio env not fully set — printing digest instead of sending:\n");
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
  console.error(`Stale-application reminder sent (${apps.length} apps).`);
})();
