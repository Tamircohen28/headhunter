---
name: job-scanner
description: Scan a job posting and get a brutally honest Match Score + Success Score against your candidate profile. Triggers on scan job, score this job, match score, success score, should I apply, how good is my fit, evaluate this role.
allowed-tools: Read, Bash, WebFetch, WebSearch, Glob, Task
effort: high
context: fork
---

# Job Scanner

Evaluate a job posting against the candidate's profile and produce honest scores.

## Step 0 — Load candidate profile

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js show
```

If the profile is missing or empty (no `experience.key_skills`), tell the user to run `/jobtrack:setup` first. A scan without a profile produces meaningless scores.

## Step 1 — Resolve input

`$ARGUMENTS` may be: a URL, pasted job description text, an existing application ID, or "company + title".

- **URL**: `WebFetch` it and extract the job posting body.
- **App ID**: load from `crud.js get applications <id>` and use `job_url` / `job_description`.
- **Text / company + title**: proceed with what's given.

## Step 2 — Run job-analyzer (get structured metadata)

If not already analyzed, spawn the **job-analyzer** subagent:

```
Task: job-analyzer
Input: {
  "job_url": "<url or null>",
  "description_text": "<extracted text>",
  "output_path": "data/scan-tmp/meta-<timestamp>.json"
}
```

Read the output JSON after it completes. This gives `required_skills`, `preferred_skills`, `hiring_stages`, `topic_hierarchy`, etc.

If there's an existing application with `research_dir`, read `research_dir/02_job_metadata.json` instead of re-running.

## Step 3 — Run deterministic pre-score

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/score-job.js data/scan-tmp/meta-<timestamp>.json
```

This gives the skill-overlap count, salary check, and remote match — anchors the agent.

## Step 4 — Gather company selectivity signal

Do a **focused** company intel pull (Section 1 of `interview-brief` only — skip the full 6-section report):
- WebSearch: `"{company}" engineer interview difficulty glassdoor`
- WebSearch: `"{company}" "software engineer" acceptance rate OR "offer rate"`
- WebSearch: hiring news (layoffs, freeze, growth) for the company in last 6 months

## Step 5 — Spawn job-scorer agent

```
Task: job-scorer
Input: {
  "job_metadata": <contents of meta JSON>,
  "pre_score": <pre-score JSON from step 3>,
  "candidate_profile": <profile JSON>,
  "company_intel": "<summary from step 4>"
}
```

## Step 6 — Present the scanner report

Format the output clearly:

```
╔══════════════════════════════════════════╗
║  JOB SCAN: {Role} @ {Company}            ║
╠══════════════════════════════════════════╣
║  Match Score:    72/100  ████████░░       ║
║  Success Score:  31/100  ███░░░░░░░  [Medium confidence] ║
║  Verdict:        LONG SHOT               ║
╚══════════════════════════════════════════╝

### Match Breakdown
Skills:          28/35  (matched 7/10 required — missing: Rust, eBPF)
Experience:      18/25  (7 yrs vs senior requirement ✓)
Location/Remote: 12/20  (hybrid role, you prefer remote)
Salary:          14/20  (band ₪45–60k, your target ₪42k — good overlap)

### Success Breakdown
Qualification fit:     14/35  (meets 70% of hard requirements)
Company selectivity:    7/20  (Tier 2 — 5–15% hire rate)
Competition:            5/20  (hot ML role, high applicant volume)
Your differentiators:   4/15  (distributed systems experience relevant)
Market timing:          1/10  (company in hiring slowdown)

### Top Strengths
• Kubernetes + Go directly match 3 core requirements
• 7 years experience matches seniority level

### Top Gaps (with bridge strategies)
• Rust (required) — bridge: emphasize C++ systems experience, mention willingness to ramp
• eBPF (preferred) — bridge: mention kernel-level work at current company

### Salary Signal
Estimated band: ₪45,000–₪60,000/month gross. Above your target — good signal.

### Recommendation
Apply only if you can invest 3+ hours tailoring. Run /jobtrack:apply to generate a
tailored CV. Address the Rust gap directly in your cover letter.
```

## Step 7 — Save and offer next steps

If the input was an existing application, save scores:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js update applications <id> \
  '{"match_score":72,"success_score":31,"scanner_notes":"Long Shot — missing Rust/eBPF, Tier 2 company"}'
```

If this was a new URL/text, offer to create an application record:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js add applications \
  '{"company":"...","role":"...","job_url":"...","match_score":72,"success_score":31}'
```

After the report, always offer:
- **"Generate tailored CV + cover letter"** → `/jobtrack:apply`
- **"Get the full company briefing"** → `/jobtrack:brief`
- **"Start interview research pipeline"** → `/jobtrack:research`
- **"Skip — not worth the effort"** → user decides
