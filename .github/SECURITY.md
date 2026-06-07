# Security Policy

## Data privacy

HeadHunter is designed to keep your job-search data **local and private**:

- `data/` is gitignored — your pipeline, CV text, and salary figures never leave your machine unless you explicitly sync them.
- `.env` is gitignored — API keys and OAuth tokens should live there only.
- All external syncs (Notion, Todoist, Google, Twilio) require explicit `--dry-run` before writing and print what they will do first.

## Credentials

- Copy `.env.example` to `.env` and fill in your keys. Never commit `.env`.
- `OPENAI_API_KEY`, `GOOGLE_OAUTH_TOKEN`, `GITHUB_PERSONAL_ACCESS_TOKEN`, `NOTION_TOKEN`, Twilio credentials, and LinkedIn credentials are all optional and only needed for the specific integrations that use them.
- The LinkedIn MCP (`mcp-linkedin`) is a community package with a prominent ToS warning in `.mcp.json`. Review before enabling.

## Reporting a vulnerability

If you discover a security issue in this project, please report it by opening a [GitHub Issue](https://github.com/TamirCohen28/headhunter/issues) with the label `security`. For sensitive findings, you can also reach the maintainer directly via GitHub at [@TamirCohen28](https://github.com/TamirCohen28).

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

## Supply chain

The core CRM (`scripts/*.js`) has **no npm runtime dependencies** — it runs on Node.js built-ins only. This minimizes supply-chain risk for the layer that holds your job-search data. Optional integrations (`deep-research.js`, `generate-research-pdf.js`) use network calls but no local package installs.
