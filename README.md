# job4u → JobTrack (Claude Code plugin)

This repository hosts **JobTrack**, a Claude Code plugin that turns job-search
tracking and interview prep into a terminal-native workflow.

It began as `job4u`, a Python interview-prep pipeline (scrape a job posting →
analyze with an LLM → divide research topics among agents → merge into a study
guide). That pipeline has been **re-implemented natively in Claude Code** — no
Python, no OpenAI — using subagents, `WebSearch`/`WebFetch`, and a local data
store. The plugin both *runs that pipeline* and provides a full job-application
CRM around it.

## The plugin lives in [`./jobtrack`](./jobtrack)

```bash
/plugin marketplace add ./jobtrack
/plugin install jobtrack@jobtrack-marketplace
# or:  /plugin install ./jobtrack
```

See **[jobtrack/README.md](./jobtrack/README.md)** for full docs.

## What it does

- **Pipeline CRM** — applications, interviews, tasks, contacts, notes; Kanban
  with forward-only stage rules; dashboard analytics; calendar; per-application
  timeline.
- **Interview-research pipeline** (the job4u port) — `/jobtrack:research <url>`
  scrapes a posting, web-researches the company, fans topic research across
  parallel subagents, and writes a study guide attached to the application.
- **Integrations** — Notion, Todoist, WhatsApp (Twilio) syncs are implemented
  as dry-runnable scripts; Gmail/Calendar via MCP or REST.
- **Zero runtime deps** — Node ≥ 18 only; data is plain JSON under
  `jobtrack/data/` (gitignored).

## Verify

```bash
bash jobtrack/scripts/test.sh   # 17 checks across all features
```

## Migrating from the old Python pipeline

The Python implementation (`src/`, `main.py`, `cli.py`, `setup.py`,
`requirements.txt`) has been removed; its behavior is reproduced by the
`interview-research` skill and the `job-analyzer` / `topic-researcher` /
`study-guide-writer` subagents. The original stage map and `JobMetadata` schema
are preserved in [`jobtrack/references/pipeline.md`](./jobtrack/references/pipeline.md).
