---
name: interview-prep
description: Prepare for upcoming interviews — list interviews in the next 14 days, manage prep checklists, generate prep briefs and mock questions. Triggers on interview prep, upcoming interview, prep checklist, mock interview, prepare for interview.
allowed-tools: Read, Bash, Grep, Glob
disallowed-tools: Write, Edit
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
application's `research_dir`.

**If `research_dir` is already set on the application**, fold the study guide
into the prep brief:

1. Read `<research_dir>/04_study_guide.md`.
2. Extract from it:
   - **Ordered study topics** — show the top 5 topics the guide recommends
     focusing on first (prerequisites before advanced).
   - **Interview cheat-sheet** — pull the "top technical question patterns"
     and "behavioral questions" sections verbatim.
   - **Prep tips and pitfalls** — include the guide's "preparation tips" and
     "common pitfalls" sections.
   - **Questions to ask** — lift the "questions to ask" section.
3. Present all of this as part of the prep brief under the heading
   **"From your study guide"**, clearly labelled so the user knows it came
   from the research pipeline.
4. Tell the user: "Study guide from `<research_dir>` (researched <last_research_at>)."

If `research_dir` is set but `04_study_guide.md` doesn't exist yet, say so and
offer to run `/jobtrack:research` to generate it.

## Link to Insights

If the application has ≥1 completed interview round (`status: Completed`),
recommend running the `interview-analyst` agent / Insights analysis to fold in
past performance (strengths, weaknesses, predicted next-round topics).
