# HeadHunter — Agent Instructions

You are operating in the **HeadHunter** job-search co-pilot repo. This project is a full job-search assistant: CRM pipeline, interview prep, CV tailoring, job discovery, salary negotiation, network mapping, and analytics.

All data lives in `data/*.json` (gitignored). All operations go through Node.js scripts in `scripts/`. **Never hand-edit `data/*.json`** — always use `scripts/crud.js`.

Requires Node.js ≥ 18. No npm install needed.

**Architecture:** local JSON store in `data/` (no DB server). See `docs/ARCHITECTURE.md` for pipelines, entity layout, and integrations.

---

## Core data operations

```bash
# Seed demo data (first run)
node scripts/crud.js seed

# List entities
node scripts/crud.js list applications
node scripts/crud.js list interviews
node scripts/crud.js list tasks
node scripts/crud.js list contacts

# Add
node scripts/crud.js add applications '{"company":"Acme","role":"Staff Engineer","status":"Applied","priority":"High"}'
node scripts/crud.js add tasks '{"title":"Follow up with recruiter","priority":"High","application_id":"app_001"}'

# Update (patch — only specified fields change)
node scripts/crud.js update applications app_001 '{"priority":"High","salary_min":45000}'

# Move through pipeline (forward-only enforced)
node scripts/crud.js move app_001 "Technical"

# Complete a task
node scripts/crud.js complete-task task_001

# View event log
node scripts/crud.js events app_001
```

## Pipeline rules

Stages (forward-only): `Saved → Applied → Phone Screen → Technical → Onsite → Offer → Accepted`  
Terminal (from any stage): `Rejected`, `Declined`, `Ghosted`  
The `move` command enforces forward-only — use `update` to correct a mistake.

## Views

```bash
node scripts/dashboard.js           # full metrics (response rate, conversion, ghosted %)
node scripts/dashboard.js --json    # machine-readable metrics
node scripts/analytics.js           # funnel with conversion rates and source breakdown
node scripts/calendar.js            # upcoming interview agenda
node scripts/timeline.js <appId>    # chronological timeline for one application
node scripts/session-briefing.js    # pipeline briefing (emits JSON — parse additionalContext)
```

## Candidate profile

The candidate profile powers CV tailoring, job scoring, and salary negotiation.

```bash
node scripts/candidate-profile.js show                        # view full profile
node scripts/candidate-profile.js set '<json-patch>'          # update any fields
node scripts/candidate-profile.js extract-cv <file.txt>       # read CV from file
node scripts/candidate-profile.js reset --confirm             # reset to blank
```

Key fields: `personal` (name/email/linkedin/github), `cv.text`, `experience` (title/years/skills), `preferences` (target_roles/remote_type/deal_breakers), `salary` (target_base_ils/floor_ils), `availability`.

## Job scoring

```bash
node scripts/score-job.js <job-metadata.json>           # pre-score vs candidate profile
node scripts/score-job.js <meta.json> --profile <profile.json>
```

Returns: `pre_match_score` (0–100), breakdown by skills/experience/location/salary, missing required skills.

## CV and application materials

```bash
# Generate A4 HTML CV from markdown (open in browser → Cmd+P → PDF)
node scripts/generate-cv-html.js --input <cv.md> --out <cv.html>

# Interview research: numbered prompts, Deep Research PDF batches, merge PDFs
node scripts/pipeline-run.js refresh-prompts --dir data/research/<slug>
OPENAI_API_KEY=... node scripts/deep-research.js --dir data/research/<slug> --batch 03 --pdf
node scripts/merge-research-pdfs.js --dir data/research/<slug>
# Fallback if only markdown: merge-research-full.js + generate-research-pdf.js
```

## Job discovery

```bash
# Save discovered jobs (dedup by URL)
node scripts/save-discovered-jobs.js '<json-array>' --dry-run   # preview
node scripts/save-discovered-jobs.js '<json-array>'              # save
```

## Follow-ups

