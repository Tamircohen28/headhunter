---
description: Scan a job posting and get Match Score + Success Score against your profile. Pass a URL, pasted JD, or application ID.
allowed-tools: Read, Bash, WebFetch, WebSearch, Glob, Task
---

# Scan a Job

Run the `job-scanner` skill for the job in `$ARGUMENTS`.

Follow the `job-scanner` skill end-to-end:
1. Load candidate profile (exit early if missing — suggest `/jobtrack:setup`).
2. Resolve input → job-analyzer → structured metadata.
3. Deterministic pre-score via `score-job.js`.
4. Company selectivity research.
5. job-scorer agent → Match Score + Success Score + verdict.
6. Display full scanner report with score bars and gap analysis.
7. Save scores to application record; offer next steps (apply, brief, research, skip).
