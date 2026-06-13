#!/usr/bin/env bash
# Wrapper for mcp-linkedin. Checks required env vars before launching so that
# /mcp failure messages are actionable rather than a bare -32000 error.
set -euo pipefail

MISSING=()
[[ -z "${LINKEDIN_EMAIL:-}" ]] && MISSING+=("LINKEDIN_EMAIL")
[[ -z "${LINKEDIN_PASSWORD:-}" ]] && MISSING+=("LINKEDIN_PASSWORD")

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "LinkedIn MCP: missing env vars: ${MISSING[*]}" >&2
  echo "  Add to ~/.zshrc and source it:" >&2
  echo "    export LINKEDIN_EMAIL=you@email.com" >&2
  echo "    export LINKEDIN_PASSWORD=yourpassword" >&2
  echo "  ⚠  This is an unofficial MCP and may violate LinkedIn ToS." >&2
  exit 1
fi

exec npx -y mcp-linkedin
