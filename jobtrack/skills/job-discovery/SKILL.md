---
name: job-discovery
description: Find matching job openings across LinkedIn, AllJobs, Drushim, Indeed, and target company career pages — ranked by relevance against your candidate profile. Triggers on find jobs, discover jobs, job search, what jobs match my profile, search for openings, find me a job, scan job boards.
allowed-tools: Read, Bash, WebSearch, WebFetch, Task
effort: high
context: fork
---

# Job Discovery

Find open roles that match the candidate profile across Israeli and global job boards.

## Step 0 — Load and validate profile

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js show
```

Required fields: `preferences.target_roles` (at least one), `preferences.locations` or `preferences.remote_type`.

If `target_roles` is empty, stop:
> "Add target roles to your profile first: `/jobtrack:setup` → Step 4, or run:
> `node candidate-profile.js set '{\"preferences\":{\"target_roles\":[\"Staff Engineer\"]}}'`"

## Step 1 — Build search queries

For each `target_role` (max 3 to avoid too many searches), build one query per source:

**LinkedIn Jobs:**
```
site:linkedin.com/jobs "{role}" ("Israel" OR "Tel Aviv" OR "Remote") -intern
```

**AllJobs (Israeli):**
```
site:alljobs.co.il "{role}"
```

**Drushim (Israeli):**
```
site:drushim.co.il "{role}"
```

**Indeed Israel:**
```
site:il.indeed.com "{role}"
```

**Target company career pages** (for each company in `preferences.target_companies`):
```
site:{company-domain}.com/careers OR site:{company-domain}.com/jobs "{role}"
```

Also add a general Israeli tech search:
```
"{role}" Israel "apply" 2025 OR 2026 -"we are looking" -agency
```

## Step 2 — Spawn job-discoverer agent

Issue a single Task call with all queries:

```
Task: job-discoverer
Input: {
  "search_queries": [
    {"query": "site:linkedin.com/jobs \"Staff Engineer\" \"Israel\" OR \"Tel Aviv\"", "source_label": "LinkedIn"},
    {"query": "site:alljobs.co.il \"Staff Engineer\"", "source_label": "AllJobs"},
    {"query": "site:drushim.co.il \"Staff Engineer\"", "source_label": "Drushim"},
    {"query": "site:il.indeed.com \"Staff Engineer\"", "source_label": "Indeed"}
  ],
  "profile_filters": {
    "exclude_companies": ["..."],
    "deal_breakers": ["..."],
    "floor_ils": 38000,
    "remote_type": "Hybrid",
    "target_roles": ["Staff Engineer", "Senior Backend Engineer"],
    "locations": ["Tel Aviv", "Israel"]
  }
}
```

## Step 3 — Display ranked shortlist

Present results as a ranked table:

```
# Discovered Jobs — {date}
Profile: {target_roles} | {remote_type} | Floor: ₪{floor_ils}/mo

| # | Company        | Role                    | Source   | Relevance | Salary hint        | Posted   |
|---|----------------|-------------------------|----------|-----------|--------------------|----------|
| 1 | Monday.com     | Staff Software Engineer | LinkedIn | 91/100    | ₪55–70k/mo         | 3 days ago |
| 2 | Wix            | Platform Engineering Lead| AllJobs | 87/100    | Not listed         | 1 week ago |
| 3 | Fiverr         | Senior Backend Engineer | Drushim  | 74/100    | ₪40–55k/mo         | 2 days ago |

Found {N} matching roles across {sources}. Showing top {shown}.
Already in pipeline: {M} of these URLs were skipped (already tracked).
```

If a deal_breaker fired on any result, note: "Filtered out: {company} — matched deal breaker '{rule}'"

## Step 4 — Offer actions

For each result, offer:
- **"Add selected to pipeline"** — user specifies which numbers (e.g. "add 1, 3")
  ```bash
  node ${CLAUDE_PLUGIN_ROOT}/scripts/save-discovered-jobs.js '<json of selected>'
  ```
- **"Add all top-5"**
- **"Deep scan #N"** → `/jobtrack:scan <url>` on the selected job
- **"Get brief for #N"** → `/jobtrack:brief <url>`
- **"Skip all"** — no action

After saving, confirm:
> "Added 2 jobs to your pipeline. Run `/jobtrack:scan` to score them, or `/jobtrack:pipeline` to see the board."
