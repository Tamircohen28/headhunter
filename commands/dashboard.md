---
description: Show the HeadHunter dashboard — stats, pipeline, upcoming interviews, overdue tasks.
allowed-tools: Read, Bash
---

# Dashboard

Render the full dashboard (section 5.1 parity):

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.js
```

Present the output cleanly. If `$ARGUMENTS` includes `json`, run with `--json`
and summarize the key metrics (total, active, offers, response rate, interview
conversion, ghosted rate, avg response time, top source).
