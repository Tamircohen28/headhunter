---
description: Show the Kanban pipeline with counts per stage.
allowed-tools: Read, Bash
---

# Pipeline

Read the applications and render the Kanban board with per-stage counts in
PIPELINE order, plus terminal buckets below. Follow the `pipeline` skill.

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list applications
```

Show all 7 active stages (Saved → Accepted) with counts even when empty, and
list `Company — Role` cards under each. If `$ARGUMENTS` names a filter (e.g.
priority or remote_type), apply it.
