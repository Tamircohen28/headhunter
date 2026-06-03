---
description: Find matching job openings across LinkedIn, AllJobs, Drushim, Indeed, and target company career pages. Ranked by relevance against your profile. Optional: pass a role or company to narrow the search.
allowed-tools: Read, Bash, WebSearch, WebFetch, Task
---

# Discover Jobs

Run the `job-discovery` skill.

`$ARGUMENTS` may be:
- Empty — search all target_roles from your profile
- A role override (e.g. "Staff Engineer") — search only this role
- A company name (e.g. "Monday") — search only this company's career page

Follow the `job-discovery` skill end-to-end:
1. Load profile — exit if no target_roles configured.
2. Build search queries per role × source (LinkedIn, AllJobs, Drushim, Indeed, target companies).
3. Spawn job-discoverer agent to search, filter, and score all results.
4. Display ranked shortlist table.
5. Save selected jobs to pipeline via `save-discovered-jobs.js`.
