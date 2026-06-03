---
name: integrations
description: Connect and sync HeadHunter with external tools — Notion, Google Calendar, Google Tasks, Todoist, GitHub, LinkedIn, email/WhatsApp reminders, and CSV import/export. Triggers on connect notion, sync calendar, google tasks, todoist, github, linkedin, export csv, import csv, whatsapp reminder.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Integrations

Implement the logic documented in `references/server-functions.md`. Check env
vars and MCP server health first; fall back to REST scripts when MCP is
unavailable. All syncs must be **idempotent** — never duplicate Notion pages,
calendar events, or tasks (reuse stored sync IDs).

## MCP server status

| MCP | Package | Status | Notes |
|-----|---------|--------|-------|
| Gmail | `@anthropic/gmail-mcp-server` | Official | Auth via Google OAuth |
| Google Calendar | `@anthropic/google-calendar-mcp-server` | Official | Auth via Google OAuth |
| Google Drive | Available via claude.ai platform | Official | Read/write Drive files (CV uploads) |
| Notion | `@notionhq/notion-mcp-server` | Official | Requires `NOTION_TOKEN` |
| GitHub | `@modelcontextprotocol/server-github` | Official | Requires `GITHUB_PERSONAL_ACCESS_TOKEN` |
| LinkedIn | `mcp-linkedin` (community) | **Unofficial** ⚠️ | May violate LinkedIn ToS. Uses email/password. |

## CSV import

```bash
# dry run (prints normalized JSON)
node ${CLAUDE_PLUGIN_ROOT}/scripts/csv-import.js <file.csv>
# persist
node ${CLAUDE_PLUGIN_ROOT}/scripts/csv-import.js <file.csv> --write
# import directly from a URL (LinkedIn/Notion exports)
node ${CLAUDE_PLUGIN_ROOT}/scripts/csv-import.js --url <url> --write
```
Column aliases (FIELD_MAP) are handled automatically. Report rows skipped for
missing company/role.

## CSV / JSON export

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/export-applications.js --format csv --out ./headhunter.csv
node ${CLAUDE_PLUGIN_ROOT}/scripts/export-applications.js --format json --out ./headhunter.json
```

## Notion (applications + tasks) — implemented

Env: `NOTION_TOKEN`, `NOTION_DATABASE_ID` (apps), `NOTION_TASKS_DATABASE_ID` (tasks).
Apps DB needs: Company (title), Role, Status, Priority, Location, Source, Job URL, Applied Date.
Tasks DB needs: Name (title), Status (checkbox), Priority (select), Description (rich_text), Due Date (date), Application (rich_text).

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-notion.js --dry-run       # preview both
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-notion.js                 # sync apps + tasks
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-notion.js --apps-only     # apps only
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-notion.js --tasks-only    # tasks only
```

## Google Calendar — implemented

Env: `GOOGLE_OAUTH_TOKEN` (Bearer), `GOOGLE_CALENDAR_ID` (default `primary`).
On interview create/update with `scheduled_at`: title `{round_type} Interview – {role} @ {company}`.
Saves `google_calendar_event_id`. PUT updates existing events; POST creates new ones.

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-google-calendar.js --dry-run   # preview
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-google-calendar.js             # apply
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-google-calendar.js --all       # re-sync all
```

## Google Tasks — implemented

Env: `GOOGLE_OAUTH_TOKEN` (Bearer), `GOOGLE_TASKS_LIST_ID` (default `@default`).
Saves `google_task_id`. PATCH updates existing tasks; POST creates new ones.

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-google-tasks.js --dry-run   # preview
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-google-tasks.js             # apply
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-google-tasks.js --all       # re-sync all
```

## Todoist — implemented

Env: `TODOIST_API_TOKEN`. Content `[{company}] {title}`. Priority High→4,
Medium→3, Low→2. Skips tasks that already have `todoist_task_id`.

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-todoist.js --dry-run   # preview
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-todoist.js             # apply
```

## Reminders

- **WhatsApp (Twilio) — implemented:** interviews in next 24h + overdue tasks.
  Env: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`,
  `WHATSAPP_TO`. `node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-twilio.js [--dry-run]`.
- **Stale-application reminders — implemented:** ACTIVE_STAGES apps not updated
  in 7+ days. Sends via WhatsApp (Twilio) when env set; prints digest otherwise.
  `node ${CLAUDE_PLUGIN_ROOT}/scripts/send-stale-reminders.js [--dry-run]`.

  To run daily, add to crontab (`crontab -e`):
  ```
  0 9 * * * node /path/to/headhunter/scripts/send-stale-reminders.js >> ~/.headhunter/stale-reminders.log 2>&1
  ```

## Backup and restore

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/backup.js              # create timestamped snapshot
node ${CLAUDE_PLUGIN_ROOT}/scripts/backup.js --out <dir>  # write to custom dir
node ${CLAUDE_PLUGIN_ROOT}/scripts/restore.js <backup.json> --confirm  # restore
```

## GitHub — implemented

Env: `GITHUB_PERSONAL_ACCESS_TOKEN` (classic token with `read:user`, `read:org`, `repo` scopes).

Uses the GitHub MCP (`@modelcontextprotocol/server-github`). When connected:
- Pull candidate's repos, stars, contributions into the candidate profile
- Research target company's open source presence (`org:{company}` GitHub search)
- Check engineering blog posts / release notes from GH releases

Setup: `export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...` or add to shell profile.

## LinkedIn — community MCP (unofficial) ⚠️

**Warning:** `mcp-linkedin` is an unofficial community package that uses credential-based
scraping. This may violate LinkedIn's Terms of Service. Do not use on accounts you
cannot afford to lose. Anthropic does not endorse or support this package.

Env: `LINKEDIN_EMAIL`, `LINKEDIN_PASSWORD`. Configured in `.mcp.json`.

When connected:
- Search for job listings at target companies
- Read company pages and employee counts
- View your own profile (for profile import into candidate setup)

If the LinkedIn MCP is not connected, fall back to WebSearch for LinkedIn URLs — the
briefing skill uses `WebSearch site:linkedin.com/company/...` regardless.

## Google Drive (via claude.ai platform MCP)

Available automatically when connected to claude.ai with Google Drive access.
Use it to: read your CV/resume from Drive, store briefings as Drive docs,
sync exported CSVs.

The Drive MCP is a remote MCP (not in `.mcp.json`) — it connects through the
claude.ai platform tool list as `mcp__claude_ai_Google_Drive`.

## Salary & compensation research (no MCP needed)

`/headhunter:brief` uses WebSearch to research:
- **Glassdoor** (`site:glassdoor.com "{company}" salary`)
- **Levels.fyi** (`site:levels.fyi "{company}"`)
- **Israeli salary surveys** (ethosia.co.il, salary.co.il, IVC reports)

No auth or MCP required — research-only via WebSearch.

## Setup guidance

For each integration, walk the user through OAuth/token setup step by step and
confirm env vars are present before attempting a sync. Never write secrets into
the plugin repo — they live in the user's environment only.
