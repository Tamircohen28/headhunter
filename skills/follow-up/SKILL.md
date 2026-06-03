---
name: follow-up
description: Draft personalized follow-up emails for stale applications, post-interview silences, and pending offers. Triggers on follow up, send follow-up, check in with recruiter, no response from company, follow up on application, follow up after interview.
allowed-tools: Read, Bash
disallowed-tools: Write, Edit
---

# Follow-up Automation

Identify applications that need follow-up and draft personalized emails for each scenario.

## Step 0 — Generate drafts

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/draft-followups.js
```

This identifies three scenarios:
- **Post-apply silence** — Applied 7+ days ago, status still Applied
- **Post-interview silence** — Completed interview 3+ days ago, no next round scheduled
- **Offer deadline** — Status = Offer for 2+ days with no action

## Step 1 — Present drafts

For each draft, show it with context and action options:

```
### 1. Acme Corp — Senior Engineer · POST-APPLY SILENCE (9 days)

To: jane.recruiter@acme.com
Subject: Following up — Senior Engineer application

---
Hi Jane,

I wanted to follow up on my application for the Senior Engineer role submitted on
2026-05-25. I remain very interested in Acme and the position. Please let me know
if you need any additional information or have any questions.

Thank you for your time.

Best regards
---

Actions: [Send via Gmail MCP] [Edit draft] [Add contact email] [Skip]
```

If the contact email is missing, note: "No recruiter email on file — add via `/headhunter:contacts` or manually."

## Step 2 — Personalize if requested

When the user asks to "make it more specific" or "add a personal touch" for a draft:
- Add a reference to the specific role/team (use job_url or job_description from the application)
- Add a company-specific detail (WebSearch one recent news item or product if needed)
- Keep it to 3–4 sentences total — recruiters don't read long follow-ups

## Step 3 — Send via Gmail MCP (if connected)

If the Gmail MCP is connected and the user confirms sending:
> "Send follow-up to {email}? (This will send from your connected Gmail account.)"

Use the Gmail MCP to send the email. Record the send:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js add notes \
  '{"application_id":"<id>","content":"Follow-up sent to {email} on {date}: {subject}","note_type":"Follow-Up"}'
```

If Gmail MCP is not connected, show the draft formatted for manual copy-paste and suggest:
> "Copy the email above and send it from your email client. Run `/headhunter:add-task` to set a reminder for the response."

## Step 4 — Create follow-up tasks

For each follow-up sent or skipped, offer:
> "Add a task to check for response in 5 days?" → `/headhunter:add-task`
