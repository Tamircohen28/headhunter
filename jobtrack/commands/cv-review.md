---
description: Review your CV and LinkedIn profile — ATS score, keyword gaps, bullet improvements, LinkedIn headline and summary audit.
allowed-tools: Read, Bash, Glob, Task
---

# CV + LinkedIn Review

Run the `cv-optimizer` skill.

Follow the `cv-optimizer` skill end-to-end:
1. Load candidate profile (exit early if no CV text — suggest `/jobtrack:setup`).
2. Check for LinkedIn content (MCP or pasted).
3. Spawn cv-reviewer + linkedin-auditor agents in parallel.
4. Present combined report with ATS score, keyword gaps, bullet improvements, LinkedIn audit.
5. Show combined priority action list.
6. Offer to save review as a note.
