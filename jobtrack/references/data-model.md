# JobTrack Data Model (source of truth)

All entities are persisted as JSON under `${CLAUDE_PLUGIN_ROOT}/data/`:

- `applications.json` — array of JobApplication
- `interviews.json` — array of InterviewRound
- `tasks.json` — array of Task
- `contacts.json` — array of Contact
- `notes.json` — array of Note

Every record has a generated `id` (string, e.g. `app_<timestamp>_<rand>`),
plus `created_date` and `updated_date` (ISO 8601). Any write MUST bump
`updated_date`.

## Storage backend preference

1. **Base44 MCP / API** — if `VITE_BASE44_APP_ID` + token are set, use the
   same entities as the web app.
2. **Local JSON store** (default) — `${CLAUDE_PLUGIN_ROOT}/data/*.json`.
3. **Notion databases** — when Notion MCP connected (see integrations).

## JobApplication

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | auto | |
| company | string | yes | |
| role | string | yes | Job title |
| job_url | string | | Original posting URL |
| status | enum | | Default `Saved`. Saved, Applied, Phone Screen, Technical, Onsite, Offer, Accepted, Declined, Rejected, Ghosted |
| priority | enum | | High, Medium, Low (default Medium) |
| applied_date | date | | ISO date |
| source | string | | LinkedIn, Referral, Company Site, etc. |
| salary_min | number | | |
| salary_max | number | | |
| currency | string | | Default USD |
| location | string | | |
| remote_type | enum | | Remote, Hybrid, On-site |
| job_description | string | | Markdown OK |
| requirements | string | | Markdown OK |
| color_label | string | | Hex for Kanban accent |
| notion_page_id | string | | Set after Notion sync |
| research_dir | string | | Path to interview-research output (set by the pipeline) |
| last_research_at | datetime | | When the interview-research pipeline last ran |
| created_date | datetime | auto | |
| updated_date | datetime | auto | bump on every write |

## InterviewRound

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | auto | |
| application_id | string | yes | FK → JobApplication |
| round_number | number | | Auto-increment per app |
| round_type | enum | yes | Recruiter Call, Phone Screen, Technical, System Design, Behavioral, Take-Home, Onsite, Panel, Final, Reference Check |
| scheduled_at | datetime | | |
| duration_minutes | number | | Default 60 |
| interviewer_name | string | | |
| interviewer_linkedin | string | | |
| google_calendar_event_id | string | | |
| google_meet_link | string | | |
| status | enum | | Scheduled, Completed, Cancelled, No-show |
| outcome | enum | | Pending, Passed, Failed, Cancelled |
| prep_notes | string | | |
| reflection_notes | string | | |
| difficulty_rating | number | | 1–5 |
| vibe_rating | number | | 1–5 |
| prep_checklist | array | | `{ id, text, done }[]` |
| questions_asked | string | | |
| my_answers | string | | |
| what_went_well | string | | |
| what_went_poorly | string | | |
| overall_feeling | enum | | Great, Good, Neutral, Nervous, Poor |
| key_takeaways | string | | |

## Task

| Field | Type | Notes |
|-------|------|-------|
| id | string | auto |
| application_id | string | Optional FK |
| title | string | Required |
| description | string | |
| due_date | datetime | |
| priority | enum | High, Medium, Low |
| completed | boolean | Default false |
| google_task_id | string | Sync ID |
| todoist_task_id | string | Sync ID |
| notion_task_page_id | string | Sync ID |
| reminder_sent | boolean | |

## Contact

| Field | Type | Required |
|-------|------|----------|
| id | string | auto |
| application_id | string | yes |
| name | string | yes |
| role_at_company | string | Recruiter, Hiring Manager, etc. |
| email | string | |
| phone | string | |
| linkedin_url | string | |
| notes | string | |

## Note

| Field | Type | Required |
|-------|------|----------|
| id | string | auto |
| application_id | string | yes |
| interview_round_id | string | optional |
| content | string | yes |
| note_type | enum | General, Follow-Up, Offer Details, Rejection Reason, Research |

## Event (auto-logged, powers the Timeline)

Written automatically by `crud.js` on create/move/complete — not edited by hand.

| Field | Type | Notes |
|-------|------|-------|
| id | string | auto |
| ts | datetime | when it happened |
| type | string | application_created, status_change, interview_added, task_added, task_completed, note_added |
| application_id | string | FK → JobApplication |
| summary | string | human-readable line |
| meta | object | type-specific (e.g. `{from, to}` for status_change) |
