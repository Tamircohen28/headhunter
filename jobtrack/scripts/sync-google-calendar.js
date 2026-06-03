#!/usr/bin/env node
// Sync jobtrack interview rounds to Google Calendar (REST v3). Idempotent via google_calendar_event_id.
// Env: GOOGLE_OAUTH_TOKEN (Bearer), GOOGLE_CALENDAR_ID (default 'primary')
// Usage: node sync-google-calendar.js [--dry-run] [--all]
const { load, save } = require("./lib");

const TOKEN = process.env.GOOGLE_OAUTH_TOKEN;
const CALENDAR_ID = process.env.GOOGLE_CALENDAR_ID || "primary";
const dry = process.argv.includes("--dry-run");
const all = process.argv.includes("--all");

if (!TOKEN && !dry) { console.error("GOOGLE_OAUTH_TOKEN not set. Use --dry-run to preview."); process.exit(1); }

const interviews = load("interviews");
const apps = Object.fromEntries(load("applications").map((a) => [a.id, a]));

const pending = interviews.filter((i) =>
  i.scheduled_at && (all || !i.google_calendar_event_id)
);

if (!pending.length) { console.error("No interview rounds to sync."); process.exit(0); }

function buildEvent(i, app) {
  const start = new Date(i.scheduled_at).toISOString();
  const end = new Date(new Date(i.scheduled_at).getTime() + (i.duration_minutes || 60) * 60000).toISOString();
  const description = [
    i.prep_notes && `Prep notes:\n${i.prep_notes}`,
    i.google_meet_link && `Meet: ${i.google_meet_link}`,
    i.interviewer_name && `Interviewer: ${i.interviewer_name}`,
  ].filter(Boolean).join("\n\n");

  return {
    summary: `${i.round_type} Interview – ${app ? app.role : "?"} @ ${app ? app.company : "?"}`,
    description: description || undefined,
    start: { dateTime: start },
    end: { dateTime: end },
  };
}

async function gcal(method, pathSuffix, body) {
  const url = `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(CALENDAR_ID)}/events${pathSuffix}`;
  const res = await fetch(url, {
    method,
    headers: { Authorization: `Bearer ${TOKEN}`, "Content-Type": "application/json" },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

(async () => {
  let created = 0, updated = 0;
  for (const i of pending) {
    const app = apps[i.application_id];
    const event = buildEvent(i, app);

    if (dry) {
      const action = i.google_calendar_event_id ? "PUT" : "POST";
      console.log(`[dry-run] ${action} Calendar: ${event.summary} @ ${i.scheduled_at}`);
      continue;
    }

    try {
      if (i.google_calendar_event_id) {
        await gcal("PUT", `/${i.google_calendar_event_id}`, event);
        updated++;
      } else {
        const created_event = await gcal("POST", "", event);
        i.google_calendar_event_id = created_event.id;
        created++;
      }
    } catch (e) {
      console.error(`Calendar error for ${event.summary}: ${e.message}`);
    }
  }

  if (!dry) {
    save("interviews", interviews);
    console.error(`Calendar sync: ${created} created, ${updated} updated.`);
  } else {
    console.error(`[dry-run] ${pending.length} interview(s) would sync.`);
  }
})();
