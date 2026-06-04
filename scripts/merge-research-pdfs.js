#!/usr/bin/env node
// Merge per-batch research PDFs (from OpenAI Code Interpreter) into one FULL PDF.
// Usage:
//   node merge-research-pdfs.js --dir data/research/<slug>
//   node merge-research-pdfs.js --dir <slug> --out "Role – FULL.pdf"
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");
const { resolveResearchDir, loadManifest } = require("./research-lib");

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

function listBatchPdfs(dir) {
  return fs.readdirSync(dir)
    .filter((f) => /^\d{2}-research-report\.pdf$/i.test(f))
    .sort();
}

function mergeWithPdfLib(inputPaths, outPath) {
  const scriptPath = path.join(__dirname, "_merge-pdf-lib-runner.js");
  const runner = `const fs=require("fs");
const { PDFDocument } = require("pdf-lib");
(async()=>{
  const inputs=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));
  const out=process.argv[2];
  const merged=await PDFDocument.create();
  for (const p of inputs) {
    const bytes=fs.readFileSync(p);
    const doc=await PDFDocument.load(bytes,{ignoreEncryption:true});
    const pages=await merged.copyPages(doc,doc.getPageIndices());
    pages.forEach(pg=>merged.addPage(pg));
  }
  fs.writeFileSync(out,await merged.save());
})().catch(e=>{console.error(e);process.exit(1);});`;
  fs.writeFileSync(scriptPath, runner);
  const res = spawnSync(
    "npx",
    ["--yes", "-p", "pdf-lib", "node", scriptPath, JSON.stringify(inputPaths), outPath],
    { encoding: "utf8", timeout: 120000 }
  );
  if (res.status !== 0) {
    console.error(res.stderr || res.stdout);
    die("PDF merge failed (npx -p pdf-lib). Check network for first-time install.");
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.dir) die("Usage: merge-research-pdfs.js --dir data/research/<slug> [--out file.pdf]");

  const dir = resolveResearchDir(args.dir);
  const m = loadManifest(dir);
  const pdfs = listBatchPdfs(dir);
  if (!pdfs.length) {
    die(
      "No *-research-report.pdf files found. Run deep-research with --pdf per batch first:\n"
      + "  OPENAI_API_KEY=... node scripts/deep-research.js --dir <slug> --batch 03 --pdf"
    );
  }

  const inputPaths = pdfs.map((f) => path.join(dir, f));
  const defaultName = `${m.role || "Interview Prep"} – FULL.pdf`.replace(/[/\\?%*:|"<>]/g, "-");
  const outPath = path.resolve(dir, args.out || defaultName);

  console.error(`Merging ${pdfs.length} PDFs → ${path.basename(outPath)}`);
  mergeWithPdfLib(inputPaths, outPath);

  console.log(JSON.stringify({
    merged_from: pdfs,
    pages_from_batches: pdfs.length,
    output: outPath,
  }, null, 2));
  console.log(outPath);
}

main();
