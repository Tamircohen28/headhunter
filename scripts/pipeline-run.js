#!/usr/bin/env node
// Interview-research run under data/research/<slug>/ (flat prompt + output files).
//
//   init    — create data/research/<slug>/ + 00_run.json
//   write   — write any artifact (prompt before agent, output after)
//   batch   — register batch NN + write NN-research-prompt.md from template
//   refresh-prompts — rewrite all NN-research-prompt.md from manifest + metadata
//   finish  — verify 04_study_guide.md, link application, print path
//
// Usage:
//   node pipeline-run.js init --app <id> --slug nvidia-senior-ai-llm [--url ...] [--company ...] [--role ...]
//   node pipeline-run.js write --dir data/research/<slug> --file 01_job_scraper.md --text "..." 
//   node pipeline-run.js write --dir <slug> --file 01_job_description.md --file-content @jd.md
//   node pipeline-run.js batch --dir <slug> --topics '["Topic A","Topic B"]' [--batch 03]
//   node pipeline-run.js finish --dir <slug> --app <id>
const path = require("path");
const { load, save, nowISO } = require("./lib");
const {
  resolveResearchDir,
  initResearch,
  writeFile,
  readArgContent,
  allocateBatchNumber,
  registerBatch,
  buildDeepResearchPrompt,
  finishResearch,
  FILES,
  researchBatchFiles,
  loadManifest,
} = require("./research-lib");

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith("--")) { args[key] = next; i++; }
      else args[key] = true;
    } else args._.push(a);
  }
  return args;
}

function die(msg) { console.error(msg); process.exit(1); }

function cmdInit(a) {
  if (!a.app) die("init requires --app <applicationId>");
  const info = initResearch({
    appId: a.app,
    slug: a.slug,
    jobUrl: a.url,
    company: a.company,
    role: a.role,
    force: a.force,
  });
  const out = {
    research_dir: info.dir_rel,
    research_dir_abs: info.dir,
    slug: info.slug,
    study_guide_path: info.study_guide_rel,
    application_id: a.app,
    files: FILES,
  };
  console.log(JSON.stringify(out, null, 2));
  console.error(`Research dir: ${info.dir_rel}`);
}

function cmdWrite(a) {
  if (!a.dir || !a.file) die("write requires --dir and --file");
  const dir = resolveResearchDir(a.dir);
  const content = readArgContent(a["file-content"] || a.text || a.content);
  if (!content && content !== "") die("write requires --text or --file-content @path");
  writeFile(dir, a.file, content);
  console.log(JSON.stringify({ file: a.file, dir: a.dir }, null, 2));
}

function cmdBatch(a) {
  if (!a.dir) die("batch requires --dir");
  const dir = resolveResearchDir(a.dir);
  const batchNum = a.batch ? parseInt(a.batch, 10) : allocateBatchNumber(dir);
  let topics;
  try {
    topics = JSON.parse(a.topics || "[]");
  } catch (_) {
    die("--topics must be JSON array of main topic strings");
  }
  const m = loadManifest(dir);
  let meta = {};
  try {
    meta = JSON.parse(require("fs").readFileSync(path.join(dir, FILES.jobMetadata), "utf8"));
  } catch (_) { /* optional */ }
  const hierarchy = meta.topic_hierarchy || {};
  const subtopicsByTopic = {};
  for (const t of topics) subtopicsByTopic[t] = hierarchy[t] || [];

  const prompt = buildDeepResearchPrompt({
    company: m.company || meta.company_name || "Company",
    role: m.role || meta.job_title || "Role",
    jobUrl: m.job_url || meta.job_url,
    location: meta.location,
    topics,
    subtopicsByTopic,
    topicLearningOrder: meta.topic_learning_order,
  });

  const { files } = registerBatch(dir, batchNum, topics);
  writeFile(dir, files.prompt, prompt);
  console.log(JSON.stringify({
    batch: batchNum,
    prompt_file: files.prompt,
    report_file: files.report,
    next: `node scripts/deep-research.js --dir ${a.dir} --batch ${String(batchNum).padStart(2, "0")}`,
  }, null, 2));
}

function cmdRefreshPrompts(a) {
  if (!a.dir) die("refresh-prompts requires --dir");
  const dir = resolveResearchDir(a.dir);
  const m = loadManifest(dir);
  const meta = JSON.parse(require("fs").readFileSync(path.join(dir, FILES.jobMetadata), "utf8"));
  const hierarchy = meta.topic_hierarchy || {};
  for (const b of [...(m.research_batches || [])].sort((x, y) => x.number - y.number)) {
    const topics = b.topics || [];
    const subtopicsByTopic = {};
    for (const t of topics) subtopicsByTopic[t] = hierarchy[t] || [];
    const prompt = buildDeepResearchPrompt({
      company: m.company || meta.company_name || "Company",
      role: m.role || meta.job_title || "Role",
      jobUrl: m.job_url || meta.job_url,
      location: meta.location,
      topics,
      subtopicsByTopic,
      topicLearningOrder: meta.topic_learning_order,
    });
    writeFile(dir, b.prompt, prompt);
    console.error(`Refreshed ${b.prompt}`);
  }
  console.log(JSON.stringify({ refreshed: (m.research_batches || []).length }, null, 2));
}

function cmdFinish(a) {
  if (!a.dir) die("finish requires --dir");
  const dir = resolveResearchDir(a.dir);
  const { study_guide_rel, appId } = finishResearch(dir, { appId: a.app });

  if (appId) {
    const apps = load("applications");
    const app = apps.find((x) => x.id === appId);
    if (app) {
      app.research_dir = path.posix.dirname(study_guide_rel.replace(/\\/g, "/"));
      app.last_research_at = nowISO();
      app.research_status = "complete";
      app.updated_date = nowISO();
      save("applications", apps);
      console.error(`Updated application ${appId}: research_dir=${app.research_dir}`);
    }
  }

  console.log(study_guide_rel);
  console.error(`Study guide: ${study_guide_rel}`);
}

const args = parseArgs(process.argv.slice(2));
const cmd = args._[0];
if (!cmd || cmd === "help") {
  die("Usage: pipeline-run.js <init|write|batch|refresh-prompts|finish> [options]");
}

if (cmd === "init") cmdInit(args);
else if (cmd === "write") cmdWrite(args);
else if (cmd === "batch") cmdBatch(args);
else if (cmd === "refresh-prompts") cmdRefreshPrompts(args);
else if (cmd === "finish") cmdFinish(args);
else die(`Unknown command: ${cmd}`);
