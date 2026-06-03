---
name: pipeline
description: View and manage the Kanban job pipeline — list stage columns with counts and move applications between stages. Triggers on move application, kanban, pipeline, pipeline stage, update status, advance application.
allowed-tools: Read, Bash, Grep, Glob
disallowed-tools: Write, Edit
---

# Pipeline (Kanban)

## List the board

Read `data/applications.json` and render an ASCII Kanban with counts per stage,
in PIPELINE order (see `references/status-config.md`):

```
Saved (n) | Applied (n) | Phone Screen (n) | Technical (n) | Onsite (n) | Offer (n) | Accepted (n)
```

Show terminal buckets (Rejected/Declined/Ghosted) separately below. Under each
column list `Company — Role` (priority badge). Support filters by `priority`
and `remote_type` when the user asks.

Each card line should show: company, role, priority badge, interview count
(from `interviews.json`), and contacts count (from `contacts.json`).

## Move an application

For "move {company} to {stage}":

1. Find the application by company (and role if ambiguous — ask).
2. Validate the target stage is a real enum value.
3. Run:
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js move <appId> "<Stage>"
   ```
   This enforces forward-only progression (terminal statuses exempt). If it
   refuses a backward move, tell the user and ask whether it's a correction.
4. After moving to **Applied** or any interview stage, proactively suggest a
   follow-up task (e.g. "Add a task: follow up in 7 days?") and offer to create
   it via the `crud.js add tasks` command.
