# Interview-Research Pipeline

Orchestration: Claude Code skills + subagents (scrape, analyze, merge) + **OpenAI Deep Research** (topic batches).

**Output layout:** [pipeline-output.md](./pipeline-output.md) — `data/research/<slug>/`

## Stage map

| Stage | Prompt file | Output file | Engine |
|-------|-------------|-------------|--------|
| 0 Init | — | `00_run.json` | `pipeline-run.js init` |
| 1 Scrape | `01_job_scraper.md` | `01_job_description.md` | WebFetch / paste |
| 2 Analyze | `02_job_analyzer.md` | `02_job_metadata.json` | job-analyzer subagent |
| 3 Research | `03-research-prompt.md` … | `03-research-report.md` … | `deep-research.js` (OpenAI) |
| 4 Merge | `NN-study-guide-prompt.md` | `04_study_guide.md` | study-guide-writer subagent |

Batch numbers increment: first research batch is **03**, second **04**, etc. Final study guide filename is always **`04_study_guide.md`**.

## Config (`settings.json` → `headhunter.research`)

| Param | Default | Meaning |
|-------|---------|---------|
| `studyWeeks` | 4 | Study plan length |
| `hoursPerWeek` | 10 | Study intensity |
| `maxTopicsPerAgent` | 4 | Topics per Deep Research batch |
| `outputDir` | `data/research` | Base directory |
| `deepResearchModel` | `o4-mini-deep-research` | Override via `OPENAI_DEEP_RESEARCH_MODEL` |

## JobMetadata schema (Stage 2 output)

See previous schema in this file — `02_job_metadata.json` fields: `job_title`, `company_name`, `topic_hierarchy`, `topic_learning_order`, `topic_dependencies`, etc.

## Finish

```bash
node scripts/pipeline-run.js finish --dir data/research/<slug> --app <appId>
```

Prints path to `04_study_guide.md`.
