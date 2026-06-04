#!/usr/bin/env node
// Merge research reports + study guide into one numbered FULL guide with TOC.
// Usage:
//   node merge-research-full.js --dir data/research/<slug>
//   node merge-research-full.js --dir <slug> --out 05_full_guide.md
const fs = require("fs");
const path = require("path");
const {
  resolveResearchDir,
  FILES,
  loadManifest,
  buildTopicIndex,
  RESEARCH_SUBSECTIONS,
  writeFile,
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

function normalizeTitle(s) {
  return String(s || "")
    .replace(/^#+\s*/, "")
    .replace(/^\d+(\.\d+)*\.?\s*/, "")
    .trim()
    .toLowerCase();
}

function listReportFiles(dir) {
  return fs.readdirSync(dir)
    .filter((f) => /^\d{2}-research-report\.md$/.test(f))
    .sort();
}

function buildToc(topicIndex) {
  const lines = ["## Table of Contents", ""];
  for (const t of topicIndex) {
    lines.push(`${t.num}. ${t.title}`);
    for (const st of t.subtopics) {
      lines.push(`   ${st.num} ${st.label}`);
    }
    lines.push("");
  }
  lines.push("---", "");
  return lines.join("\n");
}

function renumberReportBody(text, topicIndex) {
  const byTitle = new Map();
  for (const t of topicIndex) {
    byTitle.set(normalizeTitle(t.title), t);
  }

  const lines = text.split("\n");
  const out = [];
  let currentTopic = null;
  let subIdx = 0;

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];

    if (line.startsWith("# Batch ") || line.startsWith("**Topics covered:**") || line.startsWith("**Role context:**")) {
      continue;
    }
    if (line.trim() === "---" && !currentTopic) continue;

    const h2 = line.match(/^##\s+(.+)$/);
    if (h2) {
      const key = normalizeTitle(h2[1]);
      currentTopic = byTitle.get(key);
      subIdx = 0;
      if (currentTopic) {
        out.push(`## ${currentTopic.num}. ${currentTopic.title}`);
        out.push("");
      } else {
        out.push(line);
      }
      continue;
    }

    const h3 = line.match(/^###\s+(.+)$/);
    if (h3 && currentTopic) {
      const label = h3[1].trim();
      const key = normalizeTitle(label);
      const matchSub = currentTopic.subtopics.find((s) => normalizeTitle(s.label) === key);
      if (matchSub) {
        out.push(`### ${matchSub.num} ${matchSub.label}`);
      } else if (subIdx < currentTopic.subtopics.length) {
        const st = currentTopic.subtopics[subIdx];
        subIdx += 1;
        out.push(`### ${st.num} ${st.label}`);
      } else {
        out.push(line);
      }
      continue;
    }

    const h4 = line.match(/^####\s+(.+)$/);
    if (h4) {
      const label = h4[1].trim();
      const hit = RESEARCH_SUBSECTIONS.find((s) => s.patterns.some((p) => p.test(label)));
      if (hit) out.push(`#### ${hit.label}`);
      else out.push(line);
      continue;
    }

    out.push(line);
  }

  return out.join("\n");
}

function extractStudyGuideSections(guideMd) {
  const parts = { overview: "", plan: "", cheatsheet: "", questions: "" };
  const chunks = guideMd.split(/^##\s+/m).filter(Boolean);
  for (const chunk of chunks) {
    const title = chunk.split("\n")[0].trim().toLowerCase();
    const body = chunk.slice(chunk.indexOf("\n") + 1).trim();
    if (/^1\.|^overview/.test(title)) parts.overview = body;
    else if (/time-boxed|study plan|^3\./.test(title)) parts.plan = body;
    else if (/cheat.sheet|^4\./.test(title)) parts.cheatsheet = body;
    else if (/questions to ask|^5\./.test(title)) parts.questions = body;
  }
  return parts;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.dir) die("Usage: merge-research-full.js --dir data/research/<slug> [--out 05_full_guide.md]");

  const dir = resolveResearchDir(args.dir);
  const metaPath = path.join(dir, FILES.jobMetadata);
  if (!fs.existsSync(metaPath)) die(`Missing ${FILES.jobMetadata}`);

  const meta = JSON.parse(fs.readFileSync(metaPath, "utf8"));
  const topicIndex = buildTopicIndex(meta.topic_learning_order, meta.topic_hierarchy);
  const m = loadManifest(dir);

  const title = `${meta.job_title || m.role || "Role"} – FULL`;
  const subtitle = `Interview Preparation Guide · ${meta.company_name || m.company || "Company"}`;

  const reports = listReportFiles(dir);
  if (!reports.length) die("No *-research-report.md files found");

  let body = "";
  for (const f of reports) {
    const raw = fs.readFileSync(path.join(dir, f), "utf8");
    body += renumberReportBody(raw, topicIndex) + "\n\n";
  }

  const toc = buildToc(topicIndex);
  let front = "";
  const guidePath = path.join(dir, FILES.studyGuide);
  if (fs.existsSync(guidePath)) {
    const guide = fs.readFileSync(guidePath, "utf8");
    const sections = extractStudyGuideSections(guide);
    if (sections.overview) {
      front += `## Overview and Study Plan\n\n${sections.overview}\n\n---\n\n`;
    }
    if (sections.plan) {
      front += `## Time-Boxed Study Plan\n\n${sections.plan}\n\n---\n\n`;
    }
    if (sections.cheatsheet) {
      front += `## Interview Cheat-Sheet\n\n${sections.cheatsheet}\n\n---\n\n`;
    }
    if (sections.questions) {
      front += `## Questions to Ask Interviewers\n\n${sections.questions}\n\n---\n\n`;
    }
  }

  const full = [
    `# ${title}`,
    "",
    `*${subtitle}*`,
    "",
    meta.location ? `**Location:** ${meta.location}` : "",
    meta.job_url ? `**Posting:** ${meta.job_url}` : "",
    "",
    toc,
    front ? front : "",
    "# Research Topics",
    "",
    body.trim(),
    "",
  ].filter((x) => x !== undefined).join("\n");

  const outName = args.out || "05_full_guide.md";
  writeFile(dir, outName, full);

  const rel = path.join("data", "research", path.basename(dir), outName).split(path.sep).join("/");
  console.log(JSON.stringify({
    file: outName,
    path_rel: rel,
    topics: topicIndex.length,
    report_files: reports,
  }, null, 2));
  console.log(rel);
}

main();
