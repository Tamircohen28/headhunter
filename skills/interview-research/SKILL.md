---
name: interview-research
description: Run the HeadHunter interview-prep research pipeline — scrape, analyze, OpenAI Deep Research per topic batch, merge study guide. Triggers on research this job, prep pipeline, study guide, deep research interview, analyze job posting, headhunter research.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
effort: high
context: fork
---

# Interview-Research Pipeline

Persist everything under **`data/research/<slug>/`** (human-readable slug, not `app_*`).
Read `references/pipeline.md`, `references/pipeline-output.md`, `references/deep-research-template.md`.

## 0 — Application + research directory

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js add applications '{"company":"(pending)","role":"(pending)","job_url":"<url>","status":"Saved","research_status":"in_progress"}'

node ${CLAUDE_PLUGIN_ROOT}/scripts/pipeline-run.js init \
  --app <appId> \
  --slug "<company-role-slug>" \
  --url "<job_url>" \
  --company "<company>" \
  --role "<role>"
```

Use `research_dir` from JSON stdout (e.g. `data/research/nvidia-senior-ai-llm-solutions`).

## Stage 1 — Scrape

1. **Write the full scrape prompt** (WebFetch URL, fallbacks, upload paths):

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/pipeline-run.js write \
  --dir <research_dir> --file 01_job_scraper.md --text "<FULL PROMPT>"
```

2. Perform scrape; **write output**:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/pipeline-run.js write \
  --dir <research_dir> --file 01_job_description.md --text "<extracted JD markdown>"
```

## Stage 2 — Analyze (job-analyzer subagent)

1. **Write the full Task prompt** to `02_job_analyzer.md` (include JD path, output path, research instructions).

2. Spawn **job-analyzer**; it must write `02_job_metadata.json` in `<research_dir>/`.

3. Update application company/role from metadata.

## Stage 3 — Deep Research per topic batch (OpenAI)

**Do not use topic-researcher subagents for new runs.** Use OpenAI Deep Research API.

1. Read `02_job_metadata.json` → split `topic_learning_order` into batches of `maxTopicsPerAgent` (default 4).

2. For each batch, create prompt file:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/pipeline-run.js batch \
  --dir <research_dir> \
  --topics '["Topic A","Topic B","Topic C","Topic D"]'
```

This writes `03-research-prompt.md`, then `04-research-prompt.md`, etc.

3. Run Deep Research (requires `OPENAI_API_KEY`):

```bash
export OPENAI_API_KEY="..."
# optional: export OPENAI_DEEP_RESEARCH_MODEL=o3-deep-research

# Recommended: PDF per batch (API returns markdown only; --pdf uses code_interpreter)
node ${CLAUDE_PLUGIN_ROOT}/scripts/deep-research.js --dir <research_dir> --batch 03 --pdf
node ${CLAUDE_PLUGIN_ROOT}/scripts/deep-research.js --dir <research_dir> --batch 04 --pdf
```

Use `--dry-run` to test without API spend. Batches may run in parallel terminals.

Outputs per batch: `03-research-report.md` + `03-research-report.pdf` (with `--pdf`).

## Stage 4 — Merge (study-guide-writer)

1. Write full merge prompt to `{NN}-study-guide-prompt.md` where NN = last research batch number + 1.

2. Spawn **study-guide-writer** → output **`04_study_guide.md`** in `<research_dir>/`.

## Stage 5 — Full guide + PDF

**Preferred (API PDFs):** merge batch PDFs only — no markdown→PDF conversion.

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/merge-research-pdfs.js --dir <research_dir>
```

**Fallback (markdown merge + Chrome print):** if batches have `.md` only:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/merge-research-full.js --dir <research_dir>
node ${CLAUDE_PLUGIN_ROOT}/scripts/generate-research-pdf.js --dir <research_dir>
```

Prompts get global topic numbers via `refresh-prompts` after batches are registered.

## Finish

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/pipeline-run.js finish \
  --dir <research_dir> --app <appId>
```

**Print the path** from stdout to the user: `data/research/<slug>/04_study_guide.md` and offer `05_full_guide.pdf` if Stage 5 ran.

## Rules

- **Always save full prompts** to `*_prompt.md` / `01_job_scraper.md` / `02_job_analyzer.md` **before** calling agents or APIs.
- Never fabricate research; mark unknowns in prompts and reports.
- New slug per run; use `--force` on init only when intentionally overwriting.
- Do **not** use `data/pipelines/` for new runs (deprecated).
