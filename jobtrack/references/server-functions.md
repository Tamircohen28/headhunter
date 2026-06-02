# Server Functions (integration logic to replicate)

These mirror the Base44 Deno backend functions. Implement via MCP tools when
a server is connected, otherwise via the REST scripts in `scripts/`.

## gmailJobScanner

**Trigger:** new Gmail messages (webhook) or manual `/scan gmail`.

1. Fetch message by ID via Gmail API (`format=full`).
2. Extract `subject`, `from`, `body` (recursive MIME walk, base64url decode).
3. Classify status via regex (first match wins, most-advanced first):

| Status | Pattern examples (case-insensitive) |
|--------|-------------------------------------|
| Offer | offer letter, pleased to offer, job offer, extend an offer |
| Onsite | onsite interview, final round, panel interview, on-site |
| Technical | technical interview, coding challenge, take-home, hackerrank |
| Phone Screen | phone screen, intro call, recruiter call, initial call |
| Rejected | unfortunately, not moving forward, regret to inform, decided to proceed with other |

4. Match application by `company` substring in subject/from/body (case-insensitive).
5. Update status **only if** it advances in pipeline **OR** new status is
   Rejected/Declined.

## syncInterviewToCalendar

**Trigger:** InterviewRound create/update with `scheduled_at`.

- Event title: `{round_type} Interview – {role} @ {company}`
- Description: prep_notes + meet link + interviewer name
- POST new event, or PUT existing if `google_calendar_event_id` set
- Store returned `event.id` on the interview as `google_calendar_event_id`

## syncApplicationToNotion

**Env:** `NOTION_DATABASE_ID`

- Properties: Company (title), Role, Status, Priority, Location, Source, Job URL, Applied Date
- PATCH if `notion_page_id` exists, else POST to database
- Save `notion_page_id` on the application (idempotent — never duplicate)

## syncTaskToNotion

**Env:** `NOTION_TASKS_DATABASE_ID`, per-user Notion OAuth

- Properties: Name, Status (checkbox), Priority, Description, Due Date, Application (rich text)

## syncTaskToGoogleTasks

**Env:** `GOOGLE_TASKS_LIST_ID` (default `@default`)

- Create/update task: title, notes, status, due date
- Save `google_task_id`

## syncTaskToTodoist

**Env:** `TODOIST_API_TOKEN`. **Trigger:** Task create.

- Content: `[{company}] {title}` when linked, else `{title}`
- Priority map: High→4, Medium→3, Low→2
- Skip if `todoist_task_id` already set (idempotent)

## sendStaleApplicationReminders

**Schedule:** daily.

- Find ACTIVE_STAGES apps not updated in 7+ days
- Group by user, send email via Core.SendEmail integration

## sendWhatsAppReminders

**Env:** `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`, `WHATSAPP_TO`. **Schedule:** daily.

- Interviews in next 24h with status Scheduled
- Overdue incomplete tasks
- Send formatted WhatsApp messages via Twilio
