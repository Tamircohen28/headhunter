# Development Workflow

## Setup

```bash
git clone https://github.com/TamirCohen28/headhunter.git
cd headhunter
node --version   # must be >= 18
node scripts/crud.js seed   # load 5 demo applications
bash scripts/test.sh        # all 21 checks should pass
```

No `npm install`. The core CRM runs entirely on Node.js built-ins.

---

## Running the test suite

```bash
bash scripts/test.sh
```

The suite exercises: CRUD, pipeline stage enforcement, timeline, dashboard JSON output, export round-trip, candidate profile, validation hook, and related behaviour — all against a temporary data directory. It runs fully offline.

**All 21 checks must pass before opening a PR.** If something fails, the output shows which check failed and the actual vs expected result.

---

## Project structure

```
scripts/        Core runtime — one file per concern, no dependencies
skills/         Agent workflow files (Claude Code plugin format)
agents/         Subagent prompts
commands/       Slash-command entry points
references/     Schemas and integration specs
hooks/          hooks.json (Claude Code event hooks)
docs/           Documentation
.mcp.json       MCP server definitions (Claude Code)
.cursor/        Cursor rules + MCP config
settings.json   Plugin defaults
```

---

## Making changes to scripts

`scripts/lib.js` — touch with care. It provides `loadData`, `saveData`, and `DATA_DIR` to every other script. Changes here affect all CRUD operations.

`scripts/enums.js` — defines allowed pipeline stages, terminal states, and status enums. Changes here affect `crud.js move` validation and `validate-data.js`.

`scripts/crud.js` — the only writer to `data/*.json`. Any new entity field should be documented in `references/data-model.md`.

---

## Making changes to skills or agents

Skills (`skills/*/SKILL.md`) are instruction files read by the AI host. You can edit them without running any build. Test by invoking the corresponding slash command in Claude Code / Cursor / Codex.

When adding a new skill:
1. Create `skills/<skill-name>/SKILL.md`
2. Create the corresponding entry point in `commands/<command-name>.md`
3. Register in `AGENTS.md` and `README.md`
4. Register in `.claude-plugin/plugin.json` if needed

---

## Branching and commits

- Branch from `main`: `git checkout -b feat/my-change`
- Commit format: `feat(scope): short description` (see [CONTRIBUTING.md](../../../CONTRIBUTING.md))
- Open a PR against `main`

---

## Releasing

Releases are cut via the manual GitHub Actions workflow:

1. Go to **Actions → Release → Run workflow**
2. Enter the semver version (e.g. `1.5.0`)
3. The workflow: validates, runs tests, creates a git tag, creates a GitHub Release

Before running: update `CHANGELOG.md` and bump the version in `.claude-plugin/plugin.json`.
