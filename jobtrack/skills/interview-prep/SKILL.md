---
name: interview-prep
description: Prepare for upcoming interviews — list interviews in the next 14 days, manage prep checklists, generate prep briefs and mock questions. Triggers on interview prep, upcoming interview, prep checklist, mock interview, prepare for interview.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Interview Prep

## Upcoming interviews

Read `data/interviews.json` + `data/applications.json`. Show interviews with
`status: Scheduled` and `scheduled_at` within the next 14 days, sorted by date:

| Date | Company | Role | Round type | Interviewer | Prep done |
|------|---------|------|-----------|-------------|-----------|

## Prep checklist CRUD

Each interview has `prep_checklist: [{id, text, done}]`. To add/toggle/delete
an item, update the interview record:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js update interviews int_002 \
  '{"prep_checklist":[{"id":"c1","text":"Review system design","done":true}]}'
```

Read the existing checklist first, modify the array, then write it back whole.

## Prep brief

When asked to prep for an interview, generate:

- **Company research prompts** — products, recent news, tech stack, culture.
- **STAR stories** — 3–5 from the user's background mapped to likely competencies.
- **Questions to ask** the interviewer.
- **Round-specific focus** based on `round_type` (e.g. Technical → DS&A +
  system design; Behavioral → leadership/conflict stories).

## Deep research (job4u pipeline)

For a thorough study plan, hand off to the **interview-research** skill
(`/jobtrack:research`), which scrapes the posting, web-researches the company,
fans research across parallel subagents, and writes a study guide to the
application's `research_dir`. If `research_dir` is already set on the app, read
`04_study_guide.md` there and fold it into the prep brief instead of
re-researching.

## Link to Insights

If the application has ≥1 completed interview round (`status: Completed`),
recommend running the `interview-analyst` agent / Insights analysis to fold in
past performance (strengths, weaknesses, predicted next-round topics).
