---
name: headhunter:status
description: Show current notification state mid-session — overdue tasks, upcoming interviews in the next 48h, and stale applications. Triggers on status, notifications, overdue, what's urgent, check status, reminders.
allowed-tools: Read, Bash
---

# HeadHunter Status

A mid-session snapshot of anything requiring the user's attention. Run the session briefing script and augment with stale-application detection.

## Run the briefing

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/session-briefing.js
```

Parse the JSON output and display `additionalContext` formatted as a readable summary.

## Stale applications

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/send-stale-reminders.js --dry-run
```

This prints stale applications (ACTIVE_STAGES not updated in 7+ days). If the output is non-empty, show it as a stale-applications section below the briefing.

## Output format

Present everything as a concise status report:

```
=== HeadHunter Status ===

Pipeline: Saved:3  Applied:2  Technical:1
Overdue tasks (N):
  • <task title> (due <date>)
Interviews in next 48h (N):
  • <round_type> @ <company> — <datetime>
Stale applications (N, 7+ days without update):
  • <company> – <role> (<status>, <N>d stale)
```

If everything is clear (no overdue, no upcoming in 48h, no stale), say: "All clear — no urgent items right now."

## Offer actions

After showing the status, offer:
- "Review stale applications" → `/headhunter:pipeline`
- "See all tasks" → `/headhunter:tasks`
- "View upcoming interviews" → `/headhunter:calendar`
