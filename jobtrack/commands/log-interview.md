---
description: Log or update an interview round for an application.
allowed-tools: Read, Bash
---

# Log Interview

From `$ARGUMENTS`, identify the application (by company/role) and the round
details. Required: `application_id` and `round_type` (validate against the enum
in `references/data-model.md`). Optional: scheduled_at, duration_minutes,
interviewer_name, status (default Scheduled), outcome, prep_notes.

Create the round (round_number auto-increments per application):

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js add interviews '<json>'
```

To update an existing round, use `crud.js update interviews <id> '<patch>'`.

After logging a scheduled interview, offer to sync it to Google Calendar
(see the `integrations` skill) and to add prep-checklist items.
