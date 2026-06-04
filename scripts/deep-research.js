#!/usr/bin/env node
const path = require("path");
// OpenAI Deep Research via Responses API (no npm — uses native fetch).
// Writes report to <research-dir>/<NN>-research-report.md
//
// Usage:
//   OPENAI_API_KEY=... node deep-research.js --dir data/research/<slug> --batch 03
//   node deep-research.js --dir <slug> --prompt @path/to/prompt.md [--model o3-deep-research]
//   node deep-research.js --dir <slug> --batch 03 --dry-run
//
// Env:
//   OPENAI_API_KEY (required unless --dry-run)
//   OPENAI_DEEP_RESEARCH_MODEL (default: o4-mini-deep-research)
const {
  resolveResearchDir,
  researchBatchFiles,
  readFile,
  writeFile,
  loadManifest,
} = require("./research-lib");

const API = "https://api.openai.com/v1/responses";
const DEFAULT_MODEL = process.env.OPENAI_DEEP_RESEARCH_MODEL || "o4-mini-deep-research";
const POLL_MS = 5000;
const MAX_WAIT_MS = 30 * 60 * 1000;

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

function readPromptArg(a, dir, batch) {
  if (a.prompt) {
    const p = a.prompt.startsWith("@") ? a.prompt.slice(1) : a.prompt;
    if (a.prompt.startsWith("@")) return require("fs").readFileSync(p, "utf8");
    return a.prompt;
  }
  if (batch) {
    const files = researchBatchFiles(batch);
    return readFile(dir, files.prompt);
  }
  die("Provide --prompt @file or --batch NN (reads NN-research-prompt.md)");
}

function extractOutputText(data) {
  if (data.output_text) return data.output_text;
  const parts = [];
  for (const item of data.output || []) {
    if (item.type === "message" && item.content) {
      for (const c of item.content) {
        if (c.type === "output_text" && c.text) parts.push(c.text);
      }
    }
  }
  return parts.join("\n\n");
}

async function pollResponse(id, apiKey) {
  const start = Date.now();
  while (Date.now() - start < MAX_WAIT_MS) {
    const res = await fetch(`${API}/${id}`, {
      headers: { Authorization: `Bearer ${apiKey}` },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(`${res.status} ${JSON.stringify(data)}`);
    const status = data.status;
    if (status === "completed") return data;
    if (status === "failed" || status === "cancelled") {
      throw new Error(`Deep research ${status}: ${JSON.stringify(data.error || data)}`);
    }
    console.error(`  … status: ${status} (${Math.round((Date.now() - start) / 1000)}s)`);
    await new Promise((r) => setTimeout(r, POLL_MS));
  }
  throw new Error(`Timed out after ${MAX_WAIT_MS / 1000}s waiting for response ${id}`);
}

async function runDeepResearch(prompt, { model, dryRun }) {
  if (dryRun) {
    console.error(`[dry-run] model=${model} prompt_chars=${prompt.length}`);
    return "[dry-run] Deep research report would be written here.";
  }
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) die("OPENAI_API_KEY is required (or use --dry-run)");

  const body = {
    model,
    input: prompt,
    background: true,
    reasoning: { summary: "auto" },
    tools: [{ type: "web_search_preview" }],
    max_tool_calls: 50,
  };

  console.error(`Starting deep research (${model})…`);
  const createRes = await fetch(API, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  const created = await createRes.json();
  if (!createRes.ok) throw new Error(`${createRes.status} ${JSON.stringify(created)}`);

  const id = created.id;
  if (!id) throw new Error(`No response id: ${JSON.stringify(created)}`);
  console.error(`Response id: ${id}`);

  const final = await pollResponse(id, apiKey);
  const text = extractOutputText(final);
  if (!text) throw new Error("Empty output from deep research response");
  return text;
}

(async () => {
  const a = parseArgs(process.argv.slice(2));
  if (!a.dir) die("Usage: deep-research.js --dir data/research/<slug> --batch 03 [--model ...] [--dry-run]");

  const dir = resolveResearchDir(a.dir);
  const batch = a.batch ? parseInt(String(a.batch).replace(/^0+/, "") || "0", 10) : null;
  const batchPadded = batch ? String(batch).padStart(2, "0") : null;
  const model = a.model || DEFAULT_MODEL;
  const prompt = readPromptArg(a, dir, batch);

  if (a["write-prompt-only"]) {
    if (!batch) die("--write-prompt-only requires --batch");
    const files = researchBatchFiles(batch);
    writeFile(dir, files.prompt, prompt);
    console.log(files.prompt);
    process.exit(0);
  }

  const report = await runDeepResearch(prompt, { model, dryRun: !!a["dry-run"] });

  if (batch) {
    const files = researchBatchFiles(batch);
    writeFile(dir, files.report, report);
    console.log(files.report);
    console.error(`Wrote ${files.report} (${report.length} chars)`);
  } else if (a.out) {
    const outPath = a.out.startsWith("@") ? a.out.slice(1) : path.join(dir, a.out);
    require("fs").writeFileSync(outPath, report.endsWith("\n") ? report : report + "\n");
    console.log(outPath);
  } else {
    process.stdout.write(report);
  }
})().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
