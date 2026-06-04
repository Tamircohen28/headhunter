---
description: Run the interview-prep research pipeline for a job (scrape, analyze, multi-agent research, study guide).
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
---

# Research a Job

Run the `interview-research` pipeline for the job in `$ARGUMENTS` (a job URL, a
pasted description, or the name of an existing application).

Follow the `interview-research` skill end-to-end:
1. Resolve/create the target application.
2. Scrape → 3. job-analyzer subagent (metadata + web research) →
4. fan out topic-researcher subagents in parallel over topic batches →
5. study-guide-writer merges into a study guide.

Use `pipeline-run.js` + `deep-research.js` (see `references/pipeline-output.md`).
Artifacts: `data/research/<slug>/` with `01_job_scraper.md`, `01_job_description.md`,
`02_job_analyzer.md`, `02_job_metadata.json`, `NN-research-prompt.md` / `NN-research-report.md`,
`04_study_guide.md`. `finish` **prints** `04_study_guide.md` path.
