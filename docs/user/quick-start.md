# Quick Start

Get HeadHunter running in about 5 minutes.

---

## Prerequisites

- Node.js ≥ 18 (`node --version`)
- One of: Claude Code ≥ 1.0, Cursor, or OpenAI Codex CLI

---

## Step 1 — Install

**Claude Code**
```bash
/plugin marketplace add /path/to/headhunter
/plugin install headhunter@headhunter-marketplace
```

**Cursor** — open the repo root in Cursor. Rules auto-load from `.cursor/rules/` and MCP servers load from `.cursor/mcp.json`. No install step.

**OpenAI Codex CLI** — clone the repo and run `codex` from it. `AGENTS.md` is read automatically.

---

## Step 2 — Load demo data

```bash
node scripts/crud.js seed
```

This loads 5 sample applications across different pipeline stages so you can explore commands right away.

---

## Step 3 — View your pipeline

```bash
node scripts/dashboard.js    # metrics: response rate, conversion, ghosted %
node scripts/analytics.js    # funnel with conversion rates and source breakdown
```

Or in Claude Code:
```
/headhunter:pipeline
```

---

## Step 4 — Set up your candidate profile

Your profile powers CV tailoring, job scoring, and salary negotiation.

```
/headhunter:setup
```

The setup wizard collects: name, CV text (paste or file path), current role/skills, target roles, remote preference, salary expectations, and priority weights. Takes about 5 minutes.

---

## Step 5 — Add a real job

```
/headhunter:add-application
```

Or directly:
```bash
node scripts/crud.js add applications '{"company":"Acme","role":"Staff Engineer","url":"https://acme.com/jobs/123","status":"Saved","priority":"High"}'
```

---

## Step 6 — Score it

```
/headhunter:scan <job-url-or-description>
```

Produces a **Match Score** (keyword/experience/location fit) and a **Success Score** (company selectivity, hiring bar). Verdict: Strong Candidate / Apply / Long Shot / Skip.

---

## What's next

| Goal | Command |
|------|---------|
| Find more jobs | `/headhunter:discover` |
| Get a company + role brief before a recruiter call | `/headhunter:brief` |
| Generate a tailored CV + cover letter | `/headhunter:apply` |
| Build a study guide for an upcoming interview | `/headhunter:research` |
| Run a mock interview | `/headhunter:mock` |
| Draft follow-up emails | `/headhunter:followup` |
| Get a counter-offer script | `/headhunter:negotiate` |

See the full command reference in [README.md](../../README.md).
