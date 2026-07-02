#!/usr/bin/env bash
# Validate the agent surface: JSON manifests parse, JS scripts have valid syntax,
# canonical agent docs exist, and every skill/agent/command has YAML frontmatter.
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1
FAIL=0
note() { printf '  %s %s\n' "$1" "$2"; }

echo "== JSON manifests =="
for f in .claude-plugin/plugin.json .mcp.json settings.json hooks/hooks.json .cursor/mcp.json; do
  [ -f "$f" ] || { note "--" "$f (absent, skipped)"; continue; }
  if node -e "JSON.parse(require('fs').readFileSync('$f','utf8'))" 2>/dev/null; then
    note "ok" "$f"
  else
    note "XX" "$f — invalid JSON"; FAIL=1
  fi
done

echo "== JS syntax =="
for f in scripts/*.js; do
  if node --check "$f" 2>/dev/null; then note "ok" "$f"; else note "XX" "$f"; FAIL=1; fi
done

echo "== Canonical agent docs =="
for f in AGENTS.md CLAUDE.md; do
  if [ -f "$f" ]; then note "ok" "$f"; else note "XX" "$f missing"; FAIL=1; fi
done
if grep -q "AGENTS.md" CLAUDE.md 2>/dev/null; then
  note "ok" "CLAUDE.md references AGENTS.md"
else
  note "XX" "CLAUDE.md does not reference AGENTS.md"; FAIL=1
fi

echo "== Frontmatter (skills / agents / commands) =="
while IFS= read -r f; do
  if [ "$(head -1 "$f")" = "---" ]; then
    note "ok" "$f"
  else
    note "XX" "$f — missing YAML frontmatter"; FAIL=1
  fi
done < <(find skills agents commands -name '*.md' 2>/dev/null | sort)

echo
if [ "$FAIL" -eq 0 ]; then
  echo "agent-check: PASS"
else
  echo "agent-check: FAIL"
fi
exit "$FAIL"
