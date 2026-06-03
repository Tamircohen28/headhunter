# Changelog

All notable changes to the JobTrack Claude Code plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.2.0] — 2026-06-03

### Added

- **`/jobtrack:brief` command + `interview-brief` skill** — Full "Interview Intel" briefing for
  initial recruiter screens: 6-section report covering company intelligence, role analysis,
  keyword explainer, what to say (including salary script), and fast prep plan. Uses
  WebSearch + WebFetch; personalizes using `candidate-profile.json` when loaded.
  Includes ILS salary guidance with Glassdoor/Levels.fyi/Israeli salary benchmark research.
- **`/jobtrack:setup` command** — Candidate profile wizard: collects personal info, CV
  (file or paste), experience summary, job preferences, salary expectations (ILS),
  availability, and application defaults. Saved to `data/candidate-profile.json`.
- **`candidate-profile.js` script** — CRUD for `candidate-profile.json`:
  `show`, `set '<json-patch>'`, `extract-cv <file>`, `reset [--confirm]`.
- **GitHub MCP** — Official `@modelcontextprotocol/server-github` added to `.mcp.json`.
  Env: `GITHUB_PERSONAL_ACCESS_TOKEN`. Use for candidate profile import, company open
  source research.
- **LinkedIn MCP (unofficial)** — Community `mcp-linkedin` added to `.mcp.json` with
  prominent ToS warning. Env: `LINKEDIN_EMAIL`, `LINKEDIN_PASSWORD`. Remove from
  `.mcp.json` if not wanted.
- **Google Drive** — Documented as a remote MCP via claude.ai platform (no local config
  needed). Useful for reading CV files from Drive.
- **Glassdoor + Levels.fyi** — Integrated into `/jobtrack:brief` salary research via
  WebSearch (no MCP needed).
- **`references/candidate-profile-schema.md`** — Full schema documentation for
  `candidate-profile.json`.
- **Integrations MCP table** — `skills/integrations/SKILL.md` now has a status table
  for all connected MCPs.

---

## [1.1.0] — 2026-06-03

### Added

- **`sync-google-calendar.js`** — REST v3 fallback for syncing interview rounds to Google Calendar.
  Idempotent via `google_calendar_event_id`. Supports `--dry-run` and `--all`.
- **`sync-google-tasks.js`** — REST v1 fallback for syncing tasks to Google Tasks.
  Idempotent via `google_task_id`. Supports `--dry-run` and `--all`.
- **Notion task sync** — `sync-notion.js` now syncs tasks to `NOTION_TASKS_DATABASE_ID`
  in addition to applications. Adds `--tasks-only` and `--apps-only` flags.
- **`/jobtrack:insights` command** — Runs the `interview-analyst` agent against a specific
  application: surfaces strengths, weaknesses, patterns, and next-round predictions.
- **`/jobtrack:settings` command** — View and update all settings (currency, stale threshold,
  study weeks, hours/week) directly from the terminal.
- **`/jobtrack:status` command** — Mid-session notification check: overdue tasks, upcoming
  interviews, and stale applications without restarting the session.
- **`/jobtrack:search` command** — Search and filter applications by company, role, status,
  priority, remote type, salary range, or staleness.
- **`backup.js` / `restore.js`** — Timestamped JSON snapshots of all data. Restore requires
  `--confirm` to prevent accidental overwrites.
- **`send-stale-reminders.js`** — Finds stale ACTIVE_STAGES applications and sends a WhatsApp
  digest via Twilio (prints to stdout if Twilio is not configured). Includes cron setup
  instructions for daily scheduling.
- **`post-research-hook.js`** — PostToolUse hook that auto-updates `research_dir` and
  `last_research_at` on the application whenever `04_study_guide.md` is written.
- **CSV import from URL** — `csv-import.js` now accepts `--url <url>` to import directly
  from a downloadable CSV link (LinkedIn exports, Notion exports, etc.).
- **Stale detection in session briefing** — `session-briefing.js` now surfaces stale
  applications (ACTIVE_STAGES, 7+ days without update) inline at session start.
- **Offer comparison view** — `jobtrack-core` skill documents side-by-side offer comparison
  with salary midpoint, currency, and offer-detail notes.
- **Salary search** — `jobtrack-core` skill documents filtering by salary range and `has:offer`.

### Changed

- **`sync-todoist.js`** — Clarified the `--all` update path: `POST /tasks/{id}` updates an
  existing task (Todoist REST v2 uses POST for both create and update). `created` and
  `updated` counts are now reported separately.
- **`interview-research` skill** — Added `context: fork` to isolate the pipeline from the
  main session. Added a concrete worked example for the Stage 3 parallel fan-out
  (N task calls in a single message).
- **`interview-prep` skill** — Now explicitly specifies how to consume `04_study_guide.md`
  when `research_dir` is set: extracts topics, cheat-sheet, tips, pitfalls, and questions.
  Added `disallowed-tools: Write, Edit` (read-only view).
- **`pipeline` skill** — Added `disallowed-tools: Write, Edit` to prevent accidental mutation.
- **`gmail-status-scan` skill** — Added `disallowed-tools: Write, Edit` to prevent accidental
  mutation.
- **`job-analyzer` agent** — Added `effort: high` so the subagent runs with maximum
  thoroughness when spawned by the research pipeline.
- **`study-guide-writer` agent** — Added `effort: high` for the same reason.
- **`plugin.json`** — Added `engines` (Node ≥ 18, Claude Code ≥ 1.0) and `requiredEnvVars`
  (documenting all optional integration env vars). Version bumped to 1.1.0.
- **`hooks.json`** — Added `post-research-hook.js` to the `PostToolUse(Write)` hook chain.
- **`integrations` skill** — Updated to document all new scripts and flags.
- **`.gitignore`** — Clarified that `data/` covers the local backend; `~/.jobtrack` is
  outside the repo and needs no gitignore entry.

---

## [1.0.0] — 2026-05-01

### Added

- Initial release: pipeline Kanban, application CRUD, interview logging, task management.
- Integrations: Notion (applications), Todoist, Twilio WhatsApp.
- Research pipeline: `job-analyzer`, `topic-researcher`, `study-guide-writer` subagents.
- Gmail status scan, session briefing, CSV import/export.
- Local JSON store with `crud.js`, `validate-data.js`, `dashboard.js`, `timeline.js`.
