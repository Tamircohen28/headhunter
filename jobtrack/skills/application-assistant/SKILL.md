---
name: application-assistant
description: Generate a tailored CV and cover letter for a specific job application, and answer any application form questions. Triggers on apply, tailor my CV, cover letter, application form, submit application, write cover letter, customize resume.
allowed-tools: Read, Write, Bash, Glob, Task
effort: high
context: fork
---

# Application Assistant

Help the candidate submit a strong, tailored application for a specific role.

## Detect mode

**Mode A** (default) — "Generate tailored CV + cover letter": triggered by `/jobtrack:apply` or when the user asks to prepare an application.

**Mode B** — "Q&A advisor": triggered when the user asks "how do I answer X?" or "what should I write for Y field?" — answer immediately in context without spawning agents.

---

## Mode A — Tailored CV + Cover Letter

### Step 0 — Load context

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js show
```

If no profile or no `cv.text`, tell user to run `/jobtrack:setup` and upload their CV first.

Resolve the application: `$ARGUMENTS` may be an app ID, company name, or URL.

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js get applications <id>
# or search for it
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list applications --json
```

Load job metadata if available (from `research_dir/02_job_metadata.json`), or use the application's `job_description` field.

Load scanner results if available (`match_score`, `success_score`, `scanner_notes` on the application record).

### Step 1 — Spawn agents in parallel

Issue both Task calls in a single message:

```
Task 1: cv-tailor
Input: {
  "cv_text": "<profile.cv.text>",
  "job_metadata": <metadata or summary>,
  "candidate_profile": <profile>,
  "top_strengths": ["<from scanner or inferred>"],
  "top_gaps": ["<from scanner or inferred>"],
  "output_note": "Write the tailored CV to data/cvs/tailored-<appId>.md"
}

Task 2: cover-letter-writer
Input: {
  "candidate_profile": <profile summary>,
  "job_metadata": <metadata>,
  "company_intel": "<brief company summary>",
  "top_strengths": ["..."],
  "top_gaps": ["..."],
  "output_note": "Write the cover letter to data/cvs/cover-letter-<appId>.md"
}
```

### Step 2 — Save outputs

After agents return, write their outputs to disk:

```bash
# Save tailored CV markdown
# (Write tool): data/cvs/tailored-<appId>.md  ← agent output

# Generate HTML
node ${CLAUDE_PLUGIN_ROOT}/scripts/generate-cv-html.js \
  --input ${CLAUDE_PLUGIN_ROOT}/data/cvs/tailored-<appId>.md \
  --out ${CLAUDE_PLUGIN_ROOT}/data/cvs/tailored-<appId>.html

# Save cover letter
# (Write tool): data/cvs/cover-letter-<appId>.md  ← agent output
```

Update application record:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js update applications <id> \
  '{"tailored_cv_path":"data/cvs/tailored-<appId>.html","cover_letter_path":"data/cvs/cover-letter-<appId>.md"}'
```

### Step 3 — Present results

Show a summary:

```
✓ Tailored CV saved: data/cvs/tailored-<appId>.html
  → Open in browser → Cmd+P → Save as PDF

✓ Cover letter saved: data/cvs/cover-letter-<appId>.md

CV changes made:
  • Added targeted summary for {role} at {company}
  • Reordered bullets in {company} role to lead with {skill}
  • Removed: {irrelevant section}

Cover letter:
  Subject: {Role} Application — {Name}
  [show first paragraph preview]

Gaps addressed:
  • {gap}: bridged via {strategy}

Remaining gaps (acknowledge in interview if asked):
  • {gap}
```

### Step 4 — Application checklist

Present a checklist before submitting:

- [ ] Read the HTML CV in browser — does it format correctly?
- [ ] Update the cover letter greeting if you know the hiring manager's name
- [ ] Check: does the CV accurately reflect your experience? (cv-tailor never invents, but review)
- [ ] Run `/jobtrack:brief <company>` if you haven't done full company research
- [ ] Add a task: "Follow up in 7 days" → `/jobtrack:add-task`

---

## Mode B — Application Form Q&A

When the user asks "how should I answer [specific question]":

1. Read the question carefully. Identify what the employer is really asking.
2. Use the candidate profile + job context to give a specific, honest answer.
3. Draft a 2–4 sentence response the user can adapt.
4. Flag if the question is a potential red flag for this candidate (e.g. "Do you have 5+ years of X?" when they have 3).

Common application questions:
- **"Why do you want to work here?"** → Use profile `why_looking` + company-specific fact
- **"Where do you see yourself in 5 years?"** → Use `career_goal_3yr`
- **"What's your salary expectation?"** → Use `salary.target_base_ils` + the brief's salary script
- **"Why are you leaving your current role?"** → Use `preferences.why_looking` — be honest but positive
- **"What's your notice period?"** → Use `availability.notice_period_days`
