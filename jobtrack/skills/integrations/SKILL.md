---
name: integrations
description: Connect and sync JobTrack with external tools — Notion, Google Calendar, Google Tasks, Todoist, email/WhatsApp reminders, and CSV import/export. Triggers on connect notion, sync calendar, google tasks, todoist, export csv, import csv, whatsapp reminder.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Integrations

Implement the logic documented in `references/server-functions.md`. Check env
vars and MCP server health first; fall back to REST scripts when MCP is
unavailable. All syncs must be **idempotent** — never duplicate Notion pages,
calendar events, or tasks (reuse stored sync IDs).

## CSV import

```bash
# dry run (prints normalized JSON)
node ${CLAUDE_PLUGIN_ROOT}/scripts/csv-import.js <file.csv>
# persist
node ${CLAUDE_PLUGIN_ROOT}/scripts/csv-import.js <file.csv> --write
```
Column aliases (FIELD_MAP) are handled automatically. Report rows skipped for
missing company/role.

## CSV / JSON export

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/export-applications.js --format csv --out ./jobtrack.csv
node ${CLAUDE_PLUGIN_ROOT}/scripts/export-applications.js --format json --out ./jobtrack.json
```

## Notion (applications)

Env: `NOTION_DATABASE_ID`, `NOTION_TOKEN`. Properties: Company (title), Role,
Status, Priority, Location, Source, Job URL, Applied Date. PATCH if
`notion_page_id` set, else POST; save `notion_page_id` back on the application.

## Notion (tasks)

Env: `NOTION_TASKS_DATABASE_ID`. Properties: Name, Status (checkbox), Priority,
Description, Due Date, Application (rich text). Save `notion_task_page_id`.

## Google Calendar

Env via Google MCP/OAuth. On interview create/update with `scheduled_at`:
title `{round_type} Interview – {role} @ {company}`, description = prep_notes +
meet link + interviewer. Save `google_calendar_event_id`.

## Google Tasks

Env: `GOOGLE_TASKS_LIST_ID` (default `@default`). Save `google_task_id`.

## Todoist

Env: `TODOIST_API_TOKEN`. Content `[{company}] {title}`. Priority High→4,
Medium→3, Low→2. Skip if `todoist_task_id` already set.

## Reminders

- **Stale apps:** ACTIVE_STAGES apps not updated in 7+ days → email digest.
- **WhatsApp (Twilio):** interviews in next 24h + overdue tasks. Env:
  `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`, `WHATSAPP_TO`.

## Setup guidance

For each integration, walk the user through OAuth/token setup step by step and
confirm env vars are present before attempting a sync. Never write secrets into
the plugin repo — they live in the user's environment only.
