#!/usr/bin/env bash
# Wrapper for @notionhq/notion-mcp-server. Checks NOTION_TOKEN before launching
# so that /mcp failure messages are actionable rather than a bare -32000 error.
set -euo pipefail

if [[ -z "${NOTION_TOKEN:-}" ]]; then
  echo "Notion MCP: missing \$NOTION_TOKEN" >&2
  echo "  1. Go to https://www.notion.so/my-integrations → '+ New integration'" >&2
  echo "  2. Copy the Internal Integration Secret (starts with secret_...)" >&2
  echo "  3. Add to ~/.zshrc:" >&2
  echo "       export NOTION_TOKEN=secret_..." >&2
  echo "       source ~/.zshrc" >&2
  exit 1
fi

exec npx -y @notionhq/notion-mcp-server
