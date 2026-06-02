---
name: interview-research
description: Run the job4u interview-prep research pipeline natively — scrape a job posting, analyze + web-research it, divide topics across parallel research subagents, and merge into a study guide attached to a job application. Triggers on research this job, prep pipeline, study guide, deep research interview, analyze job posting, job4u pipeline.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
effort: high
---

# Interview-Research Pipeline

This is the native Claude Code port of the job4u Python pipeline — no Python,
no OpenAI. You orchestrate it by spawning subagents (the "divide topics among
agents" pattern the Python `TaskExecutor` used) and persist results into the
jobtrack store. Read `references/pipeline.md` for the full stage map and the
JobMetadata schema before starting.

## Resolve the target application

The user gives a job URL, a pasted description, or names an existing
application. Tie every run to a `JobApplication`:

- If they name/select an existing app, use its `id`.
- If it's a new URL, create one first (company/role can be filled after Stage 2):
  ```bash
  node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js add applications '{"company":"(pending)","role":"(pending)","job_url":"<url>","status":"Saved"}'
  ```
  Use the returned `id` as `<appId>`.

Research lives under `${CLAUDE_PLUGIN_ROOT}/data/research/<appId>/`. Create it
with `mkdir -p`.

## Stage 1 — Scrape

`WebFetch` the `job_url` and extract the posting text (or use pasted text).
Write it to `data/research/<appId>/01_job_description.md`. If fetch fails, ask
the user to paste the description.

## Stage 2 — Analyze + research (subagent: job-analyzer)

Spawn the **job-analyzer** subagent via the Task tool, passing the description
text, the URL, and output path `data/research/<appId>/02_job_metadata.json`.
After it returns, update the application with the real company/role:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js update applications <appId> '{"company":"...","role":"..."}'
```

## Stage 3 — Divide & research topics (subagent: topic-researcher, in PARALLEL)

1. Read `02_job_metadata.json`. Take `topic_hierarchy` main topics in
   `topic_learning_order`.
2. Split them into batches of `maxTopicsPerAgent` (default 4 — read from
   `settings.json`). N = ceil(topics / 4).
3. Spawn **N topic-researcher subagents in parallel** — issue all Task calls in
   a single message. Give each agent its topic batch (main topics + sub-topics),
   the role/company context, and output path
   `data/research/<appId>/03_topic_<k>.md`.

This is the core of the pipeline — fan-out research, exactly like the original
multi-agent step, but using native subagents.

> **Scaling tip (dynamic workflows):** for postings with many topics, this
> fan-out is a natural fit for the workflow system. The user can launch it as a
> dynamic workflow with the `ultracode` keyword (or `/effort xhigh` on Opus 4.8)
> so the topic-researcher agents run as managed background agents; track them
> with `/workflows`. The orchestration below is identical either way.

## Stage 4 — Merge (subagent: study-guide-writer)

Spawn **study-guide-writer**, passing the research dir and study config
(`studyWeeks`, `hoursPerWeek` from settings.json). It writes
`04_study_guide.md`.

## Wire back to the store

Write a run manifest and link it to the application:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js update applications <appId> \
  '{"research_dir":"data/research/<appId>","last_research_at":"<ISO now>"}'
```
Then surface the study guide path to the user and offer to: add prep tasks
(via the `pipeline`/`add-task` flows), log the upcoming interview, or open the
cheat-sheet. The `interview-prep` skill consumes this output for prep briefs.

## Notes

- Prefer running Stage 3 agents concurrently for speed; if topics are few
  (≤4) a single agent is fine.
- Never fabricate research — subagents should mark unknowns rather than invent.
- Re-running creates fresh `0X_*` files in the same dir (overwrites); tell the
  user before overwriting a prior run.
