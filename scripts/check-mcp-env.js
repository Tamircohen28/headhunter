#!/usr/bin/env node
// SessionStart hook: checks for missing optional MCP env vars and surfaces
// setup instructions for any that are absent. Silent no-op when all are set.

const MCP_CHECKS = [
  {
    server: "Notion MCP",
    vars: ["NOTION_TOKEN"],
    instructions: [
      "1. Go to https://www.notion.so/my-integrations → '+ New integration'",
      "2. Name it (e.g. 'HeadHunter'), select your workspace, submit",
      "3. Copy the 'Internal Integration Secret' (starts with secret_...)",
      "4. Add to your shell profile:",
      "   echo 'export NOTION_TOKEN=secret_...' >> ~/.zshrc && source ~/.zshrc",
      "5. Share each Notion database with the integration (open DB → ... → Connect to)",
    ],
  },
  {
    server: "LinkedIn MCP (unofficial)",
    vars: ["LINKEDIN_EMAIL", "LINKEDIN_PASSWORD"],
    instructions: [
      "⚠  The LinkedIn MCP is an unofficial community tool and may violate LinkedIn ToS.",
      "   Use your LinkedIn login credentials:",
      "   echo 'export LINKEDIN_EMAIL=you@email.com' >> ~/.zshrc",
      "   echo 'export LINKEDIN_PASSWORD=yourpassword' >> ~/.zshrc && source ~/.zshrc",
      "   Or remove the linkedin block from the plugin's .mcp.json to silence this warning.",
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

const missing = MCP_CHECKS.filter((c) => c.vars.some((v) => !process.env[v]));

if (missing.length === 0) process.exit(0);

const lines = ["⚠  HeadHunter: MCP servers need setup to connect:"];
for (const m of missing) {
  const unset = m.vars.filter((v) => !process.env[v]);
  lines.push("");
  lines.push(`  ${m.server} — missing: ${unset.map((v) => `$${v}`).join(", ")}`);
  for (const line of m.instructions) lines.push(`  ${line}`);
}

emit(lines.join("\n"));
