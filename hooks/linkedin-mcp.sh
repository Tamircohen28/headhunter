#!/usr/bin/env bash
# Wrapper for mcp-linkedin. Checks required env vars before launching.
# On missing vars, emits a JSON-RPC error to stdout (parsed by Claude Code)
# so the /mcp failure message is actionable rather than a bare -32000.
set -euo pipefail

MISSING=()
[[ -z "${LINKEDIN_EMAIL:-}" ]] && MISSING+=("LINKEDIN_EMAIL")
[[ -z "${LINKEDIN_PASSWORD:-}" ]] && MISSING+=("LINKEDIN_PASSWORD")

if [[ ${#MISSING[@]} -gt 0 ]]; then
  MSG="LinkedIn MCP not configured — missing: ${MISSING[*]}. Add to ~/.zshrc: export LINKEDIN_EMAIL=you@email.com && export LINKEDIN_PASSWORD=yourpassword && source ~/.zshrc. WARNING: unofficial MCP, may violate LinkedIn ToS."
  printf '{"jsonrpc":"2.0","error":{"code":-32000,"message":"%s"},"id":null}\n' "$MSG"
  exit 1
fi

exec npx -y mcp-linkedin
