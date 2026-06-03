---
description: Show scheduled interviews as a calendar/agenda.
allowed-tools: Read, Bash
---

# Calendar

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/calendar.js
```

If `$ARGUMENTS` names a month (`YYYY-MM`), pass `--month`. Offer to open an
application's detail or sync an interview to Google Calendar (see `integrations`).
