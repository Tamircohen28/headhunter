# JobTrack — Claude Code Plugin

A job-search CRM as a Claude Code workflow layer: pipeline, interviews, tasks,
contacts, notes, analytics, and integrations (Gmail, Google Calendar, Google
Tasks, Notion, Todoist, email/WhatsApp reminders) — all from the terminal.

This is a **workflow layer**, not a UI replacement. It mirrors the JobTrack
Base44 web app's behavior through skills, slash commands, subagents, MCP
servers, and small Node scripts.

## Install

```bash
# local path
/plugin install ./jobtrack
```

Requires Node.js (for the bundled scripts). No npm dependencies.

## First run

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js seed   # load demo data
```

Or just start adding: `/jobtrack:add-application`.

## What you get

### Skills (auto-discovered)
- **jobtrack-core** — read/add/update applications, interviews, tasks, contacts, notes; analytics & dashboard.
- **pipeline** — Kanban board + forward-only stage moves.
- **interview-research** — the job4u pipeline, ported to native subagents: scrape → analyze + web-research → divide topics across parallel research agents → merge into a study guide, attached to an application.
- **interview-prep** — upcoming interviews, prep checklists, prep briefs, mock questions (consumes research output).
- **gmail-status-scan** — detect status changes from email (with approval gate).
- **integrations** — Notion / Calendar / Google Tasks / Todoist / CSV / reminders.
- **scaffold-base44-app** — developer mode: regenerate the React web app + entities + Deno functions.

### The job4u research pipeline (native port)

The original `job4u` Python project scraped a job, analyzed it with OpenAI, then
divided study topics across multiple research agents and merged the results.
The **`interview-research`** skill reproduces this with **zero Python and no
OpenAI** — Claude Code subagents do the work:

| job4u (Python) | This plugin (native) |
|----------------|----------------------|
| Playwright scraper | `WebFetch` (or paste) |
| gpt-4o-mini browsing analysis | `job-analyzer` subagent + `WebSearch` |
| `TaskExecutor` topic division + deep-research | parallel `topic-researcher` subagents |
| consolidation | `study-guide-writer` subagent |
| `output_*/run_*/` files | `data/research/<appId>/` linked to the application |

Run it with `/jobtrack:research <url-or-app>`. See `references/pipeline.md`.

### Slash commands
- `/jobtrack:add-application`
- `/jobtrack:pipeline`
- `/jobtrack:log-interview`
- `/jobtrack:add-task`
- `/jobtrack:export-data`
- `/jobtrack:research`

### Subagents
- `job-analyzer` — scrape + web-research a posting into JobMetadata.
- `topic-researcher` — deep-research a batch of topics (spawned in parallel).
- `study-guide-writer` — merge research into a study guide + plan.
- `interview-analyst` — performance analysis + next-round predictor.
- `stale-applications` — finds 7+ day stale apps, drafts follow-ups.

### Hooks
- **SessionStart** — pipeline + next-48h interviews + overdue tasks briefing.
  Emits structured output (`hookSpecificOutput.additionalContext` +
  `sessionTitle`, e.g. `JobTrack · 5 apps · 4 active · 2 overdue`).
- **PostToolUse(Write)** — validates `data/*.json` schema (`continueOnBlock`).

Both hooks use the exec **`args`** form (no shell quoting of
`${CLAUDE_PLUGIN_ROOT}` paths).

## Latest Claude Code features used

This plugin targets current Claude Code (v2.1.15x):

- **Auto-loading skills** — drop-in under `.claude/skills`, no marketplace needed.
- **Hook exec `args` form** + `continueOnBlock` (v2.1.139).
- **Structured `SessionStart` output** — `additionalContext`, `sessionTitle`,
  `reloadSkills` (v2.1.152).
- **SKILL `effort`** — `interview-research` runs at `effort: high` (v2.1.157).
- **Dynamic workflows** — the research fan-out runs as managed background
  agents via `ultracode` / `/effort xhigh`, tracked with `/workflows` (v2.1.154).
- **`/reload-skills`** to pick up edits mid-session during development.

## Data backends (in preference order)

1. **Base44 API** — if `VITE_BASE44_APP_ID` + token set.
2. **Local JSON** (default) — `${CLAUDE_PLUGIN_ROOT}/data/*.json`.
3. **Notion** — when Notion MCP connected.

See `references/data-model.md` and `references/status-config.md`.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/crud.js` | list/add/update/move/complete-task/seed |
| `scripts/csv-import.js` | CSV → applications (alias mapping) |
| `scripts/parse-csv-import.sh` | wrapper for csv-import |
| `scripts/export-applications.js` | export CSV or JSON |
| `scripts/detect-gmail-status.js` | classify email → status |
| `scripts/session-briefing.js` | SessionStart summary |
| `scripts/validate-data.js` | PostToolUse data validation |

## Environment variables

| Variable | Used by |
|----------|---------|
| `VITE_BASE44_APP_ID` | Base44 client |
| `VITE_BASE44_APP_BASE_URL` | Base44 backend URL |
| `NOTION_TOKEN` | Notion MCP |
| `NOTION_DATABASE_ID` | Application → Notion sync |
| `NOTION_TASKS_DATABASE_ID` | Task → Notion sync |
| `GOOGLE_TASKS_LIST_ID` | Google Tasks (default `@default`) |
| `TODOIST_API_TOKEN` | Todoist sync |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_WHATSAPP_FROM` / `WHATSAPP_TO` | WhatsApp reminders |
| `JOBTRACK_DATA_DIR` | Override local data dir (defaults to `${CLAUDE_PLUGIN_ROOT}/data`) |

**Secrets live in your environment only — never commit them.** `data/` and
`.env` are gitignored.

## Integration setup

Enable MCP servers in `.mcp.json` (Gmail, Google Calendar, Notion). Adapt the
npm package names to whatever is current. When a server isn't available, the
plugin falls back to the REST logic documented in `references/server-functions.md`.

## Testing

```bash
node scripts/crud.js seed
node scripts/export-applications.js --format csv --out /tmp/jobtrack-test.csv
node scripts/detect-gmail-status.js --fixtures references/email-fixtures.md
```
