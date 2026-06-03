---
description: Add a new job application to the pipeline.
allowed-tools: Read, Bash
---

# Add Application

Collect the details for a new job application from the user's input
(`$ARGUMENTS`) — at minimum **company** and **role**. Ask for any missing
required fields. Optional: status (default `Saved`), priority (default
`Medium`), job_url, applied_date, source, location, remote_type, salary_min,
salary_max, currency (default `USD`).

Validate enums against `references/status-config.md`, then create it:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js add applications '<json>'
```

Confirm the created record (id + summary) and ask whether to add a follow-up
task or sync to Notion.
