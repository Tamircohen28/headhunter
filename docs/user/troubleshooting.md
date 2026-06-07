# Troubleshooting

---

## `bash scripts/test.sh` — some checks fail

**Cause:** `data/` doesn't exist or is empty.

```bash
node scripts/crud.js seed
bash scripts/test.sh
```

All 21 checks should pass after seeding.

---

## `node: command not found` / `node --version` shows < 18

HeadHunter requires Node.js ≥ 18. Install from [nodejs.org](https://nodejs.org) or via your version manager:

```bash
nvm install 20
nvm use 20
```

---

## `/headhunter:setup` — profile not saving

Check that `data/` exists and is writable:

```bash
ls -la data/
node scripts/candidate-profile.js show
```

If `candidate-profile.json` is missing, run setup again and complete all steps.

---

## `crud.js move` — "Invalid status transition"

The pipeline is forward-only. You cannot move an application backward via `move`. To correct a mistake:

```bash
# Use update (patch) instead of move
node scripts/crud.js update applications app_001 '{"status":"Applied"}'
```

---

## Sync script fails with auth error

All sync scripts require OAuth tokens. Check your `.env`:

```bash
cat .env   # never commit this file
```

Required per integration:

| Integration | Required env var(s) |
|-------------|---------------------|
| Notion | `NOTION_TOKEN`, `NOTION_DATABASE_ID` |
| Google Calendar | `GOOGLE_OAUTH_TOKEN`, `GOOGLE_CALENDAR_ID` |
| Google Tasks | `GOOGLE_OAUTH_TOKEN`, `GOOGLE_TASKS_LIST_ID` |
| Todoist | `TODOIST_API_TOKEN` |
| Twilio WhatsApp | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`, `WHATSAPP_TO` |

Always test with `--dry-run` first:

```bash
node scripts/sync-notion.js --dry-run
```

---

## `deep-research.js` — "OPENAI_API_KEY not set"

The interview-research pipeline optionally calls OpenAI's Deep Research API. Set the key:

```bash
export OPENAI_API_KEY=sk-...
node scripts/deep-research.js --dir data/research/<slug> --batch 03
```

Without the key, you can still run `/headhunter:research` — the skill uses Claude's built-in WebSearch instead of the OpenAI batch API.

---

## MCP server not connecting (Claude Code)

1. Check `.mcp.json` — confirm the package name is correct.
2. Confirm the required env var is exported in your shell.
3. Restart the Claude Code session after editing `.mcp.json`.

For the LinkedIn MCP (`mcp-linkedin`), note the prominent ToS warning in `.mcp.json`. If you don't want it, remove that server block.

---

## `generate-cv-html.js` — CV not rendering correctly

The output is standard A4 HTML designed for browser print-to-PDF:

1. Open the generated `.html` file in Chrome or Safari.
2. Press `Cmd+P` → select "Save as PDF".
3. Set margins to "None" and enable "Background graphics".

---

## Data looks corrupted / want to restore a backup

```bash
ls data/backups/                        # list available snapshots
node scripts/restore.js data/backups/headhunter-backup-<ts>.json   # preview
node scripts/restore.js data/backups/headhunter-backup-<ts>.json --confirm   # restore
```

---

## Something else

Open an issue: [github.com/TamirCohen28/headhunter/issues](https://github.com/TamirCohen28/headhunter/issues)

Include: Node.js version, AI host (Claude Code / Cursor / Codex), the command you ran, and the full error output.