```bash
node scripts/draft-followups.js           # detect and draft follow-up emails
node scripts/draft-followups.js --json    # structured JSON output
```

Three scenarios detected automatically:
- Post-apply silence (Applied 7+ days, no response)
- Post-interview silence (Completed interview 3+ days ago, no feedback)
- Offer deadline (Offer status for 2+ days)

## Integrations — always use `--dry-run` first

```bash
node scripts/sync-notion.js --dry-run           # preview; needs NOTION_TOKEN + NOTION_DATABASE_ID
node scripts/sync-todoist.js --dry-run          # preview; needs TODOIST_API_TOKEN
node scripts/sync-google-calendar.js --dry-run  # preview; needs GOOGLE_OAUTH_TOKEN
node scripts/sync-google-tasks.js --dry-run     # preview; needs GOOGLE_OAUTH_TOKEN
node scripts/sync-twilio.js --dry-run           # preview; needs TWILIO_* env vars
node scripts/send-stale-reminders.js --dry-run  # preview stale-app digest
```

## Import / Export

```bash
node scripts/csv-import.js <file.csv>             # dry-run: parse and print
node scripts/csv-import.js <file.csv> --write     # persist to applications.json
node scripts/csv-import.js --url <url> --write    # import from remote CSV URL
node scripts/export-applications.js --format csv --out ./export.csv
node scripts/export-applications.js --format json --out ./export.json
```

## Backup and restore

```bash
node scripts/backup.js                            # snapshot to data/backups/ (skips if identical to latest; keeps 10)
node scripts/backup.js --prune-duplicates         # remove duplicate backup files on disk
node scripts/backup.js --out <dir>               # snapshot to custom directory
node scripts/pipeline-run.js init --app <id> --slug <slug>   # data/research/<slug>/
node scripts/pipeline-run.js write --dir <slug> --file 01_job_scraper.md --text "..."
node scripts/pipeline-run.js batch --dir <slug> --topics '["Topic A",...]'
node scripts/deep-research.js --dir <slug> --batch 03        # OPENAI_API_KEY required
node scripts/pipeline-run.js finish --dir <slug> --app <id>  # prints 04_study_guide.md path
node scripts/restore.js <backup.json>            # safety check (shows --confirm prompt)
node scripts/restore.js <backup.json> --confirm  # actually restore
```

## Settings

`settings.json` (repo root) controls defaults. Top-level key is `headhunter`.

```json
{
  "headhunter": {
    "defaultCurrency": "USD",
    "staleThresholdDays": 7,
    "dataDir": "${CLAUDE_PLUGIN_ROOT}/data",
    "research": { "studyWeeks": 4, "hoursPerWeek": 10, "maxTopicsPerAgent": 4 }
  }
}
```

Environment override: `HEADHUNTER_DATA_DIR` — set this to use a different data directory.

## Data model (JobApplication key fields)

| Field | Notes |
|-------|-------|
| `id` | Auto-generated (`app_<ts>_<rand>`) |
| `status` | Enum — see pipeline stages above |
| `priority` | High / Medium / Low |
| `match_score` | 0–100, set by job scanner |
| `success_score` | 0–100, set by job scanner |
| `research_status` | not_started / in_progress / complete / stale |
| `research_dir` | Path to `data/research/<slug>/` (human-readable slug, not `app_*`) |
| `tailored_cv_path` | Path to generated HTML CV |
| `cover_letter_path` | Path to cover letter markdown |

Full schema: `references/data-model.md`

## Key constraints

- **Never delete data without `--confirm`** — the CLI enforces this.
- **Status moves are forward-only** — use `update` (not `move`) to correct a mistake.
- **`data/` is gitignored** — never commit user data.
- **No external sends without `--dry-run` review first** — Twilio, Notion, Todoist all support dry-run.

## Self-test

```bash
bash scripts/test.sh    # 21 checks across all core features — run after any change
```

All 21 should pass. If any fail, check that `data/` exists and `node scripts/crud.js seed` ran.
