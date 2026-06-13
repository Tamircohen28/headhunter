#!/usr/bin/env node
// SessionStart hook: checks for missing optional env vars and surfaces
// step-by-step setup instructions for any that are absent.
// Silent no-op when all vars for a group are set.
// Never blocks session start (run with continueOnBlock: true).

const GROUPS = [
  {
    name: "Notion integration",
    vars: ["NOTION_TOKEN", "NOTION_DATABASE_ID", "NOTION_TASKS_DATABASE_ID"],
    instructions: [
      "1. Go to https://www.notion.so/my-integrations → '+ New integration'",
      "2. Name it 'HeadHunter', select your workspace, click Submit",
      "3. Copy the 'Internal Integration Secret' (starts with secret_...)",
      "4. Open your HeadHunter Applications database in Notion → '...' menu → 'Connect to' → select HeadHunter",
      "5. Repeat for your Tasks database",
      "6. Copy each database ID from its URL: notion.so/<workspace>/<DATABASE_ID>?v=...",
      "7. Add to ~/.zshrc:",
      "   export NOTION_TOKEN=secret_...",
      "   export NOTION_DATABASE_ID=<applications-db-id>",
      "   export NOTION_TASKS_DATABASE_ID=<tasks-db-id>",
      "   source ~/.zshrc",
    ],
  },
  {
    name: "Google Calendar integration",
    vars: ["GOOGLE_OAUTH_TOKEN", "GOOGLE_CALENDAR_ID"],
    instructions: [
      "HeadHunter uses the official claude.ai Google Calendar MCP — no extra tokens needed.",
      "To set a specific calendar ID (optional, defaults to 'primary'):",
      "   export GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com",
      "   source ~/.zshrc",
      "To find your calendar ID: Google Calendar → Settings → select calendar → 'Calendar ID'",
    ],
  },
  {
    name: "Google Tasks integration",
    vars: ["GOOGLE_TASKS_LIST_ID"],
    instructions: [
      "To sync tasks to Google Tasks, set your task list ID:",
      "   export GOOGLE_TASKS_LIST_ID=<your-task-list-id>",
      "   source ~/.zshrc",
      "To find your task list ID, use the Google Tasks API explorer:",
      "   https://developers.google.com/tasks/reference/rest/v1/tasklists/list",
    ],
  },
  {
    name: "Todoist integration",
    vars: ["TODOIST_API_TOKEN"],
    instructions: [
      "1. Go to https://todoist.com/app/settings/integrations/developer",
      "2. Copy your API token",
      "3. Add to ~/.zshrc:",
      "   export TODOIST_API_TOKEN=your_token_here",
      "   source ~/.zshrc",
    ],
  },
  {
    name: "WhatsApp reminders (via Twilio)",
    vars: ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM", "WHATSAPP_TO"],
    instructions: [
      "1. Create a Twilio account at https://www.twilio.com",
      "2. Enable WhatsApp Sandbox: Console → Messaging → Try it out → Send a WhatsApp message",
      "3. Find your Account SID and Auth Token at https://console.twilio.com",
      "4. Add to ~/.zshrc:",
      "   export TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "   export TWILIO_AUTH_TOKEN=your_auth_token",
      "   export TWILIO_WHATSAPP_FROM=whatsapp:+14155238886  # Twilio sandbox number",
      "   export WHATSAPP_TO=whatsapp:+972XXXXXXXXX          # your number with country code",
      "   source ~/.zshrc",
    ],
  },
  {
    name: "OpenAI (for deep research)",
    vars: ["OPENAI_API_KEY"],
    instructions: [
      "Required for the /headhunter:research deep-research pipeline.",
      "1. Go to https://platform.openai.com/api-keys → '+ Create new secret key'",
      "2. Add to ~/.zshrc:",
      "   export OPENAI_API_KEY=sk-...",
      "   source ~/.zshrc",
      "Optional — override the model used for deep research (defaults to o3-mini):",
      "   export OPENAI_DEEP_RESEARCH_MODEL=o3",
    ],
  },
  {
    name: "LinkedIn MCP (unofficial)",
    vars: ["LINKEDIN_EMAIL", "LINKEDIN_PASSWORD"],
    instructions: [
      "⚠  Unofficial community MCP — may violate LinkedIn ToS. Use at your own risk.",
      "Add to ~/.zshrc:",
      "   export LINKEDIN_EMAIL=you@email.com",
      "   export LINKEDIN_PASSWORD=yourpassword",
      "   source ~/.zshrc",
      "Or remove the linkedin block from the plugin's .mcp.json to silence this warning.",
    ],
  },
];

function emit(context) {
  process.stdout.write(
    JSON.stringify({
      reloadSkills: false,
      hookSpecificOutput: {
        hookEventName: "SessionStart",
        additionalContext: context,
      },
    })
  );
}

const missing = GROUPS.filter((g) => g.vars.some((v) => !process.env[v]));

if (missing.length === 0) process.exit(0);

const lines = ["⚠  HeadHunter: optional integrations need setup:"];
for (const g of missing) {
  const unset = g.vars.filter((v) => !process.env[v]);
  lines.push("");
  lines.push(`  ${g.name} — missing: ${unset.map((v) => `$${v}`).join(", ")}`);
  for (const line of g.instructions) lines.push(`  ${line}`);
}
lines.push("");
lines.push("  Run /headhunter:settings to see current config. These are all optional — HeadHunter works without them.");

emit(lines.join("\n"));
