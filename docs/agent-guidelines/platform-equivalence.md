# Platform capability equivalence

Maps Claude Code features to Cursor and Codex equivalents for **HeadHunter**.

Platform tool versions: [`../engineering/build-and-release/platform-targets.md`](../engineering/build-and-release/platform-targets.md).

## Instructions

| Capability | Claude Code | Cursor | Codex |
|------------|-------------|--------|-------|
| Repo policy | `CLAUDE.md` → `@AGENTS.md` | `.cursor/rules/*.mdc` → `AGENTS.md` | `AGENTS.md` |

## Skills

| Capability | Claude Code | Cursor | Codex |
|------------|-------------|--------|-------|
| Bundled skills | `skills/` via `.claude-plugin/plugin.json` | same paths in `.cursor-plugin/plugin.json` | same paths in `.codex-plugin/plugin.json` |

## MCP servers

| Capability | Claude Code | Cursor | Codex |
|------------|-------------|--------|-------|
| Stubs | `.mcp.json` | `.cursor/mcp.json` (Cursor-native) + plugin `mcpServers` | `mcpServers` in `.codex-plugin/plugin.json` + `.codex/config.toml` |

Fill `${ENV_VAR}` placeholders locally — never commit tokens.

## Hooks / lifecycle automation

| Capability | Claude Code | Cursor | Codex |
|------------|-------------|--------|-------|
| Session hooks | `hooks/hooks.json` (data protect, briefing, backup) | No native `hooks.json` — use scoped `.mdc` rules + `AGENTS.md` discipline | `hooks` field in `.codex-plugin/plugin.json` |

**Cursor substitute:** enforce data-protection rules via `.cursor/rules/headhunter.mdc` and never hand-edit `data/*.json` (use `scripts/crud.js`).

## Claude-only features (documented asymmetry)

| Feature | Notes |
|---------|-------|
| Marketplace install | Claude Code: `/plugin marketplace add` — see README Install |
| Official Gmail/Calendar MCP | Authenticate via Claude Code `/mcp` UI |
| Plugin hooks on Write/SessionStart | Node scripts under `scripts/` — Codex mirrors via plugin hooks field |

These asymmetries are intentional; skill and policy parity is maintained across platforms.
