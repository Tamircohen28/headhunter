---
description: Set up or update your candidate profile — personal info, CV, target roles, salary expectations, deal breakers. Run once before using /jobtrack:brief or applying to jobs.
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Candidate Profile Setup

Guide the user through building or updating their candidate profile at
`data/candidate-profile.json`. This profile powers:
- `/jobtrack:brief` personalization (elevator pitch, salary guidance, emphasis/de-emphasis)
- Job filtering and recommendations
- Application auto-fill (cover letter, contact info)

## Step 0 — Check for existing profile

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js show
```

If a profile exists, show a summary and ask: "What would you like to update?" then jump to the relevant section. If no profile exists, run all sections in order.

## Step 1 — Personal information

Collect interactively (one field at a time or in a group — adapt to the user's pace):

- **Full name** — used in cover letters and applications
- **Email** — primary contact email
- **Phone** — with country code (Israel: +972)
- **LinkedIn URL** — your public profile
- **GitHub URL** — your public profile (optional)
- **Portfolio URL** — personal site, blog, or project (optional)
- **Location** — city (e.g. Tel Aviv, Herzliya, Ramat Gan)

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js set \
  '{"personal":{"name":"...","email":"...","phone":"...","linkedin_url":"...","location":"..."}}'
```

## Step 2 — CV / Resume

Ask: "Do you have a CV file to load, or would you prefer to paste your experience?"

**If file path given:**
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js extract-cv <path>
```
For PDFs: use the Read tool to read the file, extract the text, then save:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js set \
  '{"cv":{"file_path":"<path>","text":"<full extracted text>","last_updated":"<ISO now>"}}'
```

**If pasted text:**
Save directly:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js set \
  '{"cv":{"text":"<pasted>","last_updated":"<ISO now>"}}'
```

## Step 3 — Experience summary

Extract from the CV or ask:

- **Total years of experience**
- **Current title and company**
- **One-paragraph summary** (used in elevator pitch)
- **Top 10 key skills** (comma-separated)
- **Specializations** (e.g. distributed systems, ML infra, security)
- **Notable open source projects** (name + URL)
- **Certifications** (if any)
- **Education** (degree, institution)

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js set \
  '{"experience":{"years_total":8,"current_title":"Senior Backend Engineer","summary":"...","key_skills":["Go","Kubernetes","gRPC"]}}'
```

## Step 4 — Job preferences

Ask each:

- **Target roles** — titles you're open to (e.g. "Staff Engineer, Principal SWE, Tech Lead")
- **Target companies** — specific companies you want to work at (optional)
- **Exclude companies** — companies to skip entirely
- **Industries** — preferred industries (FinTech, AI/ML, SaaS, Defence, etc.)
- **Preferred locations** — cities or "Anywhere in Israel"
- **Remote type** — Remote / Hybrid / On-site / No preference
- **Company stage** — Startup (seed–Series B), Scale-up (Series C+), Enterprise, Public — pick all that apply
- **Company size** — 1–50 / 50–200 / 200–1000 / 1000+
- **Must-haves** — non-negotiable requirements (e.g. "fully remote", "no defence", "modern stack")
- **Deal breakers** — instant disqualifiers
- **Why you're looking now** — honest 1–2 sentences (used in interview answers)
- **3-year career goal** — where you want to be (used to filter senior/IC/management roles)

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js set \
  '{"preferences":{"target_roles":["Staff Engineer"],"remote_type":"Hybrid","must_haves":["equity"],"why_looking":"Ready for a bigger technical scope","career_goal_3yr":"Principal IC or small-team tech lead"}}'
```

## Step 5 — Salary expectations (ILS)

Ask:
- **Current base salary** (monthly gross ILS)
- **Current total comp** (including bonus, equity annualized)
- **Target base** (what you want to earn — monthly gross ILS)
- **Target total comp** (base + bonus + equity annualized)
- **Hard floor** (the minimum you'd accept — monthly gross ILS)
- **Notes** (e.g. "equity more important than base", "open to RSUs at growth stage")

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js set \
  '{"salary":{"current_base_ils":35000,"target_base_ils":45000,"floor_ils":38000,"notes":"equity matters"}}'
```

## Step 6 — Availability

- **Available from** (ISO date, or "immediately", or "after 60 days notice")
- **Notice period** (days)
- **Actively looking?** (yes/no)

## Step 7 — Application defaults

- **Cover letter template** (optional — with `{{company}}`, `{{role}}`, `{{reason}}` placeholders)
- **Languages** (e.g. ["Hebrew (native)", "English (fluent)"])
- **Visa / work authorization** (e.g. Citizen, Permanent Resident, Work Permit)

## Final confirmation

Show a formatted summary of the full profile. Ask: "Does this look correct? Anything to change?" Apply any corrections, then:

```
✓ Candidate profile saved to data/candidate-profile.json
→ Run /jobtrack:brief <job URL> to generate your first briefing.
→ Run /jobtrack:search to filter saved jobs against your preferences.
```
