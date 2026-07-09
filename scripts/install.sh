#!/usr/bin/env bash
# install.sh — first-time HeadHunter setup (Node check + platform hints).
#
# Usage: make install  |  bash scripts/install.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: Node.js >= 18 required. Install from https://nodejs.org" >&2
  exit 1
fi

node_major=$(node -e 'console.log(process.versions.node.split(".")[0])')
if (( node_major < 18 )); then
  echo "ERROR: Node.js >= 18 required (found $(node --version))" >&2
  exit 1
fi

echo "HeadHunter install — Node $(node --version) OK"
echo ""
echo "Claude Code:"
echo "  /plugin marketplace add Tamircohen28/headhunter"
echo "  /plugin install headhunter@headhunter-marketplace"
echo ""
echo "Cursor: open this repo root — .cursor/rules/ and .cursor/mcp.json load automatically."
echo ""
echo "Codex CLI: run codex from this repo root (reads AGENTS.md)."
echo ""
echo "Optional: cp .env.example .env and fill integration tokens."
echo "Demo data: make seed"
