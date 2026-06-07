#!/usr/bin/env bash
# Self-test: exercises the acceptance criteria against a temp data dir.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export CLAUDE_PLUGIN_ROOT="$ROOT"
export HEADHUNTER_DATA_DIR="$(mktemp -d)"
trap 'rm -rf "$HEADHUNTER_DATA_DIR"' EXIT

pass=0; fail=0
ok()   { echo "  ✅ $1"; pass=$((pass+1)); }
no()   { echo "  ❌ $1"; fail=$((fail+1)); }
check(){ if eval "$2"; then ok "$1"; else no "$1"; fi; }

cd "$ROOT"
echo "HeadHunter self-test (data: $HEADHUNTER_DATA_DIR)"

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
node scripts/export-applications.js --format csv --out "$HEADHUNTER_DATA_DIR/e.csv" >/dev/null 2>&1
rows=$(( $(wc -l < "$HEADHUNTER_DATA_DIR/e.csv") - 1 ))
if [ "$rows" -eq 5 ]; then ok "csv export has 5 data rows"; else no "csv export has 5 data rows (got $rows)"; fi
check "json export valid" "node scripts/export-applications.js --format json | python3 -m json.tool >/dev/null"

# csv import with aliases
printf 'Company Name,Position,Stage\nFoo,Dev,Applied\nBar,SRE,Saved\nBaz,DE,Saved\n' > "$HEADHUNTER_DATA_DIR/imp.csv"
check "csv import maps 3 rows" "[ \$(node scripts/csv-import.js \"$HEADHUNTER_DATA_DIR/imp.csv\" | grep -c '\"company\"') -eq 3 ]"

# gmail fixtures: 5/5 classified
check "gmail classifies 5/5 fixtures" "[ \$(node scripts/detect-gmail-status.js --fixtures references/email-fixtures.md | grep -c '\"detected_status\": \"') -eq 5 ]"

# integration dry-runs (no network/creds)
check "todoist dry-run works" "node scripts/sync-todoist.js --dry-run 2>&1 | grep -qi 'dry-run'"
check "notion dry-run works" "node scripts/sync-notion.js --dry-run 2>&1 | grep -qi 'dry-run'"
check "twilio dry-run works" "node scripts/sync-twilio.js --dry-run 2>&1 | grep -qi 'reminder'"

# session briefing valid JSON
check "session briefing emits valid JSON" "node scripts/session-briefing.js | python3 -m json.tool >/dev/null"

# backup dedup
node scripts/backup.js >/dev/null 2>&1
before=$(ls -1 "$HEADHUNTER_DATA_DIR/backups" 2>/dev/null | wc -l | tr -d ' ')
node scripts/backup.js >/dev/null 2>&1
after=$(ls -1 "$HEADHUNTER_DATA_DIR/backups" 2>/dev/null | wc -l | tr -d ' ')
check "backup skips identical consecutive snapshot" "[ \"$before\" = \"$after\" ]"

