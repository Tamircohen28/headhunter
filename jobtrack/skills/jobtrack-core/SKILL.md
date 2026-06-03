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

Use the deterministic dashboard script rather than computing by hand:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.js          # formatted
node ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.js --json    # raw metrics
```

It returns total, active, offers, response rate %, avg response time, ghosted
rate %, interview conversion %, top source, pipeline counts, upcoming
interviews (14d), overdue tasks, and recent applications.

## Other views

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/calendar.js            # interview agenda
node ${CLAUDE_PLUGIN_ROOT}/scripts/timeline.js <appId>    # per-application timeline
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js events <appId> # raw event log
```

## Offer comparison

When the user asks to compare offers or salary ranges, read `data/applications.json`
and filter for applications with `salary_min` or `salary_max` set (or `status: Offer`).
Render a side-by-side table:

| Company | Role | Status | Currency | Min | Max | Mid | Benefits / Notes |
|---------|------|--------|----------|-----|-----|-----|-----------------|

- **Mid** = (salary_min + salary_max) / 2, or salary_min if only one is set.
- **Benefits / Notes** — pull from any note with `note_type: "Offer Details"` linked to that application.
- Sort by Mid salary descending.
- If currencies differ, flag it and do NOT convert (show each in its own currency).
- After the table, highlight the highest-paying offer and note any with equity or
  benefits mentioned in notes.

## Search and filter

When the user asks to find or filter applications:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list applications --json
```

Load the JSON and filter in-memory. Support these patterns:
- By company or role substring (case-insensitive)
- By status: `status:<Stage>`
- By priority: `priority:High|Medium|Low`
- By remote type: `remote:Remote|Hybrid|On-site`
- Stale: not updated in 7+ days in ACTIVE_STAGES (Applied, Phone Screen, Technical, Onsite, Offer)
- Has offer range: `salary_min` or `salary_max` present

For search, also see `/jobtrack:search` for a dedicated search command.

Status changes, additions, and completions are auto-logged to `events.json`,
which powers the timeline (Application-detail Timeline tab parity).

## First run

If `data/applications.json` is missing or empty, offer to run `crud.js seed`
to load demo data, or to import a CSV (see the `integrations` skill).
