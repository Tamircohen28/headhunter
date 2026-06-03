---
description: Run a mock interview session for a specific round — the AI interviewer asks questions, evaluates your answers, and gives targeted feedback. Pass a company name, app ID, or "next interview".
allowed-tools: Read, Write, Bash, Glob, Task
---

# Mock Interview

Run the `mock-interview` skill for the application in `$ARGUMENTS`.

Follow the `mock-interview` skill end-to-end:
1. Load application + candidate profile + study guide.
2. Pre-assessment: 4 questions about strengths, weak areas, focus, round type + difficulty.
3. Spawn mock-interviewer agent — interactive Q&A session (5–10 questions).
4. Save session results to interview prep notes.
5. Offer follow-up tasks and next steps.
