#!/usr/bin/env node
const path = require("path");
const fs = require("fs");
// OpenAI Deep Research via Responses API (native fetch).
// Default: markdown → <NN>-research-report.md
// With --pdf: also enables code_interpreter; downloads container PDF → <NN>-research-report.pdf
//
// Usage:
//   OPENAI_API_KEY=... node deep-research.js --dir data/research/<slug> --batch 03
//   node deep-research.js --dir <slug> --batch 03 --pdf
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
  buildPdfDeliverableInstructions,
} = require("./research-lib");

/** Load repo-root `.env` (gitignored) if present — does not override existing env. */
function loadDotEnv() {
  const envFile = path.join(__dirname, "..", ".env");
  if (!fs.existsSync(envFile)) return;
  for (const line of fs.readFileSync(envFile, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const eq = t.indexOf("=");
    if (eq < 0) continue;
    const k = t.slice(0, eq).trim();
    let v = t.slice(eq + 1).trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
      v = v.slice(1, -1);
    }
    if (k && process.env[k] === undefined) process.env[k] = v;
  }
}
loadDotEnv();

const API = "https://api.openai.com/v1/responses";
const DEFAULT_MODEL = process.env.OPENAI_DEEP_RESEARCH_MODEL || "o4-mini-deep-research";
const POLL_MS = 5000;
const MAX_WAIT_MS = 45 * 60 * 1000;

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
    if (a.prompt.startsWith("@")) return fs.readFileSync(a.prompt.slice(1), "utf8");
    return a.prompt;
  }
  if (batch) {
    const files = researchBatchFiles(batch);
    return readFile(dir, files.prompt);
  }
  die("Provide --prompt @file or --batch NN (reads NN-research-prompt.md)");
}

function walkOutput(output, fn) {
  for (const item of output || []) {
    fn(item);
    if (item.content) {
      for (const c of item.content) fn(c);
    }
  }
}

function extractOutputText(data) {
  if (data.output_text) return data.output_text;
  const parts = [];
  walkOutput(data.output, (item) => {
    if (item.type === "output_text" && item.text) parts.push(item.text);
  });
  return parts.join("\n\n");
}

function extractPdfCitations(data) {
  const found = [];
  walkOutput(data.output, (item) => {
    if (!item.annotations) return;
    for (const ann of item.annotations) {
      if (ann.type !== "container_file_citation") continue;
      const name = (ann.filename || "").toLowerCase();
      if (!name.endsWith(".pdf")) continue;
      if (!ann.container_id || !ann.file_id) continue;
      found.push({
        container_id: ann.container_id,
        file_id: ann.file_id,
        filename: ann.filename,
      });
    }
  });
  const seen = new Set();
  return found.filter((f) => {
    const k = `${f.container_id}:${f.file_id}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

async function downloadContainerFile({ container_id, file_id }, apiKey) {
  const url = `https://api.openai.com/v1/containers/${container_id}/files/${file_id}/content`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${apiKey}`, Accept: "application/binary" },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Container file download ${res.status}: ${err}`);
  }
  const buf = Buffer.from(await res.arrayBuffer());
  return buf;
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

async function runDeepResearch(prompt, { model, dryRun, wantPdf, batchLabel }) {
  const fullPrompt = wantPdf
    ? prompt + buildPdfDeliverableInstructions({ batchLabel })
    : prompt;

  if (dryRun) {
    console.error(`[dry-run] model=${model} pdf=${!!wantPdf} prompt_chars=${fullPrompt.length}`);
    return { text: "[dry-run] Deep research report would be written here.", pdfs: [] };
  }

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) die("OPENAI_API_KEY is required (or use --dry-run)");

  const tools = [{ type: "web_search_preview" }];
  if (wantPdf) {
    tools.push({ type: "code_interpreter", container: { type: "auto" } });
  }

  const body = {
    model,
    input: fullPrompt,
    background: true,
    reasoning: { summary: "auto" },
    tools,
    max_tool_calls: wantPdf ? 60 : 50,
  };

  console.error(`Starting deep research (${model})${wantPdf ? " + PDF via code_interpreter" : ""}…`);
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

  const pdfs = [];
  if (wantPdf) {
    const citations = extractPdfCitations(final);
    if (!citations.length) {
      console.error("Warning: no container_file_citation PDF in response. Markdown saved; re-run with --pdf or check prompt.");
    }
    for (const cite of citations) {
      console.error(`Downloading PDF: ${cite.filename} (${cite.file_id})`);
      const buf = await downloadContainerFile(cite, apiKey);
      pdfs.push({ filename: cite.filename, buffer: buf });
    }
  }

  return { text, pdfs };
}

(async () => {
  const a = parseArgs(process.argv.slice(2));
  if (!a.dir) {
    die("Usage: deep-research.js --dir data/research/<slug> --batch 03 [--pdf] [--model ...] [--dry-run]");
  }

  const dir = resolveResearchDir(a.dir);
  const batch = a.batch ? parseInt(String(a.batch).replace(/^0+/, "") || "0", 10) : null;
  const model = a.model || DEFAULT_MODEL;
  const wantPdf = !!a.pdf;
  let prompt = readPromptArg(a, dir, batch);

  if (a["write-prompt-only"]) {
    if (!batch) die("--write-prompt-only requires --batch");
    const files = researchBatchFiles(batch);
    if (wantPdf) prompt += buildPdfDeliverableInstructions({ batchLabel: `batch ${files.prompt}` });
    writeFile(dir, files.prompt, prompt);
    console.log(files.prompt);
    process.exit(0);
  }

  const batchLabel = batch ? `batch ${String(batch).padStart(2, "0")}` : null;
  const { text, pdfs } = await runDeepResearch(prompt, {
    model,
    dryRun: !!a["dry-run"],
    wantPdf,
    batchLabel,
  });

  if (batch) {
    const files = researchBatchFiles(batch);
    writeFile(dir, files.report, text);
    console.error(`Wrote ${files.report} (${text.length} chars)`);

    if (wantPdf && pdfs.length) {
      const pdfBuf = pdfs[0].buffer;
      fs.writeFileSync(path.join(dir, files.reportPdf), pdfBuf);
      console.error(`Wrote ${files.reportPdf} (${pdfBuf.length} bytes)`);
      console.log(files.reportPdf);
    } else if (wantPdf && a["dry-run"]) {
      fs.writeFileSync(path.join(dir, files.reportPdf), Buffer.from("%PDF-1.4\n%dry-run placeholder\n"));
      console.log(files.reportPdf);
    } else {
      console.log(files.report);
    }
  } else if (a.out) {
    const outPath = a.out.startsWith("@") ? a.out.slice(1) : path.join(dir, a.out);
    fs.writeFileSync(outPath, text.endsWith("\n") ? text : `${text}\n`);
    console.log(outPath);
  } else {
    process.stdout.write(text);
  }
})().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
