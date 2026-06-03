Here's the full gap analysis plus everything I'd add beyond the spec:

---

## Missing features (from the spec)

**1. Google Calendar sync script**
No `sync-google-calendar.js`. Every other integration (Notion, Todoist, Twilio) has a dry-runnable Node script; Calendar only says "use the MCP server." A REST fallback (Google Calendar API v3) would complete parity.

**2. Google Tasks sync script**
Same gap — `sync-google-tasks.js` is documented in `server-functions.md` and referenced in env vars, but never implemented. Todoist has a full script; Tasks doesn't.

**3. `/headhunter:insights` command**
The `interview-analyst` agent exists but nothing invokes it in context. There's no `/headhunter:insights <company>` command that feeds the agent the right application data and surfaces the strengths/weaknesses/next-round-predictor output. It's an orphaned agent.

**4. `/headhunter:settings` command**
`settings.json` is a config file, not a user-facing UI. No way to view or change default currency, study weeks, hours/week, or stale threshold from the terminal.

**5. Notification state**
Spec section 5.9 calls for persistent in-session notifications (overdue tasks, upcoming interviews). The session briefing fires at start, but there's no `/headhunter:status` or notification-check command for mid-session use.

**6. Stale reminder scheduler**
`stale-applications` agent drafts emails but there's no wiring to actually send them. The spec says daily — no cron hook or scheduled invocation.

**7. Notion task sync is underdocumented**
`sync-notion.js` only syncs applications. Task sync to `NOTION_TASKS_DATABASE_ID` is specified in `server-functions.md` but never implemented in the script.

---

## Incomplete implementations

**8. Research pipeline orchestration guidance is thin**
`interview-research` skill mentions the `ultracode` / `/effort xhigh` dynamic-workflow path as a "tip" but doesn't give concrete instructions. The fan-out step (spawning N parallel `topic-researcher` agents) is described in prose but the actual Task-tool calls are left to Claude to figure out at runtime — a worked example would make it reliable.

**9. `interview-prep` skill doesn't actually consume the study guide**
It says "if `research_dir` is set, read `04_study_guide.md`" but the skill body doesn't spell out how to fold that content into the prep brief. In practice Claude may or may not do it.

**10. `sync-todoist.js --all` update path**
The PUT path is written but Todoist REST v2 actually uses `POST /tasks/{id}` for updates (same verb as create) — the comment in the code says this correctly but the variable name `isUpdate` and the identical `method: "POST"` make it confusing and fragile to future edits.

---

## Enhancements worth building

**11. `backup.js` / `restore.js` scripts**
No way to snapshot or restore the `~/.jobtrack` data. Given the P1 fix moving data to the home dir, a simple timestamped JSON backup is an obvious safety net.

**12. Stale detection in session briefing**
The briefing already runs at startup — it could surface stale applications (7+ days in active stages) inline, not just overdue tasks. Currently only `stale-applications` agent does this, and it's never auto-invoked.

**13. Salary formatting + offer comparison**
Multiple applications may have offers. No command or view compares offers side-by-side (salary range, benefits field, equity). Useful and low-effort to add as a view in `jobtrack-core`.

**14. Application search / filter command**
No `/headhunter:search <term>` — the only way to find an application is to list all and eyeball it. With 50+ applications this becomes painful.

**15. `disallowed-tools` on skills that shouldn't write**
`pipeline`, `interview-prep`, `gmail-status-scan` are mostly read-only views. Adding `disallowed-tools: [Write, Edit]` (v2.1.157 feature) would prevent accidental data mutation when those skills are active.

**16. `context: fork` on the research skill**
The `interview-research` skill does heavy multi-step work and spawns subagents — it should declare `context: fork` so it runs in an isolated context and doesn't pollute the main session's tool history.

**17. `effort: high` on `job-analyzer` and `study-guide-writer` agents**
Currently only the orchestrating skill has `effort: high`. The individual research subagents should also declare it.

**18. PostToolUse hook for research output**
When `04_study_guide.md` is written, automatically update the application's `last_research_at` and `research_dir`. Right now that's done manually in the skill — a hook on Write matching `data/research/*/04_study_guide.md` could do it automatically.

**19. CSV import from URL (not just file)**
`csv-import.js` only takes a local path. Many job trackers (Notion, LinkedIn exports) produce downloadable CSVs — a `--url` flag using `fetch` would save the manual download step.

**20. `plugin.json` missing `engines` / `peerDependencies`**
No declaration of minimum Node version (needs ≥ 18 for native `fetch`), minimum Claude Code version, or required env vars. Installing on Node 16 silently breaks.

**21. `.gitignore` doesn't cover `~/.jobtrack`**
The gitignore covers `data/` (the old path), but since the default is now `~/.jobtrack` that entry is moot. Should add a note in the README and ensure the `.gitignore` still excludes `data/` for people who set `JOBTRACK_DATA_DIR=./data`.

**22. No `CHANGELOG.md`**
For a plugin distributed via marketplace, a changelog is expected. Currently the only history is git log.

---

**Summary: 22 items.** ~7 are spec gaps (missing features that were promised), ~3 are incomplete implementations needing finishing, and ~12 are enhancements that would push it from "good" to "production quality."

Want me to start working through these? I can tackle them in priority order — the integration scripts (#1, #2, #7) and the `/headhunter:insights` command (#3) are the highest-value gaps; the `disallowed-tools` + `context: fork` skill improvements (#15, #16, #17) are one-line changes with meaningful safety benefit.