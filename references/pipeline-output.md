# Research output layout (`data/research/<slug>/`)

Interview-research artifacts live under **`data/research/<slug>/`** where **slug** is a human-readable job name (e.g. `nvidia-senior-ai-llm-solutions`), **not** `app_*` ids.

## Run directory

```
data/research/<slug>/
  00_run.json
  01_job_scraper.md          # prompt / instructions for scrape step
  01_job_description.md      # scraped job posting (output)
  02_job_analyzer.md         # full prompt sent to job-analyzer subagent
  02_job_metadata.json       # JobMetadata (output)
  03-research-prompt.md      # OpenAI Deep Research input (batch 1)
  03-research-report.md      # Deep Research output (batch 1)
  04-research-prompt.md      # batch 2 (if needed)
  04-research-report.md
  …
  NN-study-guide-prompt.md   # prompt for study-guide-writer (NN = last batch + 1)
  04_study_guide.md          # final merged study guide (fixed name)
```

### Batch numbering

- **03, 04, 05…** — one pair per topic batch (`maxTopicsPerAgent` topics each, default 4).
- **04_study_guide.md** — always the final deliverable filename (downstream skills depend on it).

## CLI

### Initialize

```bash
node scripts/pipeline-run.js init \
  --app <appId> \
  --slug "nvidia-senior-ai-llm-solutions" \
  --url "<job_url>" \
  --company "NVIDIA" \
  --role "Senior AI and LLM Solutions Software Engineer"
```

If `data/research/<slug>/` already exists, a timestamp suffix is added unless `--force`.

### Write prompts and outputs (before/after each step)

```bash
node scripts/pipeline-run.js write --dir data/research/<slug> \
  --file 01_job_scraper.md --text "<full scrape prompt>"

node scripts/pipeline-run.js write --dir data/research/<slug> \
  --file 01_job_description.md --file-content @/path/to/extracted-jd.md
```

Always persist the **full** prompt text before calling an agent or API.

### Topic batches — Deep Research (OpenAI)

1. Build prompt file:

```bash
node scripts/pipeline-run.js batch --dir data/research/<slug> \
  --topics '["Python for Production Engineering","Linux Environments",...]'
```

Creates `03-research-prompt.md` (or next free number) using the [Deep Research template](deep-research-template.md).

2. Run Deep Research (requires `OPENAI_API_KEY`):

```bash
export OPENAI_API_KEY="..."
# optional: export OPENAI_DEEP_RESEARCH_MODEL=o3-deep-research

node scripts/deep-research.js --dir data/research/<slug> --batch 03
```

Writes `03-research-report.md`. Use `--dry-run` to validate without API calls.

Run batches **03, 04, …** in parallel shells if desired (one API job per batch).

### Finish

After **study-guide-writer** saves `04_study_guide.md`:

```bash
node scripts/pipeline-run.js finish --dir data/research/<slug> --app <appId>
```

Prints: `data/research/<slug>/04_study_guide.md`

## Application linkage

| Field | Value |
|-------|--------|
| `research_dir` | `data/research/<slug>` |
| `research_status` | `complete` after `finish` |

## Legacy paths (still readable)

| Old path | Notes |
|----------|--------|
| `data/research/app_<id>/` | Pre-slug runs |
| `data/pipelines/<slug>-<timestamp>/` | Deprecated; do not use for new runs |

Downstream skills read, in order:

1. `<research_dir>/04_study_guide.md`
2. `<research_dir>/02_job_metadata.json`

## Environment

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Deep Research (`deep-research.js`) |
| `OPENAI_DEEP_RESEARCH_MODEL` | Default `o4-mini-deep-research`; set `o3-deep-research` for max quality |
