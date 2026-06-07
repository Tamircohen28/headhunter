# HeadHunter — Claude Code Guide

HeadHunter is a local-first AI job-search co-pilot. It manages a full job-search lifecycle: CRM pipeline, interview prep, CV tailoring, job discovery, salary negotiation, network mapping, and analytics — all driven by Claude Code skills and Node.js scripts. All CRM data lives in `data/*.json` (gitignored). No database server, no npm install for the core runtime.

---

## Key file locations

| Path | Purpose |
|------|---------|
| `skills/` | Agent workflow instructions (loaded automatically by the plugin) |
| `agents/` | Subagent prompts spawned by skills |
| `commands/` | Slash-command entry points (`/headhunter:<name>`) |
| `scripts/crud.js` | All entity CRUD — add / update / move / delete / seed |
| `scripts/lib.js` | `loadData` / `saveData` / `DATA_DIR` helpers |
| `scripts/enums.js` | Pipeline stages, terminal states, allowed enum values |
| `scripts/test.sh` | 21-check self-test suite |
| `references/data-model.md` | Field-level schema for all entities |
| `docs/ARCHITECTURE.md` | System layers, storage model, pipelines |
| `settings.json` | Plugin defaults (currency, stale threshold, research params) |
| `.mcp.json` | MCP server definitions for Claude Code |
| `.claude-plugin/plugin.json` | Plugin manifest |
| `hooks/hooks.json` | Claude Code hooks (SessionStart briefing, PostToolUse validation) |

---

## Build & test

```bash
bash scripts/test.sh          # 21 checks — run after any change
node scripts/crud.js seed     # seed 5 demo applications
```

No compilation step. Node.js ≥ 18 required. No `npm install` needed for the core CRM.

---

## Commit convention

```
<type>(<scope>): <short description>

Types: feat | fix | refactor | docs | test | chore
Examples:
  feat(scanner): add success-score to scan output
  fix(crud): enforce forward-only move for terminal states
  docs(architecture): update pipeline diagram
```

---

## Hard constraints

- **Never hand-edit `data/*.json`** — always use `node scripts/crud.js` so validation, `updated_date`, and the event log stay consistent.
- **Never commit `data/` or `.env`** — both are gitignored; they contain personal job-search data and secrets.
- **Status moves are forward-only** — use `crud.js update` (patch) to correct a mistake, not `move`.
- **Always `--dry-run` before external sends** — Notion, Todoist, Twilio, and Google sync scripts all support `--dry-run`.
- **No npm dependencies in core scripts** — `scripts/*.js` must run with `node` alone. Only `deep-research.js` and `generate-research-pdf.js` use optional peer tools.
- **Do not add test stubs that call the real network** — `scripts/test.sh` must run offline.
