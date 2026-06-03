---
name: mock-interview
description: Run a realistic mock interview session for a specific round — the interviewer asks questions, evaluates your answers, gives feedback, and produces a performance summary. Triggers on mock interview, practice interview, mock session, interview practice, test my answers, drill me.
allowed-tools: Read, Write, Bash, Glob, Task
---

# Mock Interview

Run an interactive mock interview session tied to a real application.

## Step 0 — Load context

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/candidate-profile.js show
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list applications --json
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list interviews --json
```

Resolve the target application from `$ARGUMENTS` (app ID, company name, or "next interview").

If there's a scheduled upcoming interview, default to that round type. Otherwise ask.

## Step 1 — Pre-assessment (4 questions, answer in one message)

Ask the user:

1. **Which topics feel strongest?** (e.g. system design, Go, behavioral storytelling)
2. **Which feel weakest or most uncertain?** (e.g. DP algorithms, salary negotiation, conflict stories)
3. **What do you most want this session to focus on?** (weak areas? confirming strong areas? full realistic simulation?)
4. **Round type and difficulty?**
   - Round: Recruiter / Technical / System Design / Behavioral / Final
   - Difficulty: Easy / Medium / Hard (default Medium)
   - Number of questions: 5 (quick) / 8 (standard) / 10 (deep)

Use answers to configure the mock-interviewer agent.

## Step 2 — Load study guide (if available)

If the application has a `research_dir`, read `<research_dir>/04_study_guide.md` and extract the top topics and question patterns. Pass a summary to the mock-interviewer so questions are role-specific, not generic.

## Step 3 — Spawn mock-interviewer agent

```
Task: mock-interviewer
Input: {
  "application": {"company": "...", "role": "...", "round_type": "Technical"},
  "candidate_profile": {"current_title": "...", "years": 7, "key_skills": [...]},
  "study_guide_summary": "<top 5 topics and likely questions from study guide>",
  "self_assessment": {"strong": [...], "weak": [...], "focus": "..."},
  "difficulty": "Medium",
  "num_questions": 8
}
```

The agent runs the full interactive session. It asks one question at a time and waits for the user to respond in the conversation. Claude relays each exchange naturally.

## Step 4 — After the session

When the mock-interviewer produces its session summary JSON:

1. Save results to the interview record if one exists:
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js update interviews <id> \
     '{"prep_notes":"Mock session verdict: <verdict>. Strengths: <list>. Improve: <list>"}'
   ```

2. Offer to:
   - Add prep tasks for the improvement areas → `/jobtrack:add-task`
   - Run another session with a different focus
   - Start the full research pipeline → `/jobtrack:research`
