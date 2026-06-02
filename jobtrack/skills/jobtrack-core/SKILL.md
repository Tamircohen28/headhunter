---
name: jobtrack-core
description: Core job-search CRM operations — read, add, and update job applications, interviews, tasks, contacts, and notes. Triggers on job application, job search, track applications, job pipeline, offer, rejection, application status.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# JobTrack Core

You manage the user's job-search CRM. Data lives in
`${CLAUDE_PLUGIN_ROOT}/data/*.json` (local store, the default backend). If
`VITE_BASE44_APP_ID` and a token are set, prefer the Base44 API; if Notion MCP
is connected and the user wants it, mirror there. Otherwise use local JSON.

## Backend & helpers

Use the bundled Node CLI for all reads/writes (it enforces IDs, timestamps,
and rules — never hand-edit JSON unless repairing corruption):

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list applications
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js add applications '{"company":"Acme","role":"SWE"}'
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js update applications app_001 '{"priority":"High"}'
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js move app_001 "Technical"
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js complete-task task_004
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js seed   # first-run demo data
```

Entities: `applications`, `interviews`, `tasks`, `contacts`, `notes`.

## Rules (enforce strictly)

- Read the data model in `references/data-model.md` and status rules in
  `references/status-config.md` before writing.
- Validate enum values before any write (status, priority, round_type, etc.).
- Status moves are **forward-only**; `Rejected`/`Declined`/`Ghosted` allowed
  from any stage. The `move` command enforces this — don't bypass it without
  explicit user confirmation.
- Always bump `updated_date` (the CRUD CLI does this automatically).
- **Never delete data without explicit user confirmation.**

## Output formatting

Render application lists as a table:

| Company | Role | Status | Priority | Days since update |
|---------|------|--------|----------|-------------------|

Use status emoji/labels from `references/status-config.md`
(⚪ Saved, 🔵 Applied, 🟣 Phone Screen, 🟦 Technical, 🟠 Onsite, 🟢 Offer,
✅ Accepted, 🔴 Rejected, 🚫 Declined, 👻 Ghosted).

## Dashboard / analytics

When asked for a dashboard or stats, compute from the data:
total applications, active pipeline count, offers, response rate %
(non-Saved that got any reply ÷ applied), interviews in next 14 days,
avg response time (days), ghosted rate %, interview conversion %,
top source, pipeline counts by stage, upcoming interviews (14-day),
overdue tasks, and 5 most-recently-updated applications.

## First run

If `data/applications.json` is missing or empty, offer to run `crud.js seed`
to load demo data, or to import a CSV (see the `integrations` skill).
