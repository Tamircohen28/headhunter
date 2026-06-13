#!/usr/bin/env bash
# Wrapper for @notionhq/notion-mcp-server. Checks NOTION_TOKEN before launching.
# On missing token, emits a JSON-RPC error to stdout (parsed by Claude Code)
# so the /mcp failure message is actionable rather than a bare -32000.
set -euo pipefail

if [[ -z "${NOTION_TOKEN:-}" ]]; then
  MSG="Notion MCP not configured — missing: NOTION_TOKEN. Get it at https://www.notion.so/my-integrations then add to ~/.zshrc: export NOTION_TOKEN=secret_... && source ~/.zshrc"
  printf '{"jsonrpc":"2.0","error":{"code":-32000,"message":"%s"},"id":null}\n' "$MSG"
  exit 1
fi

exec npx -y @notionhq/notion-mcp-server