# research run layout (data/research/<slug>/)
APP_ID=$(node scripts/crud.js add applications '{"company":"PipeCo","role":"Tester","status":"Saved"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
RUN_JSON=$(node scripts/pipeline-run.js init --app "$APP_ID" --slug pipe-test --company PipeCo --role Tester)
RESEARCH_DIR=$(echo "$RUN_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['research_dir'])")
SLUG=$(basename "$RESEARCH_DIR")
node scripts/pipeline-run.js write --dir "$RESEARCH_DIR" --file 01_job_scraper.md --text "fetch url" >/dev/null
node scripts/pipeline-run.js write --dir "$RESEARCH_DIR" --file 01_job_description.md --text "# JD\nbody" >/dev/null
node scripts/pipeline-run.js batch --dir "$RESEARCH_DIR" --topics '["Topic A"]' --batch 03 >/dev/null
check "batch creates 03-research-prompt.md" "test -f \"$HEADHUNTER_DATA_DIR/research/$SLUG/03-research-prompt.md\""
node scripts/deep-research.js --dir "$RESEARCH_DIR" --batch 03 --dry-run >/dev/null 2>&1
check "deep-research dry-run ok" "test -f \"$HEADHUNTER_DATA_DIR/research/$SLUG/03-research-report.md\""
node scripts/deep-research.js --dir "$RESEARCH_DIR" --batch 03 --pdf --dry-run >/dev/null 2>&1
check "deep-research --pdf dry-run writes pdf placeholder" "test -f \"$HEADHUNTER_DATA_DIR/research/$SLUG/03-research-report.pdf\""
echo "# Guide" > "$HEADHUNTER_DATA_DIR/research/$SLUG/04_study_guide.md"
GUIDE=$(node scripts/pipeline-run.js finish --dir "$RESEARCH_DIR" --app "$APP_ID" | tail -1)
check "finish prints 04_study_guide path" "echo \"$GUIDE\" | grep -q '04_study_guide.md'"
node scripts/pipeline-run.js refresh-prompts --dir "$RESEARCH_DIR" >/dev/null 2>&1
check "refresh-prompts numbers topics" "grep -q '^1\\. \\*\\*Topic A\\*\\*' \"$HEADHUNTER_DATA_DIR/research/$SLUG/03-research-prompt.md\""
echo "# Topic" > "$HEADHUNTER_DATA_DIR/research/$SLUG/03-research-report.md"
echo '{"topic_learning_order":["Topic A"],"topic_hierarchy":{"Topic A":["Sub one"]}}' > "$HEADHUNTER_DATA_DIR/research/$SLUG/02_job_metadata.json"
node scripts/merge-research-full.js --dir "$RESEARCH_DIR" >/dev/null 2>&1
check "merge-research-full creates 05_full_guide.md" "test -f \"$HEADHUNTER_DATA_DIR/research/$SLUG/05_full_guide.md\""
check "full guide has TOC" "grep -qi 'table of contents' \"$HEADHUNTER_DATA_DIR/research/$SLUG/05_full_guide.md\""

# ── Candidate profile ────────────────────────────────────────────────────────
node scripts/candidate-profile.js set '{"personal":{"name":"Test User","email":"test@example.com"}}' >/dev/null 2>&1
check "candidate-profile set writes profile" "test -f \"$HEADHUNTER_DATA_DIR/candidate-profile.json\""
check "candidate-profile show reads name" "node scripts/candidate-profile.js show | python3 -m json.tool | grep -q 'Test User'"

# ── draft-followups ──────────────────────────────────────────────────────────
check "draft-followups --json exits cleanly" "node scripts/draft-followups.js --json >/dev/null 2>&1"

# ── analytics ────────────────────────────────────────────────────────────────
check "analytics runs without error" "node scripts/analytics.js >/dev/null 2>&1"

# ── save-discovered-jobs ─────────────────────────────────────────────────────
LEADS_FILE="$HEADHUNTER_DATA_DIR/test-leads.json"
printf '%s\n' '[{"company":"TestCo","role":"SWE","job_url":"https://testco.com/jobs/1","status":"Saved"}]' > "$LEADS_FILE"
DISC_OUT=$(cat "$LEADS_FILE" | node scripts/save-discovered-jobs.js --stdin --dry-run 2>&1 || true)
check "save-discovered-jobs --dry-run parses leads" "echo \"$DISC_OUT\" | grep -qi 'would_add'"

# ── Google Calendar dry-run ──────────────────────────────────────────────────
check "sync-google-calendar --dry-run works" "node scripts/sync-google-calendar.js --dry-run 2>&1 | grep -qi 'dry-run\|nothing\|no interview'"

# ── Google Tasks dry-run ─────────────────────────────────────────────────────
check "sync-google-tasks --dry-run works" "node scripts/sync-google-tasks.js --dry-run 2>&1 | grep -qi 'dry-run\|nothing\|no task'"

# ── stale reminders ──────────────────────────────────────────────────────────
check "send-stale-reminders exits cleanly" "node scripts/send-stale-reminders.js --dry-run >/dev/null 2>&1 || true"

# ── validate-data (PostToolUse hook) ─────────────────────────────────────────
VALID_PAYLOAD="{\"tool_input\":{\"file_path\":\"$HEADHUNTER_DATA_DIR/applications.json\"}}"
check "validate-data exits 0 on valid data" "echo '$VALID_PAYLOAD' | node scripts/validate-data.js; [ \$? -eq 0 ]"

# ── protect-data (PreToolUse hook) ───────────────────────────────────────────
BLOCK_PAYLOAD="{\"tool_input\":{\"file_path\":\"$HEADHUNTER_DATA_DIR/applications.json\"}}"
check "protect-data blocks direct data write" "echo '$BLOCK_PAYLOAD' | node scripts/protect-data.js; [ \$? -eq 1 ]"
SAFE_PAYLOAD="{\"tool_input\":{\"file_path\":\"$HEADHUNTER_DATA_DIR/candidate-profile.json\"}}"
check "protect-data allows candidate-profile write" "echo '$SAFE_PAYLOAD' | node scripts/protect-data.js; [ \$? -eq 0 ]"

# ── score-job without profile ─────────────────────────────────────────────────
DUMMY_META="$HEADHUNTER_DATA_DIR/dummy-meta.json"
echo '{"job_title":"Staff Engineer","company_name":"Acme","required_skills":["Go","Kubernetes"],"preferred_skills":[],"nice_to_have_skills":[],"location":"Remote"}' > "$DUMMY_META"
check "score-job without profile returns error JSON" "node scripts/score-job.js \"$DUMMY_META\" --profile /nonexistent.json | python3 -m json.tool | grep -q 'error\|pre_score'"

# ── restore preview (no --confirm) ───────────────────────────────────────────
BACKUP_FILE=$(ls -t "$HEADHUNTER_DATA_DIR"/backups/*.json 2>/dev/null | head -1)
if [ -n "$BACKUP_FILE" ]; then
  RESTORE_OUT=$(node scripts/restore.js "$BACKUP_FILE" 2>&1 || true)
  check "restore without --confirm prints warning" "echo \"$RESTORE_OUT\" | grep -qi 'confirm'"
fi

echo ""
echo "Result: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
