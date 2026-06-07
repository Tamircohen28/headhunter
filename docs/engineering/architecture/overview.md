# Architecture Overview

HeadHunter is a **local-first AI job-search co-pilot**. There is no server, no database engine, and no cloud backend. All persistence is plain JSON files on disk; all intelligence is delegated to the AI host (Claude Code, Cursor, or Codex) through skills, subagents, and deterministic Node.js scripts.

---

## Layers

```
┌─────────────────────────────────────────────────────┐
│  AI hosts: Claude Code · Cursor · Codex CLI         │
├─────────────────────────────────────────────────────┤
│  Agent layer                                        │
│    Skills (workflow instructions)                   │
│    Subagents (focused research / generation tasks)  │
│    Slash commands (/headhunter:<name>)              │
├─────────────────────────────────────────────────────┤
│  Deterministic runtime (Node.js scripts)            │
│    crud.js · lib.js · enums.js                      │
│    sync-*.js · analytics.js · score-job.js          │
│    pipeline-run.js · deep-research.js               │
├─────────────────────────────────────────────────────┤
│  Local store (source of truth)                      │
│    data/*.json · candidate-profile.json             │
│    data/research/<slug>/                            │
├─────────────────────────────────────────────────────┤
│  Optional external services                         │
│    MCP: Gmail · Calendar · Notion · GitHub          │
│    REST: Todoist · Twilio · OpenAI Deep Research    │
└─────────────────────────────────────────────────────┘
```

### Why this separation matters

- **Scripts are always correct** — `crud.js` enforces pipeline order, schema validation, and the event log with no AI in the path. Tests run offline against the script layer alone.
- **Skills are instructions, not code** — a skill file tells the AI what sequence of scripts and MCPs to call. Updating a skill changes behavior without touching any Node.js code.
- **Subagents are isolated** — each subagent (`job-analyzer`, `study-guide-writer`, `mock-interviewer`) has a narrow prompt and limited tool access. They fail small.

---

## Data flow: a scan request

```
User: /headhunter:scan <url>

  job-scanner skill
    → score-job.js (deterministic pre-score: skills, experience, location, salary)
    → job-scorer subagent
        → WebSearch (Glassdoor, Blind — company selectivity)
        → Produces: match_score, success_score, scanner_notes, verdict
    → crud.js update applications <id> (persists scores)
```

---

## Data flow: interview research

```
User: /headhunter:research

  interview-research skill (context: fork — isolated from main session)
    → Stage 1: job-analyzer subagent → job_metadata.json
    → Stage 2: topic-researcher subagent → topic list
    → Stage 3: N parallel study tasks (one per topic)
        → deep-research.js (OpenAI Responses API — if OPENAI_API_KEY set)
           OR Claude WebSearch (fallback)
    → Stage 4: study-guide-writer subagent → 04_study_guide.md
    → post-research-hook.js (PostToolUse) → sets research_status = "complete"
```

---

## Storage design

One JSON array file per entity type. `crud.js` is the only writer — it adds `updated_date`, appends to `events.json`, and validates against `enums.js` before saving.

| File | Entity |
|------|--------|
| `applications.json` | Job applications (pipeline cards) |
| `interviews.json` | Interview rounds |
| `tasks.json` | Prep / follow-up tasks |
| `contacts.json` | People at target companies |
| `notes.json` | Free-form notes |
| `events.json` | Append-only audit log (do not hand-edit) |

External systems (Notion, Todoist, Google Calendar) hold **copies**, linked by IDs stored on the primary record (`notion_page_id`, `todoist_task_id`, `google_calendar_event_id`). Sync scripts are idempotent — they PATCH via stored IDs instead of creating duplicates.

---

## Key design invariants

1. **`data/` is never committed** — gitignored. Personal data stays local.
2. **Forward-only pipeline** — `crud.js move` rejects backward transitions. Use `update` to correct mistakes.
3. **No runtime npm dependencies** — `scripts/*.js` uses Node.js built-ins only. No supply-chain risk for the CRUD layer.
4. **`--dry-run` on all external sends** — Notion, Todoist, Twilio, Google sync all print what they would do before writing.
5. **`--confirm` on destructive ops** — `delete` and `restore` require an explicit flag.

---

## Further reading

- [../ARCHITECTURE.md](../ARCHITECTURE.md) — full storage model, pipeline stage diagrams, Mermaid flowcharts
- [../../references/data-model.md](../../references/data-model.md) — field-level schema for all entities
- [../../references/pipeline-output.md](../../references/pipeline-output.md) — research run folder layout and CLI
- [../../references/server-functions.md](../../references/server-functions.md) — integration triggers and idempotent sync rules
