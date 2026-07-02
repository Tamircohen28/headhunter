# Changelog

All notable changes to the HeadHunter Claude Code plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
See [docs/engineering/build-and-release/versioning.md](docs/engineering/build-and-release/versioning.md)
for the release and versioning policy.

---

## [Unreleased]

_Nothing yet. Add entries here as you land changes; they roll into the next release._

---

## [1.4.7] — 2026-06-13

### Changed

- **LinkedIn MCP is now opt-in** (#9) — Removed the unofficial community `linkedin`
  server from the default `.mcp.json`. It fails to connect for any user who hasn't set
  `LINKEDIN_EMAIL`/`LINKEDIN_PASSWORD`, producing a permanent `/mcp` failure with no
  actionable message. Users who want it add the block manually per new README
  instructions. LinkedIn was also dropped from the session-start env check
  (`check-mcp-env.js`) since the server is no longer active by default.

---

## [1.4.6] — 2026-06-13

### Fixed

- **MCP wrapper scripts emit a JSON-RPC error to stdout** (#8) — Claude Code discards
  stderr from MCP servers, so the actionable "missing env var" message from the wrapper
  scripts never surfaced in `/mcp`. `hooks/linkedin-mcp.sh` and `hooks/notion-mcp.sh`
  now return a proper JSON-RPC error payload on stdout, which Claude Code parses and
  displays inline in the `/mcp` failure output instead of the opaque
  `-32000: Connection closed`.

---

## [1.4.5] — 2026-06-13

### Added

- **`hooks/linkedin-mcp.sh` + `hooks/notion-mcp.sh` env-check wrappers** (#7) — Wrap the
  bare `npx` MCP launches; they check required env vars before starting the server and
  print exact `export` commands when any are missing. Pattern mirrors
  tamirs-superpowers' `github-mcp.sh`. `.mcp.json` now invokes the wrappers instead of
  `npx` directly.

---

## [1.4.4] — 2026-06-13

### Changed

- **Session-start env check expanded to all 14 optional integration vars** (#6) —
  `scripts/check-mcp-env.js` previously only covered `NOTION_TOKEN`, `LINKEDIN_EMAIL`,
  and `LINKEDIN_PASSWORD`. It now checks Notion (token + both database IDs), Google
  Calendar, Google Tasks, Todoist, Twilio/WhatsApp, and OpenAI deep research, plus
  LinkedIn. Each group shows only the vars actually missing, with exact `export`
  commands and where to find the values. Silent when all are set.

---

## [1.4.3] — 2026-06-13

### Added

- **`scripts/check-mcp-env.js` + SessionStart hook** (#5) — Runs at session start and
  warns via `additionalContext` when `NOTION_TOKEN`, `LINKEDIN_EMAIL`, or
  `LINKEDIN_PASSWORD` are missing, with step-by-step setup instructions per missing
  server. Silent no-op when all vars are set; never blocks session start
  (`continueOnBlock: true`).

---

## [1.4.2] — 2026-06-13

### Removed

- **Redundant Gmail, Google Calendar, and GitHub MCP servers** (#4) — Removed from
  `.mcp.json`. Gmail and Calendar are covered by the official claude.ai platform
  integrations (authenticated via `/mcp`); GitHub is already provided zero-config by
  tamirs-superpowers. The duplicate local npm servers caused `/doctor` failures on
  every startup with no benefit. Only `notion` and `linkedin` remain.

---

## [1.4.1] — 2026-06-13

### Fixed

- **Replaced non-existent Anthropic Gmail/Calendar npm packages** (#3) —
  `@anthropic/gmail-mcp-server` and `@anthropic/google-calendar-mcp-server` do not exist
  on npm and caused MCP connection failures on every startup. Swapped for real working
  packages: `@gongrzhe/server-gmail-autoauth-mcp` (Gmail, OAuth auto-auth) and
  `mcp-google-calendar` (requires `GOOGLE_CALENDAR_CREDENTIALS_PATH`). Both need a
  one-time Google OAuth setup, documented in `_setup` comments in `.mcp.json`.
  _(Note: these local Gmail/Calendar servers were removed again in 1.4.2 in favor of the
  official claude.ai platform integrations.)_

---

## [1.4.0] — 2026-06-03

### Added

- **`/headhunter:discover` command + `job-discovery` skill** — Searches LinkedIn, AllJobs, Drushim, Indeed, and target company career pages for matching open roles. Uses `job-discoverer` agent with WebSearch + WebFetch. Results ranked by relevance score; filtered against deal_breakers and exclude_companies. Saves selected jobs to pipeline via `save-discovered-jobs.js`. Closes the biggest competitive gap vs. Teal/Sonara.
- **`/headhunter:negotiate` command + `salary-negotiation` skill** — Data-driven counter-offer script with market anchoring (Glassdoor/Levels.fyi/Israeli salary surveys), specific counter amount at market p75, levers to pull if base is fixed, verbatim script, walk-away number, and what NOT to say. Uses `salary-negotiator` agent. Competes with Huru.ai and ORO AI.
- **`/headhunter:followup` command + `follow-up` skill** — Detects three follow-up scenarios (post-apply silence ≥7d, post-interview silence ≥3d, offer pending ≥2d). Drafts personalized emails per scenario. Sends via Gmail MCP if connected; records sends as notes.
- **`/headhunter:network` command + `network-finder` skill** — Finds contacts at a target company via WebSearch + LinkedIn/GitHub MCPs. Uses `network-researcher` agent to draft personalized DM/email outreach (specific hooks, not templates). Maps warm intro paths via existing CRM contacts.
- **`scripts/draft-followups.js`** — Identifies follow-up-needed applications across all three scenarios. Outputs structured JSON or human-readable drafts.
- **`scripts/save-discovered-jobs.js`** — Batch-saves discovered job leads to applications.json, deduplicating by URL. Supports `--dry-run` and `--stdin`.
- **`agents/job-discoverer.md`** — Multi-board job search agent with relevance scoring (title match + location + salary + freshness).
- **`agents/salary-negotiator.md`** — Full negotiation brief with counter-offer, levers table, scripts, and walk-away signal.
- **`agents/network-researcher.md`** — Finds and prioritizes contacts, researches recent activity, drafts personalized outreach.

### Fixed (internal quality)

- **`hooks/hooks.json`** — Added `SessionEnd` hook: runs `backup.js` automatically after every Claude session.
- **`skills/interview-brief/SKILL.md`** — Now reads `match_score`/`success_score` from application record and surfaces a **Prior Scan Summary** block at the top of every briefing. Added `Task` to allowed-tools.
- **`skills/application-assistant/SKILL.md`** — Warns when `match_score < 50` before generating tailored CV. Standardized profile-required exit pattern.
- **`skills/mock-interview/SKILL.md`** — Mock session results now persisted to `InterviewRound.mock_sessions` array. Standardized profile-required exit.
- **`references/data-model.md`** — Added `mock_sessions` to InterviewRound; added `research_status` to JobApplication.
- **`scripts/enums.js`** — Added `research_status` enum (`not_started / in_progress / complete / stale`).
- **`scripts/post-research-hook.js`** — Now sets `research_status = "complete"` when study guide is written.
- **`commands/brief.md`** — Added `Task` to allowed-tools frontmatter.

### Added — later 1.4.0 work (2026-06-03 → 2026-06-08, shipped under the same 1.4.0 version, previously unlogged)

- **Cursor + Codex support** — Added `AGENTS.md` as the canonical, tool-agnostic agent
  guide (shared by Claude Code, Cursor, and Codex), plus `.cursor/mcp.json` and
  `.cursor/rules/headhunter.mdc`. Removed all legacy `job4u` references and rewrote the
  README. (`976e398`)
- **Deep Research pipeline overhaul** — Restructured interview-research output under
  `data/research/<slug>/`. Added `scripts/deep-research.js` (OpenAI Deep Research
  integration), `scripts/pipeline-run.js` (orchestrates the multi-step run), and
  `scripts/research-lib.js` shared helpers. New `docs/ARCHITECTURE.md`,
  `references/pipeline-output.md`, and `references/deep-research-template.md`. `backup.js`
  extended to cover the research tree. (`159988b`)
- **Research PDF pipeline** — Added `scripts/generate-research-pdf.js`,
  `scripts/merge-research-full.js`, and `scripts/merge-research-pdfs.js`: numbered
  per-topic PDFs, a merged full report, and OpenAI batch PDF generation. Added
  `.env.example` keys for the pipeline. (`58f1508`)
- **Deep Research reasoning summary is opt-in** — Reasoning summaries are only requested
  when the OpenAI org is verified, avoiding API errors for unverified orgs. (`644abcc`)

### Fixed — later 1.4.0 work

- **`session-briefing.js`** — Now reads `staleThreshold` from `settings.json` instead of
  a hardcoded value; also renamed the test script and corrected the README install path.
  (`51562d0`)

### Hardened — portfolio-grade pass (2026-06-08, shipped under 1.4.0)

- **`scripts/protect-data.js`** — New PreToolUse guard that blocks direct `Write`/`Edit`
  to `data/*.json`, enforcing the write-through-CRUD rule. Wired into `hooks/hooks.json`.
  (`f07bd9d`)
- **Test suite expanded 21 → 38 checks** — Added coverage for candidate-profile,
  draft-followups, analytics, save-discovered-jobs, google-calendar/tasks dry-run,
  stale-reminders, the validate-data and protect-data hooks, score-job, and restore
  preview.
- **`scripts/validate-data.js`** — Now handles `candidate-profile.json` as a single
  object rather than an array.
- **All 14 agents pinned to full model IDs** — Migrated from `sonnet`/`haiku` shorthand
  to explicit model IDs. Added `context: fork` to the `mock-interview` (with
  `effort: high`) and `follow-up` (Gmail MCP isolation) skills.
- **`.github/SECURITY.md`** — Data-privacy, credential-handling, and vulnerability-
  disclosure guidance. CI secret-scan expanded to detect GitHub PATs (classic +
  fine-grained) and Slack bot tokens.
- **Metadata & housekeeping** — Fixed placeholder author fields in
  `plugin.json`/`marketplace.json`, added a CI badge to the README, expanded
  `.gitignore`, and removed the leftover `task.md` session artifact.

---

## [1.3.0] — 2026-06-03

### Added

- **`/headhunter:scan` command + `job-scanner` skill** — Brutally honest Match Score (0–100) and Success Score (0–100) for any job posting. Deterministic pre-scoring via `score-job.js`, then `job-scorer` agent refines with company selectivity research (Glassdoor, Blind). Verdict: Strong Candidate / Apply / Long Shot / Skip. Saves scores + notes to the application record.
- **`/headhunter:apply` command + `application-assistant` skill** — Generates a tailored CV and cover letter in parallel (cv-tailor + cover-letter-writer agents). CV output is A4-optimized HTML via `generate-cv-html.js` (browser print-to-PDF, zero deps). Also handles application form Q&A in Mode B.
- **`/headhunter:cv-review` command + `cv-optimizer` skill** — ATS score, missing keyword analysis, top 5 bullet improvements, LinkedIn headline/summary/skills audit. Runs cv-reviewer + linkedin-auditor agents in parallel.
- **`/headhunter:mock` command + `mock-interview` skill** — Interactive mock interview sessions. Pre-assessment (4 questions), then spawns mock-interviewer agent that asks round-appropriate questions, evaluates answers with per-question scores, gives feedback, and produces a Ready/More prep/Not ready verdict.
- **`/headhunter:analytics` command** — Pipeline funnel with conversion rates at each stage, offer rate, ghost rate, top-performing sources, scanner score averages.
- **`score-job.js`** — Deterministic pre-scorer: skill keyword overlap, experience level check, remote/location match, salary range check. Feeds the job-scorer agent.
- **`generate-cv-html.js`** — Markdown → A4 HTML converter. Zero external deps, inline CSS, print-safe. Open in browser → Cmd+P → PDF.
- **`analytics.js`** — Full pipeline funnel analytics with bar charts, conversion rates, source breakdown.
- **`agents/job-scorer.md`** — WebSearch-based success scorer; classifies company selectivity into Tiers 1–4.
- **`agents/cv-tailor.md`** — Rewrites CV for a specific role (reframes, reorders, keyword-aligns). Never invents facts.
- **`agents/cover-letter-writer.md`** — 3-paragraph cover letter: hook + fit + ask. No clichés; names real company facts.
- **`agents/cv-reviewer.md`** — ATS scoring, keyword gap analysis, bullet quantification, format and structure audit.
- **`agents/linkedin-auditor.md`** — LinkedIn profile completeness score, headline formula, keyword optimization, experience vs CV consistency.
- **`agents/mock-interviewer.md`** — Full interactive interviewer persona: Technical/Behavioral/System Design/Recruiter/Final modes. STAR scoring for behavioral, correctness+complexity for technical.

### Changed

- **`skills/interview-prep`** — Added pre-assessment section (4 questions before any prep brief) to weight weak areas more heavily. Added mock interview link at the end.
- **`scripts/candidate-profile.js`** — Added `preferences.priority_weights` (comp/growth/wlb/tech/mission, 1–10), `past_interview_patterns`, `github_imported_at`, `linkedin_imported_at` to profile schema.
- **`commands/setup.md`** — Added Step 1b (GitHub auto-import via MCP) and Step 1c (LinkedIn auto-import via MCP), and priority weights collection in Step 4.
- **`references/data-model.md`** — Added `match_score`, `success_score`, `scanner_notes`, `tailored_cv_path`, `cover_letter_path`, `referral_contact_id` to JobApplication.

---

## [1.2.0] — 2026-06-03

### Added

- **`/headhunter:brief` command + `interview-brief` skill** — Full "Interview Intel" briefing for
  initial recruiter screens: 6-section report covering company intelligence, role analysis,
  keyword explainer, what to say (including salary script), and fast prep plan. Uses
  WebSearch + WebFetch; personalizes using `candidate-profile.json` when loaded.
  Includes ILS salary guidance with Glassdoor/Levels.fyi/Israeli salary benchmark research.
- **`/headhunter:setup` command** — Candidate profile wizard: collects personal info, CV
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
- **Glassdoor + Levels.fyi** — Integrated into `/headhunter:brief` salary research via
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
- **`/headhunter:insights` command** — Runs the `interview-analyst` agent against a specific
  application: surfaces strengths, weaknesses, patterns, and next-round predictions.
- **`/headhunter:settings` command** — View and update all settings (currency, stale threshold,
  study weeks, hours/week) directly from the terminal.
- **`/headhunter:status` command** — Mid-session notification check: overdue tasks, upcoming
  interviews, and stale applications without restarting the session.
- **`/headhunter:search` command** — Search and filter applications by company, role, status,
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
- **Offer comparison view** — `headhunter-core` skill documents side-by-side offer comparison
  with salary midpoint, currency, and offer-detail notes.
- **Salary search** — `headhunter-core` skill documents filtering by salary range and `has:offer`.

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
- **`.gitignore`** — Clarified that `data/` covers the local backend; `~/.headhunter` is
  outside the repo and needs no gitignore entry.

---

## [1.0.0] — 2026-05-01

### Added

- Initial release: pipeline Kanban, application CRUD, interview logging, task management.
- Integrations: Notion (applications), Todoist, Twilio WhatsApp.
- Research pipeline: `job-analyzer`, `topic-researcher`, `study-guide-writer` subagents.
- Gmail status scan, session briefing, CSV import/export.
- Local JSON store with `crud.js`, `validate-data.js`, `dashboard.js`, `timeline.js`.
