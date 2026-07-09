#!/usr/bin/env bash
# update.sh — refresh HeadHunter checkout and plugin install hints.
#
# Usage: make update  |  bash scripts/update.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo main)
  git fetch origin 2>/dev/null || true
  git pull --rebase "origin/$default" 2>/dev/null || echo "Note: pull skipped (detached or dirty tree)"
fi

echo "HeadHunter update"
echo "Claude Code: /plugin marketplace update headhunter-marketplace && /plugin update headhunter@headhunter-marketplace"
echo "Cursor/Codex: git pull in this repo to refresh rules and skills."
