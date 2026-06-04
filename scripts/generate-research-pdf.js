#!/usr/bin/env node
// Markdown FULL guide → print-styled HTML → PDF (Chrome headless).
// Usage:
//   node generate-research-pdf.js --input data/research/<slug>/05_full_guide.md
//   node generate-research-pdf.js --dir data/research/<slug>
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");
const { resolveResearchDir } = require("./research-lib");

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

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function inlineFormat(s) {
  return esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>');
}

function mdToHtml(text) {
  const lines = text.split("\n");
  const out = [];
  let inList = false;
  let inCode = false;
  let codeBuf = [];

  function closeList() {
    if (inList) { out.push("</ul>"); inList = false; }
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (trimmed.startsWith("```")) {
      if (inCode) {
        out.push(`<pre><code>${esc(codeBuf.join("\n"))}</code></pre>`);
        codeBuf = [];
        inCode = false;
      } else {
        closeList();
        inCode = true;
      }
      continue;
    }
    if (inCode) { codeBuf.push(line); continue; }

    if (trimmed === "") { closeList(); out.push("<br>"); continue; }
    if (trimmed === "---") { closeList(); out.push('<hr class="section-rule">'); continue; }

    if (trimmed.startsWith("# ")) {
      closeList();
      out.push(`<h1 class="doc-title">${inlineFormat(trimmed.slice(2))}</h1>`);
      continue;
    }
    if (trimmed.startsWith("## ")) {
      closeList();
      const t = trimmed.slice(3);
      const isToc = /^table of contents/i.test(t);
      const cls = isToc ? "toc-heading" : "chapter";
      out.push(`<h2 class="${cls}">${inlineFormat(t)}</h2>`);
      continue;
    }
    if (trimmed.startsWith("### ")) {
      closeList();
      out.push(`<h3>${inlineFormat(trimmed.slice(4))}</h3>`);
      continue;
    }
    if (trimmed.startsWith("#### ")) {
      closeList();
      out.push(`<h4>${inlineFormat(trimmed.slice(5))}</h4>`);
      continue;
    }

    if (/^\d+\.\s/.test(trimmed) && !trimmed.startsWith("- ")) {
      closeList();
      out.push(`<p class="toc-line">${inlineFormat(trimmed)}</p>`);
      continue;
    }
    if (/^\s{2,}\d+\.\d+/.test(line)) {
      closeList();
      out.push(`<p class="toc-sub">${inlineFormat(trimmed)}</p>`);
      continue;
    }

    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      if (!inList) { out.push("<ul>"); inList = true; }
      out.push(`<li>${inlineFormat(trimmed.slice(2))}</li>`);
      continue;
    }

    closeList();
    if (trimmed.startsWith("*") && trimmed.endsWith("*")) {
      out.push(`<p class="subtitle">${inlineFormat(trimmed.replace(/^\*|\*$/g, ""))}</p>`);
    } else {
      out.push(`<p>${inlineFormat(trimmed)}</p>`);
    }
  }
  closeList();
  if (inCode && codeBuf.length) {
    out.push(`<pre><code>${esc(codeBuf.join("\n"))}</code></pre>`);
  }
  return out.join("\n");
}

function chromePath() {
  const candidates = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
  ];
  for (const c of candidates) {
    if (c.includes("/") && fs.existsSync(c)) return c;
  }
  return candidates[0];
}

function printPdf(htmlPath, pdfPath) {
  const chrome = chromePath();
  const url = `file://${htmlPath}`;
  const res = spawnSync(chrome, [
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    `--print-to-pdf=${pdfPath}`,
    url,
  ], { encoding: "utf8", timeout: 120000 });
  if (res.status !== 0) {
    console.error(res.stderr || res.stdout);
    die("Chrome PDF export failed. Open the HTML in a browser and print to PDF.");
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  let inputFile = args.input;
  if (args.dir) {
    const dir = resolveResearchDir(args.dir);
    inputFile = path.join(dir, args.guide || "05_full_guide.md");
  }
  if (!inputFile) die("Usage: generate-research-pdf.js --input <file.md> | --dir <research-slug>");

  if (!fs.existsSync(inputFile)) die(`File not found: ${inputFile}`);

  const md = fs.readFileSync(inputFile, "utf8");
  const base = inputFile.replace(/\.md$/i, "");
  const htmlPath = args.html || `${base}.html`;
  const pdfPath = args.out || `${base}.pdf`;

  const body = mdToHtml(md);
  const titleMatch = md.match(/^#\s+(.+)/m);
  const docTitle = titleMatch ? titleMatch[1].trim() : "Interview Preparation Guide";

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>${esc(docTitle)}</title>
<style>
  @page { size: A4; margin: 18mm 16mm; }
  *, *::before, *::after { box-sizing: border-box; }
  body {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #111;
    max-width: 21cm;
    margin: 0 auto;
    padding: 0.5cm 0;
  }
  h1.doc-title {
    font-size: 18pt;
    font-weight: 700;
    text-align: center;
    margin: 0 0 0.4em;
    page-break-after: avoid;
  }
  p.subtitle { text-align: center; font-size: 11pt; color: #333; margin-bottom: 1.2em; }
  h2.toc-heading { font-size: 14pt; margin-top: 1em; page-break-after: avoid; }
  h2.chapter {
    font-size: 13pt;
    margin-top: 1.4em;
    padding-top: 0.3em;
    border-top: 1px solid #ccc;
    page-break-before: always;
  }
  h2.chapter:first-of-type { page-break-before: auto; }
  h3 { font-size: 11.5pt; margin-top: 1em; page-break-after: avoid; }
  h4 { font-size: 10.5pt; margin-top: 0.8em; font-weight: 600; page-break-after: avoid; }
  p.toc-line { margin: 0.15em 0 0.15em 0.5em; font-size: 10pt; }
  p.toc-sub { margin: 0.08em 0 0.08em 1.5em; font-size: 9.5pt; color: #333; }
  ul { margin: 0.4em 0 0.6em 1.2em; }
  li { margin-bottom: 0.25em; }
  pre {
    font-size: 8.5pt;
    background: #f6f6f6;
    border: 1px solid #e0e0e0;
    padding: 0.6em;
    overflow-x: auto;
    page-break-inside: avoid;
  }
  code { font-family: Menlo, Consolas, monospace; font-size: 9pt; }
  hr.section-rule { border: none; border-top: 1px solid #ddd; margin: 1.2em 0; }
  a { color: #0a5; word-break: break-all; }
  table { border-collapse: collapse; width: 100%; margin: 0.6em 0; font-size: 9.5pt; }
  th, td { border: 1px solid #ccc; padding: 4px 6px; text-align: left; }
</style>
</head>
<body>
${body}
</body>
</html>`;

  fs.writeFileSync(htmlPath, html);
  printPdf(path.resolve(htmlPath), path.resolve(pdfPath));

  console.log(JSON.stringify({ html: htmlPath, pdf: pdfPath }, null, 2));
  console.log(pdfPath);
}

main();
