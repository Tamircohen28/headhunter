// Research run layout: data/research/<slug>/ (flat files, not app_* ids).
const fs = require("fs");
const path = require("path");
const { DATA_DIR, nowISO } = require("./lib");

const RESEARCH_DIR = path.join(DATA_DIR, "research");

const FILES = {
  manifest: "00_run.json",
  scraperPrompt: "01_job_scraper.md",
  jobDescription: "01_job_description.md",
  analyzerPrompt: "02_job_analyzer.md",
  jobMetadata: "02_job_metadata.json",
  studyGuide: "04_study_guide.md",
};

function slugify(text) {
  return String(text || "job")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80) || "job";
}

function researchBatchFiles(batchNum) {
  const nn = String(batchNum).padStart(2, "0");
  return {
    prompt: `${nn}-research-prompt.md`,
    report: `${nn}-research-report.md`,
    reportPdf: `${nn}-research-report.pdf`,
  };
}

/** Appended to Deep Research prompts when --pdf is used (Code Interpreter PDF). */
function buildPdfDeliverableInstructions({ batchLabel }) {
  return `

PDF DELIVERABLE (mandatory):
After completing web research, use the code_interpreter tool to produce a polished A4 PDF report${batchLabel ? ` for ${batchLabel}` : ""}:
- Title block with role and company; table of contents for every numbered topic in this batch
- Body sections use the topic numbers from "Main topics to research" (e.g. "## 3. Topic title", "### 3.1 Subtopic")
- Readable typography (11–12pt body), margins, page breaks before each main topic
- Preserve citations and URLs where possible
Save exactly one PDF in the container named \`research_report.pdf\` (use reportlab, fpdf2, or matplotlib PdfPages).
The PDF is the primary artifact; also include a short markdown summary in your final message.
`;
}

function studyGuidePromptFile(batchNumAfterResearch) {
  const nn = String(batchNumAfterResearch).padStart(2, "0");
  return `${nn}-study-guide-prompt.md`;
}

function resolveResearchDir(arg) {
  if (!arg) throw new Error("research dir required");
  let p = arg;
  if (!path.isAbsolute(p)) {
    p = p.replace(/^data[\\/]research[\\/]/, "");
    p = path.join(RESEARCH_DIR, p);
  }
  if (!fs.existsSync(p)) throw new Error(`Research directory not found: ${p}`);
  return p;
}

function relativeResearchPath(absDir) {
  const rel = path.relative(DATA_DIR, absDir);
  return rel.startsWith("..") ? absDir : path.join("data", "research", path.basename(absDir)).split(path.sep).join("/");
}

function loadManifest(dir) {
  const f = path.join(dir, FILES.manifest);
  if (!fs.existsSync(f)) throw new Error(`Missing ${FILES.manifest} in ${dir}`);
  return JSON.parse(fs.readFileSync(f, "utf8"));
}

function saveManifest(dir, manifest) {
  fs.writeFileSync(path.join(dir, FILES.manifest), JSON.stringify(manifest, null, 2) + "\n");
}

function writeFile(dir, name, content) {
  const text = content.endsWith("\n") ? content : content + "\n";
  fs.writeFileSync(path.join(dir, name), text);
}

function readFile(dir, name) {
  const f = path.join(dir, name);
  if (!fs.existsSync(f)) throw new Error(`Missing ${name} in ${dir}`);
  return fs.readFileSync(f, "utf8");
}

function readArgContent(arg) {
  if (!arg) return "";
  if (arg.startsWith("@")) {
    const f = arg.slice(1);
    if (!fs.existsSync(f)) throw new Error(`File not found: ${f}`);
    return fs.readFileSync(f, "utf8");
  }
  return arg;
}

function pickResearchSlug(requested, { force }) {
  const base = slugify(requested);
  const target = path.join(RESEARCH_DIR, base);
  if (!fs.existsSync(target)) return { slug: base, dir: target, created: true };
  if (force) return { slug: base, dir: target, created: false, overwrite: true };
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const slug = `${base}-${ts}`;
  return { slug, dir: path.join(RESEARCH_DIR, slug), created: true };
}

function initResearch({ appId, slug, jobUrl, company, role, force }) {
  if (!fs.existsSync(RESEARCH_DIR)) fs.mkdirSync(RESEARCH_DIR, { recursive: true });
  const picked = pickResearchSlug(slug || `${company}-${role}`, { force: !!force });
  if (picked.created || picked.overwrite) fs.mkdirSync(picked.dir, { recursive: true });

  const manifest = {
    pipeline: "interview-research",
    application_id: appId,
    slug: picked.slug,
    company: company || null,
    role: role || null,
    job_url: jobUrl || null,
    started_at: nowISO(),
    finished_at: null,
    research_batches: [],
    study_guide: FILES.studyGuide,
    files: FILES,
  };
  saveManifest(picked.dir, manifest);

  return {
    slug: picked.slug,
    dir: picked.dir,
    dir_rel: relativeResearchPath(picked.dir),
    study_guide_path: path.join(picked.dir, FILES.studyGuide),
    study_guide_rel: `${relativeResearchPath(picked.dir)}/${FILES.studyGuide}`,
  };
}

function allocateBatchNumber(dir) {
  const m = loadManifest(dir);
  const used = new Set((m.research_batches || []).map((b) => b.number));
  let n = 3;
  while (used.has(n)) n++;
  return n;
}

