---
name: network-finder
description: Find contacts at a target company, identify warm intro paths, and draft personalized outreach for recruiters, hiring managers, and engineers. Triggers on network, referral, who do I know at, find contacts, reach out, connection at company, warm intro, linkedin outreach.
allowed-tools: Read, Bash, WebSearch, Glob, Task
context: fork
---

# Network & Referral Finder

Map contacts at a target company and draft outreach that gets responses.

## Step 0 — Resolve target company

From `$ARGUMENTS`: company name, app ID, or URL.

If an application ID is given, use the company from that record. Load existing contacts:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list contacts --json
```
Filter to contacts linked to this company's applications.

Also load candidate profile for context (current title, skills, linkedin_url).

## Step 1 — Search for employees

Run targeted WebSearches:

```
site:linkedin.com/in "{company}" "software engineer" OR "engineering manager" OR "recruiter" OR "talent"
"{company}" "engineering manager" OR "tech lead" OR "recruiter" LinkedIn 2025
"{company}" "open to referrals" OR "we're hiring" engineer linkedin
```

If the GitHub MCP is connected, also search:
```
org:{company-github-org} members
```
to find engineers with public profiles.

If the LinkedIn MCP is connected, use it to search for company employees by title.

## Step 2 — Spawn network-researcher agent

```
Task: network-researcher
Input: {
  "company": {"name": "Monday.com", "domain": "monday.com"},
  "target_role": "Staff Engineer",
  "candidate_profile": {
    "current_title": "Senior Engineer",
    "key_skills": ["Go", "Kubernetes"],
    "summary": "...",
    "linkedin_url": "...",
    "github_url": "..."
  },
  "existing_contacts": [...from contacts.json for this company],
  "search_results": "<raw snippets from Step 1 searches>"
}
```

## Step 3 — Present network map

Display the agent's output: existing CRM contacts, recommended new contacts with outreach drafts, warm intro paths, and timing advice.

## Step 4 — Save new contacts

For any contacts the user wants to track:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js add contacts \
  '{"application_id":"<id>","name":"...","role_at_company":"...","email":"...","linkedin_url":"...","notes":"Found via network search"}'
```

Offer:
- "Add a task to send these outreach messages by [date]" → `/jobtrack:add-task`
- "When you hear back, log it as a contact note" → `crud.js update contacts <id>`
