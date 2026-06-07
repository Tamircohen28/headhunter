# CI Workflow

CI runs on every pull request and every push to `main` via `.github/workflows/ci.yml`.

---

## Jobs

### `lint`

- **JS syntax check:** runs `node --check` on every file in `scripts/`. Catches parse errors before they reach tests.
- **Shell lint:** runs `shellcheck` on `scripts/parse-csv-import.sh` and `scripts/test.sh`. Catches common shell scripting bugs (unquoted variables, bad conditionals, etc.).

### `test`

Runs `bash scripts/test.sh` — the 21-check self-test suite.

Covers:
- CRUD: add, list, update, move, delete
- Pipeline enforcement: forward-only stage transitions
- Timeline: chronological event merge
- Dashboard: JSON output structure
- Export: CSV and JSON round-trip
- Candidate profile: show, set, extract-cv
- Validation hook: schema check after writes

All tests run against a fresh temporary `data/` directory — no side effects on real data.

### `secret-scan`

Greps committed files for high-signal secret patterns:

| Pattern | Catches |
|---------|---------|
| `sk-[A-Za-z0-9]{20,}` | OpenAI API keys |
| `AIza[A-Za-z0-9_-]{35}` | Google API keys |
| `AKIA[A-Z0-9]{16}` | AWS access key IDs |

Excludes `.env.example` (which intentionally contains placeholder stubs). Fails the build if a real-looking secret is found in any `.js`, `.sh`, or `.json` file.

---

## What CI does NOT check

- Integration scripts (`sync-*.js`) — these require live credentials and can't run in CI. Test with `--dry-run` locally before merging.
- `deep-research.js` — requires `OPENAI_API_KEY`. Test locally.
- Agent / skill behavior — the AI is not in the loop during CI. Test new skills manually in Claude Code / Cursor / Codex.

---

## Release workflow

`.github/workflows/release.yml` is a separate, manual-dispatch workflow. It:

1. Validates the semver version input.
2. Runs `bash scripts/test.sh`.
3. Creates and pushes a git tag.
4. Creates a GitHub Release pointing to `CHANGELOG.md`.

Trigger it from **Actions → Release → Run workflow** after updating `CHANGELOG.md` and bumping the version in `.claude-plugin/plugin.json`.