/** Standard interview-prep subsections (matches reference PDF style). */
const RESEARCH_SUBSECTIONS = [
  { key: "core", label: "Core Concepts and Definitions", patterns: [/core concepts/i] },
  { key: "relevance", label: "Why It Matters for This Role and Company", patterns: [/why it matters/i] },
  { key: "questions", label: "Likely Interview Questions", patterns: [/likely interview/i] },
  { key: "answers", label: "Worked Answers and Examples", patterns: [/worked answers/i] },
  { key: "resources", label: "Curated Resources", patterns: [/curated resources/i] },
];

function buildTopicIndex(topicLearningOrder, topicHierarchy) {
  const topics = topicLearningOrder || [];
  return topics.map((title, i) => {
    const num = i + 1;
    const subs = (topicHierarchy && topicHierarchy[title]) || [];
    return {
      num,
      title,
      subtopics: subs.map((sub, j) => ({ num: `${num}.${j + 1}`, label: sub })),
      subsections: RESEARCH_SUBSECTIONS.map((s, j) => ({
        num: `${num}.${j + 1}`,
        label: s.label,
        key: s.key,
      })),
    };
  });
}

function topicStartIndex(topicLearningOrder, batchTopics) {
  if (!batchTopics || !batchTopics.length) return 1;
  const first = batchTopics[0];
  const idx = (topicLearningOrder || []).indexOf(first);
  return idx >= 0 ? idx + 1 : 1;
}

function formatNumberedTopicsBlock(topics, subtopicsByTopic, startIndex = 1) {
  let n = startIndex;
  return topics.map((t) => {
    const subs = (subtopicsByTopic && subtopicsByTopic[t]) || [];
    const main = `${n}. **${t}**`;
    n += 1;
    if (!subs.length) return main;
    const subLines = subs.map((s, j) => `   ${n - 1}.${j + 1} ${s}`);
    return `${main}\n${subLines.join("\n")}`;
  }).join("\n");
}

function registerBatch(dir, batchNum, topics) {
  const m = loadManifest(dir);
  const files = researchBatchFiles(batchNum);
  m.research_batches = m.research_batches || [];
  const entry = {
    number: batchNum,
    topics: topics || [],
    prompt: files.prompt,
    report: files.report,
    report_pdf: files.reportPdf,
    recorded_at: nowISO(),
  };
  const idx = m.research_batches.findIndex((b) => b.number === batchNum);
  if (idx >= 0) m.research_batches[idx] = entry;
  else m.research_batches.push(entry);
  saveManifest(dir, m);
  return { batchNum, files };
}

function buildDeepResearchPrompt({
  company,
  role,
  jobUrl,
  topics,
  subtopicsByTopic,
  location,
  topicLearningOrder,
  startTopicNum,
}) {
  const start = startTopicNum != null
    ? startTopicNum
    : (topicLearningOrder ? topicStartIndex(topicLearningOrder, topics) : 1);
  const topicBlock = formatNumberedTopicsBlock(topics, subtopicsByTopic, start);

  return `Research topic:
Interview preparation for ${role} at ${company}${location ? ` (${location})` : ""}.
Job posting: ${jobUrl || "(see internal job description file)"}

Audience:
A senior software candidate preparing for technical and hiring-manager interviews.

Geography:
${location || "Role location as stated in job posting; include Israel/global NVIDIA context if relevant."}

Time range:
Prioritize sources from 2024–2026; foundational docs may be older.

Sources to prioritize:
- Official documentation (vendor, standards bodies)
- Engineering blogs from reputable companies
- Academic papers and conference talks
- Credible interview experience writeups (Glassdoor, Blind, engineering blogs)
- NVIDIA and semiconductor/EDA ecosystem sources where relevant

Sources to avoid:
- Unsourced affiliate listicles
- Generic SEO spam
- Unverified rumor posts

Output format:
Markdown report with ## per main topic (use the topic number from the list, e.g. "## 3. Python for production AI and tooling") and ### per numbered sub-topic (e.g. "### 3.1 Type hints and pydantic models").

Required sections (for EACH sub-topic section, use ### headings):
1. Core concepts and definitions (technically precise)
2. Why it matters for this specific role and company
3. Likely interview questions (technical and behavioral where relevant)
4. Worked answers / examples (code or diagrams in markdown when useful)
5. Curated resources with URLs

Citation requirements:
Cite sources for major factual claims. Mark unknowns explicitly — do not invent company-internal details.

Decision criteria:
Depth over breadth; prefer specifics tied to ${company}'s domain (${role}).

Main topics to research:
${topicBlock}
`;
}

function finishResearch(dir, { appId }) {
  const m = loadManifest(dir);
  const guide = path.join(dir, FILES.studyGuide);
  if (!fs.existsSync(guide)) {
    throw new Error(`Missing ${FILES.studyGuide}. Run study-guide-writer and save output first.`);
  }
  m.finished_at = nowISO();
  saveManifest(dir, m);
  const rel = relativeResearchPath(dir);
  return {
    dir_rel: rel,
    study_guide_rel: `${rel}/${FILES.studyGuide}`,
    appId: appId || m.application_id,
  };
}

module.exports = {
  RESEARCH_DIR,
  FILES,
  RESEARCH_SUBSECTIONS,
  slugify,
  researchBatchFiles,
  studyGuidePromptFile,
  buildTopicIndex,
  topicStartIndex,
  formatNumberedTopicsBlock,
  resolveResearchDir,
  relativeResearchPath,
  loadManifest,
  saveManifest,
  writeFile,
  readFile,
  readArgContent,
  initResearch,
  allocateBatchNumber,
  registerBatch,
  buildDeepResearchPrompt,
  buildPdfDeliverableInstructions,
  finishResearch,
};
