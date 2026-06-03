---
description: List tasks across all applications, filterable by overdue/today/upcoming/completed.
allowed-tools: Read, Bash
---

# Tasks

List all tasks (section 5.6). Read them and filter per `$ARGUMENTS`
(`overdue`, `today`, `upcoming`, `completed`; default: open tasks):

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list tasks
```

Render as a table: Title | Application | Due | Priority | Done. Flag overdue
items. Offer to complete a task (`crud.js complete-task <id>`) or sync to
Todoist/Notion/Google Tasks (see the `integrations` skill).
