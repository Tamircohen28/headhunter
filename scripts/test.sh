#!/usr/bin/env bash
# Self-test: exercises the acceptance criteria against a temp data dir.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export CLAUDE_PLUGIN_ROOT="$ROOT"
export JOBTRACK_DATA_DIR="$(mktemp -d)"
trap 'rm -rf "$JOBTRACK_DATA_DIR"' EXIT

pass=0; fail=0
ok()   { echo "  ✅ $1"; pass=$((pass+1)); }
no()   { echo "  ❌ $1"; fail=$((fail+1)); }
check(){ if eval "$2"; then ok "$1"; else no "$1"; fi; }

cd "$ROOT"
echo "JobTrack self-test (data: $JOBTRACK_DATA_DIR)"

node scripts/crud.js seed >/dev/null 2>&1
check "seed loads 5 applications" "[ \$(node scripts/crud.js list applications | grep -c '\"id\"') -eq 5 ]"

# forward-only move rules
node scripts/crud.js move app_003 "Technical" >/dev/null 2>&1
check "forward move Applied->Technical succeeds" "node scripts/crud.js get applications app_003 | grep -q '\"Technical\"'"
check "backward move Technical->Applied is refused" "! node scripts/crud.js move app_003 'Applied' >/dev/null 2>&1"
check "terminal Rejected allowed from any stage" "node scripts/crud.js move app_002 'Rejected' >/dev/null 2>&1"

# enum validation
check "invalid status rejected on add" "! node scripts/crud.js add applications '{\"company\":\"X\",\"role\":\"Y\",\"status\":\"Bogus\"}' >/dev/null 2>&1"

# events / timeline
check "status change logged as event" "node scripts/crud.js events app_003 | grep -q 'status_change'"
check "timeline renders for app_001" "node scripts/timeline.js app_001 | grep -q 'Timeline'"

# dashboard
check "dashboard json has metrics" "node scripts/dashboard.js --json | grep -q 'responseRatePct'"

# calendar
check "calendar lists scheduled interview" "node scripts/calendar.js | grep -qi 'Acme'"

# export round-trip
node scripts/export-applications.js --format csv --out "$JOBTRACK_DATA_DIR/e.csv" >/dev/null 2>&1
rows=$(( $(wc -l < "$JOBTRACK_DATA_DIR/e.csv") - 1 ))
if [ "$rows" -eq 5 ]; then ok "csv export has 5 data rows"; else no "csv export has 5 data rows (got $rows)"; fi
check "json export valid" "node scripts/export-applications.js --format json | python3 -m json.tool >/dev/null"

# csv import with aliases
printf 'Company Name,Position,Stage\nFoo,Dev,Applied\nBar,SRE,Saved\nBaz,DE,Saved\n' > "$JOBTRACK_DATA_DIR/imp.csv"
check "csv import maps 3 rows" "[ \$(node scripts/csv-import.js \"$JOBTRACK_DATA_DIR/imp.csv\" | grep -c '\"company\"') -eq 3 ]"

# gmail fixtures: 5/5 classified
check "gmail classifies 5/5 fixtures" "[ \$(node scripts/detect-gmail-status.js --fixtures references/email-fixtures.md | grep -c '\"detected_status\": \"') -eq 5 ]"

# integration dry-runs (no network/creds)
check "todoist dry-run works" "node scripts/sync-todoist.js --dry-run 2>&1 | grep -qi 'dry-run'"
check "notion dry-run works" "node scripts/sync-notion.js --dry-run 2>&1 | grep -qi 'dry-run'"
check "twilio dry-run works" "node scripts/sync-twilio.js --dry-run 2>&1 | grep -qi 'reminder'"

# session briefing valid JSON
check "session briefing emits valid JSON" "node scripts/session-briefing.js | python3 -m json.tool >/dev/null"

echo ""
echo "Result: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
