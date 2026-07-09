#!/usr/bin/env bash
# uninstall.sh — reverse safe install-side effects and plugin removal hints.
#
# Usage: make uninstall  |  bash scripts/uninstall.sh
set -euo pipefail

echo "HeadHunter uninstall"
echo "Claude Code: /plugin uninstall headhunter@headhunter-marketplace"
echo ""
echo "Local data under data/ is gitignored — remove manually if desired:"
echo "  rm -rf data/*.json data/backups data/research"
echo ""
echo "Cursor/Codex: close the workspace; no global uninstall required."
