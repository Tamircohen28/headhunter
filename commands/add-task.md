---
description: Create a task, optionally linked to an application.
allowed-tools: Read, Bash
---

# Add Task

From `$ARGUMENTS`, gather a task `title` (required) and optional description,
due_date, priority (High/Medium/Low), and `application_id` to link it to an
application.

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js add tasks '<json>'
```

Confirm the created task. If a Todoist/Google Tasks/Notion integration is
connected, offer to sync it (see the `integrations` skill).
