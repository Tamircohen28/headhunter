---
description: Sync applications/tasks to external tools (Notion, Todoist) and send reminders (WhatsApp).
allowed-tools: Read, Bash
---

# Sync

Run integration syncs. Always preview with `--dry-run` first, confirm with the
user, then run for real. Check the relevant env vars are set (see README §env).

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-notion.js   --dry-run   # applications → Notion
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-todoist.js  --dry-run   # tasks → Todoist
node ${CLAUDE_PLUGIN_ROOT}/scripts/sync-twilio.js   --dry-run   # WhatsApp reminder digest
```

`$ARGUMENTS` selects the target (`notion`, `todoist`, `whatsapp`, or `all`).
Syncs are idempotent (reuse stored `notion_page_id` / `todoist_task_id`). For
Google Calendar/Tasks, use the connected MCP server per the `integrations` skill.
