---
name: jobtrack:search
description: Search and filter job applications by company, role, status, location, source, priority, or any field. Triggers on search, find application, filter jobs, show remote jobs, find by company, filter by status.
allowed-tools: Read, Bash, Grep
---

# JobTrack Search

Find applications matching a query. Display matches as a table; offer to take actions on results.

## Search strategy

Load `data/applications.json` and filter in-memory across all text fields. The search term is case-insensitive and matches substrings.

**Fields searched by default:** company, role, location, source, job_url, job_description, notes (from `data/notes.json`).

**Structured filters** (apply when the user specifies them):
- `status:<stage>` — e.g. `status:Applied`
- `priority:<level>` — High / Medium / Low
- `remote:<type>` — Remote / Hybrid / On-site
- `salary:>N` or `salary:<N` — filter by `salary_min`/`salary_max`
- `has:offer` — applications with a salary range set
- `stale` — not updated in 7+ days in ACTIVE_STAGES

Multiple filters combine with AND.

## Examples

```
/jobtrack:search stripe
/jobtrack:search "senior engineer" status:Technical
/jobtrack:search remote priority:High
/jobtrack:search stale
/jobtrack:search has:offer
```

## Output

Render matches as a table:

| Company | Role | Status | Priority | Location | Days since update |
|---------|------|--------|----------|----------|-------------------|

Show match count: "Found N application(s) matching '<query>'."

If no matches: "No applications match '<query>'. Try a broader term or different filter."

## Offer actions on results

After listing results:
- "Move <company> to a different stage?" → use `/jobtrack:pipeline`
- "View details for <company>?" → use `crud.js get applications <id>`
- "Add a task for <company>?" → use `/jobtrack:add-task`
