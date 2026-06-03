# Interview-Research Pipeline

This is the HeadHunter interview-prep pipeline, implemented using Claude Code
subagents instead of Python + the OpenAI API. There is **no Python and no
OpenAI dependency** — orchestration is done by the `interview-research` skill
spawning subagents in parallel (the same "divide topics among agents" pattern
the Python `TaskExecutor` used), and `WebSearch`/`WebFetch` replace the
Playwright scraper and the browsing model.

Output attaches to the **headhunter store**: each run is tied to a
`JobApplication` and written under `data/research/<application_id>/`.

## Stage map (input → work → output)

### Stage 1 — Scrape (was: JobScrapingStep / Playwright)
- **Input:** `job_url` (or pasted job description).
- **Work:** `WebFetch` the URL and extract the job posting text. Fallback:
  ask the user to paste the description if the page can't be fetched.
- **Output:** `data/research/<appId>/01_job_description.md` (cleaned text,
  100–50,000 chars, like the original validation).

### Stage 2 — Analyze + research (was: JobAnalysisStep / gpt-4o-mini browsing)
- **Agent:** `job-analyzer`.
- **Input:** scraped description + URL.
- **Work:** extract structured metadata AND web-research the company:
  Glassdoor/interview experiences, hiring process & stages, technical question
  patterns by domain, behavioral questions, prep tips & pitfalls.
- **Output:** `data/research/<appId>/02_job_metadata.json` matching the
  JobMetadata schema below — critically the **`topic_hierarchy`**
  (15–25 main topics for senior roles, each with 5–10 technical sub-topics),
  `topic_learning_order`, and `topic_dependencies`.

### Stage 3 — Divide & research topics (was: commented ResearchPromptStep + TaskExecutor)
- **Agent:** `topic-researcher` (spawned N times **in parallel**).
- **Division rule:** split the `topic_hierarchy` main topics into batches of
  `MAX_TOPICS_PER_AGENT` (default **4**). N = ceil(topics / 4). Respect
  `topic_learning_order` when batching so prerequisites land in earlier batches.
- **Work per agent:** for each assigned main topic + its sub-topics, produce
  deep study notes: concepts/definitions, why it matters for THIS role,
  likely interview questions, worked answers/examples, and curated resources.
- **Output:** `data/research/<appId>/03_topic_<k>.md` per agent.

### Stage 4 — Merge into study guide (was: consolidation)
- **Agent:** `study-guide-writer`.
- **Input:** metadata + all `03_topic_*.md`.
- **Work:** merge into a single ordered study guide and a time-boxed plan
  using `STUDY_WEEKS` (default 4) × `HOURS_PER_WEEK` (default 10), plus a
  one-page interview cheat-sheet (top questions + STAR prompts).
- **Output:** `data/research/<appId>/04_study_guide.md` and `00_run.json`
  (run manifest). The application record is updated with `research_dir` and
  `last_research_at`.

## Config (from settings.json → headhunter.research)

| Param | Default | Meaning |
|-------|---------|---------|
| `studyWeeks` | 4 | study plan length |
| `hoursPerWeek` | 10 | study intensity |
| `maxTopicsPerAgent` | 4 | topics per research subagent (division size) |
| `minTopics` / `maxTopics` | 15 / 25 | topic-hierarchy size for senior roles |

## JobMetadata schema (Stage 2 output)

```json
{
  "job_title": "string",
  "company_name": "string",
  "location": "string",
  "job_url": "string",
  "required_skills": ["..."],
  "preferred_skills": ["..."],
  "nice_to_have_skills": ["..."],
  "required_qualifications": ["..."],
  "hiring_stages": ["Recruiter Call", "Technical", "Onsite", "..."],
  "hiring_timeline": "string",
  "evaluation_criteria": ["..."],
  "technical_question_domains": { "Domain": ["question/topic", "..."] },
  "behavioral_questions": ["..."],
  "preparation_tips": ["..."],
  "common_pitfalls": ["..."],
  "topic_hierarchy": { "Main Topic": ["sub-topic 1", "sub-topic 2", "..."] },
  "topic_dependencies": { "Main Topic": ["prerequisite topic", "..."] },
  "topic_learning_order": ["Main Topic A", "Main Topic B", "..."],
  "study_resources": { "Topic or type": ["resource/url", "..."] }
}
```

Topic hierarchy requirements (from the original prompt): specific & technical,
include vendor tech where relevant (Intel, AMD, NVIDIA, cloud providers),
emerging trends, and a fundamentals→advanced progression; dependent topics
appear after their prerequisites.
