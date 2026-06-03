---
description: Generate a tailored CV and cover letter for a job application, or answer application form questions. Pass an application ID, company name, or job URL.
allowed-tools: Read, Write, Bash, Glob, Task
---

# Apply to a Job

Run the `application-assistant` skill for the application in `$ARGUMENTS`.

If `$ARGUMENTS` contains a question (e.g. "how do I answer the salary field?"), use Mode B (Q&A advisor) directly.

Otherwise, follow Mode A end-to-end:
1. Load candidate profile + job context.
2. Spawn cv-tailor + cover-letter-writer agents in parallel.
3. Generate styled HTML CV via `generate-cv-html.js`.
4. Save outputs; update application record.
5. Present results + submission checklist.
