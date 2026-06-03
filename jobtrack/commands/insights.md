---
name: jobtrack:insights
description: Analyze past interview performance for a job application and predict next-round topics. Triggers on insights, interview analysis, predict next round, performance review, strengths weaknesses.
allowed-tools: Read, Bash, Grep, Glob, Task
---

# JobTrack Insights

Run the **interview-analyst** agent against a specific job application to surface strengths, weaknesses, patterns, and a next-round prediction.

## Step 1 — Resolve the target application

The user may give a company name, role, or application ID. Find the application:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list applications --json
```

If the input is ambiguous (multiple matches), list them and ask the user to confirm. Once resolved, extract the `id`.

## Step 2 — Check for interview history

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list interviews --json
```

Filter for rounds where `application_id` matches. If there are **zero** completed rounds (`status: Completed`), tell the user the analysis will rely on role-type predictions only (no personal performance data yet). If there are no rounds at all and no scheduled next round, say so and offer to log an interview first via `/jobtrack:log-interview`.

## Step 3 — Spawn the interview-analyst agent

Use the Task tool to spawn **interview-analyst**, passing:

- The target `application_id`
- Company name and role (for context)
- The list of completed interview rounds (JSON)
- The next scheduled round (if any)

```
Task: interview-analyst
Input: {
  "application_id": "<id>",
  "company": "<company>",
  "role": "<role>",
  "completed_rounds": [ ... ],
  "next_round": { ... } or null
}
```

## Step 4 — Present the results

Surface the agent's output in two sections:

### Performance Analysis
Show the JSON block (strengths, weaknesses, patterns, top_recommendations, overall_performance) formatted as a readable summary — not raw JSON.

### Next-Round Predictor
Show predicted topics, likely questions, technical study areas, and behavioral themes as a structured prep list.

## Step 5 — Offer follow-up actions

- "Add prep tasks for these topics?" → use `/jobtrack:add-task`
- "Update prep notes on the scheduled round?" → use `crud.js update interviews <id>`
- "Run the full research pipeline?" → suggest `/jobtrack:research`
