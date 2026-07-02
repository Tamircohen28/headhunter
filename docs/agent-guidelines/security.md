# Security

## Secrets and credentials

- All credentials come from environment variables loaded from a local `.env` (gitignored). Copy `.env.example` and fill only the integrations you use.
- **Never commit `.env` or `data/`** — both are gitignored and contain personal, sensitive data.
- MCP configs (`.mcp.json`, `.cursor/mcp.json`) reference secrets only as `${VAR}` placeholders — never inline a literal token.
- The CI **Secret scan** job blocks merges on leaked key patterns (OpenAI, AWS, GitHub, Google, Slack).

## Safe external operations

- **Always `--dry-run` before external sends** — Notion, Todoist, Twilio, and Google sync scripts all support it.
- **Never hand-edit `data/*.json`** — always go through `node scripts/crud.js` so validation, timestamps, and the event log stay consistent.
- Destructive scripts (e.g. restore) require an explicit `--confirm` flag.
