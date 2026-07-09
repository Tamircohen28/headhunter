# Platform targets

HeadHunter supports **Claude Code**, **Cursor**, and **OpenAI Codex CLI**. Canonical version pins live in [platform-targets.json](platform-targets.json).

| Platform | Validated against | Notes |
|----------|-------------------|-------|
| Claude Code | 1.0.0 | Plugin marketplace install; hooks via `hooks/hooks.json` |
| Cursor | 0.45.0 | Rules from `.cursor/rules/`; MCP from `.cursor/mcp.json` |
| Codex | 0.40.0 | Reads `AGENTS.md`; plugin manifest in `.codex-plugin/plugin.json` |

Update `platform-targets.json`, README Row 3 badges, and this file together when adopting new platform APIs. Agents run `make platform-targets-sync` before PR.
