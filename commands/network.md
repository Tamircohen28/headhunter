---
description: Find contacts at a target company, identify warm intro paths, and draft personalized outreach for recruiters, hiring managers, and engineers. Pass a company name or application ID.
allowed-tools: Read, Bash, WebSearch, Glob, Task
---

# Network & Referral Finder

Run the `network-finder` skill for the company in `$ARGUMENTS`.

Follow the `network-finder` skill end-to-end:
1. Resolve company; load existing contacts from CRM.
2. Search for employees via WebSearch (+ LinkedIn/GitHub MCPs if connected).
3. Spawn network-researcher agent → ranked contacts + personalized outreach drafts.
4. Present network map with warm intro paths and timing advice.
5. Save selected contacts to CRM; offer follow-up tasks.
