---
description: Generate a full Interview Intel briefing for a recruiter screen or first interview. Pass a job URL, pasted description, company name, or recruiter message.
allowed-tools: Read, Bash, WebFetch, WebSearch, Glob, Task
---

# Interview Brief

Run the `interview-brief` skill for the job in `$ARGUMENTS`.

Follow the `interview-brief` skill end-to-end:
1. Resolve input (URL → WebFetch, file → Read, text/name → proceed).
2. Load `data/candidate-profile.json` if it exists (personalization).
3. Run Section 1–6 research and generate the full briefing.
4. After presenting, offer to:
   - Save as a note (`crud.js add notes`) on the matched/created application.
   - Add prep tasks from the "Fast Prep Plan".
   - Run `/jobtrack:research` for the deep multi-agent study guide.
