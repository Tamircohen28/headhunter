# Key Concepts

## Local-first data model

HeadHunter stores everything in plain JSON files on your machine under `data/`. There is no server, no cloud sync, and no account. Your job-search data stays private by default.

```
data/
├── applications.json       ← pipeline cards (one per job)
├── interviews.json         ← interview rounds
├── tasks.json              ← prep/follow-up tasks
├── contacts.json           ← people at target companies
├── notes.json              ← free-form notes
├── events.json             ← append-only audit log
├── candidate-profile.json  ← your CV, skills, salary, preferences
└── research/<slug>/        ← study guides per role
```

`data/` is gitignored — your pipeline never ships with the repo.

---

## The application pipeline

Every job you track moves through a forward-only stage sequence:

```
Saved → Applied → Phone Screen → Technical → Onsite → Offer → Accepted
```

From any active stage you can also move to a terminal state: `Rejected`, `Declined`, or `Ghosted`.

HeadHunter enforces forward-only movement. To correct a mistaken stage, use `crud.js update` (a patch), not `move`.

---

## Candidate profile

Your profile (`data/candidate-profile.json`) is the engine behind CV tailoring, job scoring, and salary negotiation. It holds:

- Personal info: name, email, LinkedIn, GitHub
- CV text (paste or extracted from a file)
- Experience: current title, years, skills
- Preferences: target roles, remote type, deal-breakers, excluded companies
- Salary: target base, floor (in your preferred currency)
- Priority weights: comp / growth / WLB / tech / mission (1–10)

Set it up with `/headhunter:setup`. Once it's populated, every scan, CV tailoring, and negotiation brief is personalized to you.

---

## Skills

HeadHunter's intelligence lives in **skills** — workflow instruction files loaded automatically by the plugin. Each skill orchestrates the right combination of subagents, scripts, and MCP tools to complete a job-search task.

| Skill | Command | What it does |
|-------|---------|-------------|
| `headhunter-core` | (always loaded) | CRM CRUD, pipeline view, search/filter |
| `job-discovery` | `/headhunter:discover` | Multi-board job search with relevance scoring |
| `job-scanner` | `/headhunter:scan` | Match Score + Success Score for any posting |
| `application-assistant` | `/headhunter:apply` | Tailored CV (A4 HTML) + cover letter |
| `cv-optimizer` | `/headhunter:cv-review` | ATS score, keyword gaps, LinkedIn audit |
| `interview-brief` | `/headhunter:brief` | 6-section Intel brief with salary script |
| `interview-research` | `/headhunter:research` | Deep study guide (multi-agent + OpenAI) |
| `interview-prep` | `/headhunter:prep` | Pre-assessment + prep brief from study guide |
| `mock-interview` | `/headhunter:mock` | Live mock with per-answer scoring |
| `job-scanner` | `/headhunter:insights` | Post-interview performance + next-round prediction |
| `salary-negotiation` | `/headhunter:negotiate` | Counter-offer script with market anchoring |
| `network-finder` | `/headhunter:network` | Contact map + personalized outreach |
| `follow-up` | `/headhunter:followup` | Draft follow-up emails for stale applications |
| `gmail-status-scan` | `/headhunter:scan` | Classify inbox → detect pipeline status changes |

---

## Subagents

Skills spawn **subagents** for focused tasks: `job-analyzer`, `study-guide-writer`, `mock-interviewer`, `cv-tailor`, `cover-letter-writer`, etc. You don't invoke subagents directly — skills orchestrate them automatically.

---

## MCP integrations

Optional MCP servers extend HeadHunter's reach:

| MCP | Purpose |
|-----|---------|
| Gmail | Inbox scanning + follow-up sends |
| Google Calendar | Interview scheduling + reminders |
| Notion | Application + task sync |
| GitHub | Candidate profile import, company research |
| LinkedIn (community ⚠️) | Job search, company pages |

Configure environment variables in `.env` (see `.env.example`). All integrations degrade gracefully — HeadHunter works fully offline without them.

---

## Scripts vs MCP

HeadHunter uses both:

- **Scripts** (`scripts/*.js`) — deterministic batch operations (sync, export, backup, scoring). Run without an AI in the loop. Support `--dry-run`.
- **MCP** — conversational, one-off operations inside the AI session (read one email, browse a Notion page, fetch a GitHub profile).

Rule: use scripts for anything you'd put in a cron job; use MCP for ad-hoc interactive work.
