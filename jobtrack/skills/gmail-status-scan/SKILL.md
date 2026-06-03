---
name: gmail-status-scan
description: Scan Gmail for job-application updates and auto-detect status changes (rejections, offers, interview invites). Triggers on scan gmail, email update, application status from email, check my inbox for job updates.
allowed-tools: Read, Bash, Grep, Glob
disallowed-tools: Write, Edit
---

# Gmail Status Scan

Detect application status changes from emails and propose pipeline updates.
See `references/server-functions.md` (gmailJobScanner) for the full logic.

## How to run

1. **If Gmail MCP is connected:** fetch recent messages, then pass each as
   `{id, from, subject, body}` JSON to the classifier:
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/scripts/detect-gmail-status.js --json '[ ... ]'
   ```
2. **Offline / testing:** run against the fixtures:
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/scripts/detect-gmail-status.js \
     --fixtures ${CLAUDE_PLUGIN_ROOT}/references/email-fixtures.md
   ```

The script returns `{id, detected_status, matched_company, matched_application_id}`
for each email.

## Apply updates safely

1. Present a table of detected changes **before** applying anything:

   | Email from | Detected status | Matched application | Current → New |
   |-----------|-----------------|---------------------|---------------|

2. Only apply a change if it **advances** the pipeline OR the new status is
   `Rejected`/`Declined`. Skip same-or-backward transitions.
3. **Require explicit user approval** for the batch, then apply each via:
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js move <appId> "<Status>"
   ```
4. Report unmatched emails so the user can link them manually.
