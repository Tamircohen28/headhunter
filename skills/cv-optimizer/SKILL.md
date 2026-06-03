---
name: cv-optimizer
description: Review your CV and LinkedIn profile against target roles — ATS score, missing keywords, bullet improvements, and LinkedIn optimization. Triggers on review my CV, CV feedback, improve my resume, LinkedIn audit, ATS score, keyword gaps, CV optimization.
allowed-tools: Read, Bash, Glob, Task
effort: high
context: fork
---

# CV + LinkedIn Optimizer

Give the candidate honest, actionable improvements to their CV and LinkedIn profile.

## Step 0 — Load profile

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js show
```

Required fields: `cv.text`, `experience.target_roles` (or `preferences.target_roles`), `experience.key_skills`.

If `cv.text` is empty, ask the user to either:
- Paste their CV text (then save via `candidate-profile.js set '{"cv":{"text":"..."}}'`)
- Provide a file path (then run `candidate-profile.js extract-cv <file>`)
- Run `/headhunter:setup` first

## Step 1 — Check LinkedIn connectivity

If the LinkedIn MCP is connected (check by attempting a small fetch), fetch the candidate's own profile. Otherwise, ask: "Do you want to paste your LinkedIn 'About' section and headline for an audit?" — LinkedIn audit is optional.

## Step 2 — Spawn agents in parallel

Issue both Task calls in a single message:

```
Task 1: cv-reviewer
Input: {
  "cv_text": "<profile.cv.text>",
  "target_roles": <profile.preferences.target_roles>,
  "key_skills": <profile.experience.key_skills>,
  "industry": "<infer from current company or target roles>"
}

Task 2: linkedin-auditor   (only if LinkedIn content is available)
Input: {
  "profile_text": "<LinkedIn profile text>",
  "target_roles": <profile.preferences.target_roles>,
  "cv_text": "<profile.cv.text>",
  "industry": "<industry>"
}
```

If no LinkedIn content is available, run only Task 1.

## Step 3 — Present combined report

Display the cv-reviewer output in full, then the linkedin-auditor output.

After both sections, show a **Combined Priority List** — the top 5 actions across both tools that will have the most impact:

```
## Combined Priority Actions

1. [Highest impact item — usually ATS keywords or bullet quantification]
2. ...
5. ...

→ Apply CV changes: run /headhunter:apply to generate a tailored version for a specific role
→ Review again after changes: re-run /headhunter:cv-review
```

## Step 4 — Offer to save as a note

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js add notes \
  '{"application_id":null,"content":"CV Review <date>: ATS XX/100. Key actions: ...","note_type":"General"}'
```

(No application_id since this is a general CV review, not role-specific.)
