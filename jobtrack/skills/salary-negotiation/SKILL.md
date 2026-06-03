---
name: salary-negotiation
description: Analyze a job offer and get a specific counter-offer script with market data, levers to pull, and what to say. Triggers on negotiate, salary negotiation, counter offer, they offered me, evaluate offer, is this offer good, what should I ask for.
allowed-tools: Read, Bash, WebSearch, Task
effort: high
---

# Salary Negotiation

Produce a data-driven counter-offer script for a real offer.

## Step 0 — Load profile and offer

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js show
```

If no salary fields are set (`floor_ils` is null), ask the user for their floor and target before proceeding.

**Resolve the offer** from `$ARGUMENTS`:
- If an application ID is provided and its status is `Offer`: load salary fields from the application record (`salary_min`, `salary_max`).
- If the user typed inline (e.g. "they offered me ₪42k base + 10% bonus"): parse it.
- If nothing provided: ask "What did they offer? (base salary, bonus, equity, signing)"

## Step 1 — Pre-research (in-skill, no agent yet)

WebSearch for market data:
```
site:glassdoor.com "{company}" "{role}" salary
site:levels.fyi "{company}"
"{role}" Israel salary 2025 OR 2026
```

Collect 3–5 data points (source, amount, date).

## Step 2 — Spawn salary-negotiator agent

```
Task: salary-negotiator
Input: {
  "offer": {"base_ils": 42000, "bonus_ils": 4200, "equity": "0.05% over 4yr", "signing_ils": 0},
  "candidate_profile": {
    "floor_ils": 38000,
    "target_base_ils": 50000,
    "target_total_ils": 60000,
    "current_base_ils": 35000,
    "years_total": 7,
    "current_title": "Senior Engineer",
    "key_skills": ["Go", "Kubernetes", "gRPC"]
  },
  "role": {"title": "Staff Engineer", "company": "Monday.com"},
  "market_research": "<collected snippets from Step 1>"
}
```

## Step 3 — Present and act

Display the full negotiation brief from the agent.

After presenting, offer:
- "Update the application record with these offer details":
  ```bash
  node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js update applications <id> \
    '{"salary_min":42000,"salary_max":52000,"currency":"ILS"}'
  ```
- "Add a follow-up task: Negotiate offer by [date]" → `/jobtrack:add-task`
- "Get the full company brief first" → `/jobtrack:brief <company>`
