# Deep Research prompt template

Used by `pipeline-run.js batch` and `scripts/deep-research.js`. The API does **not** ask clarifying questions — specify everything up front.

```text
Research topic:
Interview preparation for {role} at {company} ({location}).

Audience:
A senior candidate preparing for technical and hiring-manager interviews.

Geography:
{location or "As stated in job posting"}

Time range:
Prioritize 2024–2026 sources; foundational references may be older.

Sources to prioritize:
- Official documentation and vendor engineering blogs
- Standards bodies and academic papers where relevant
- Credible interview experience reports
- Company and industry-specific engineering content

Sources to avoid:
- Unsourced affiliate rankings
- Generic SEO content

Output format:
Markdown with ## per main topic, ### per sub-topic.

Required sections (each main topic):
1. Core concepts and definitions
2. Why it matters for this role and company
3. Likely interview questions
4. Worked answers / examples
5. Resources with URLs

Citation requirements:
Cite major claims. Mark unknowns — do not invent internal company details.

Main topics:
- {topic 1}
  Sub-topics: …
```

## API invocation

```bash
node scripts/deep-research.js --dir data/research/<slug> --batch 03
```

Uses OpenAI **Responses API** with `background: true`, `web_search_preview`, and `max_tool_calls: 50`. See [OpenAI Deep Research docs](https://developers.openai.com/api/docs/guides/deep-research).

### PDF output (not native)

The Deep Research API returns **markdown text only** — there is no `output_format: pdf`. ChatGPT’s “Download as PDF” is a **UI feature**, not available on the API.

To get PDFs programmatically, use **`--pdf`**, which also enables **code_interpreter** and instructs the model to render `research_report.pdf` in its container. The script downloads it to `NN-research-report.pdf` via [container file content](https://platform.openai.com/docs/api-reference/container-files).

```bash
OPENAI_API_KEY=... node scripts/deep-research.js --dir data/research/<slug> --batch 03 --pdf
node scripts/merge-research-pdfs.js --dir data/research/<slug>
```

Merge batch PDFs locally (no re-render from markdown). Requires network once for `npx -p pdf-lib`.
