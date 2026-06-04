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

## Pre-assessment (ask first — 4 questions, one message)

Before generating any prep brief, ask the user:

1. **Which topics feel strongest?** (e.g. "system design, Go concurrency, behavioral storytelling")
2. **Which feel weakest or most uncertain?** (e.g. "dynamic programming, salary negotiation, conflict stories")
3. **What do you most want to focus on?** (drilling weak spots / confirming strong areas / full simulation)
4. **Round type?** — Recruiter / Technical / System Design / Behavioral / Onsite / Final

Use the answers to weight the prep brief:
- Weak area mentioned → make it the **first and most detailed** section, with extra depth
- Strong area mentioned → include it briefly, skip basics
- "Full simulation" → hand off to `/headhunter:mock` instead

If the user is in a hurry ("just give me the brief"), skip the pre-assessment and use defaults (cover all areas, medium depth).

## Prep brief

When asked to prep for an interview, generate:

- **Company research prompts** — products, recent news, tech stack, culture.
- **STAR stories** — 3–5 from the user's background mapped to likely competencies.
- **Questions to ask** the interviewer.
- **Round-specific focus** based on `round_type` (e.g. Technical → DS&A +
  system design; Behavioral → leadership/conflict stories).

## Deep research (HeadHunter pipeline)

For a thorough study plan, hand off to the **interview-research** skill
(`/headhunter:research`), which scrapes the posting, web-researches the company,
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

If `research_dir` is set but neither study guide file exists, say so and
offer to run `/headhunter:research` to generate it.

## Link to Insights

If the application has ≥1 completed interview round (`status: Completed`),
recommend running the `interview-analyst` agent / Insights analysis to fold in
past performance (strengths, weaknesses, predicted next-round topics).

## Link to Mock Interview

After generating the prep brief, always offer:
> "Ready to practice? Run `/headhunter:mock <company>` for a live mock session — the interviewer will ask you questions based on this prep brief and give real-time feedback."
