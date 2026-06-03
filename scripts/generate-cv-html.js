#!/usr/bin/env node
// Convert a tailored CV markdown file to a clean, A4-optimized HTML file.
// Open the HTML in a browser and Cmd+P → Save as PDF.
// Usage: node generate-cv-html.js --input <file.md> --out <file.html>
const fs = require("fs");
const path = require("path");

const inputIdx = process.argv.indexOf("--input");
const outIdx = process.argv.indexOf("--out");
const inputFile = inputIdx !== -1 ? process.argv[inputIdx + 1] : null;
const outFile = outIdx !== -1 ? process.argv[outIdx + 1] : null;

if (!inputFile || !outFile) {
  console.error("Usage: generate-cv-html.js --input <file.md> --out <file.html>");
  process.exit(1);
}
if (!fs.existsSync(inputFile)) { console.error(`File not found: ${inputFile}`); process.exit(1); }

const md = fs.readFileSync(inputFile, "utf8");

// ── Minimal markdown → HTML converter (no deps) ──────────────────────────
function mdToHtml(text) {
  const lines = text.split("\n");
  const out = [];
  let inList = false;
  let inSubList = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Close sublists before processing
    if (inSubList && !/^\s{2,}[-*]/.test(line)) { out.push("</ul>"); inSubList = false; }
    // Close top-level list before headings/hr
    if (inList && (trimmed.startsWith("#") || trimmed === "---" || trimmed === "")) {
      out.push("</ul>"); inList = false;
    }

    if (trimmed === "") { out.push("<br>"); continue; }
    if (trimmed === "---") { out.push('<hr class="section-rule">'); continue; }

    if (trimmed.startsWith("# "))  { out.push(`<h1>${esc(trimmed.slice(2))}</h1>`); continue; }
    if (trimmed.startsWith("## ")) { out.push(`<h2>${esc(trimmed.slice(3))}</h2>`); continue; }
    if (trimmed.startsWith("### ")){ out.push(`<h3>${esc(trimmed.slice(4))}</h3>`); continue; }

    if (/^\s{2,}[-*]/.test(line)) {
      if (!inSubList) { out.push('<ul class="sub">'); inSubList = true; }
      out.push(`<li>${inlineFormat(trimmed.replace(/^[-*]\s*/, ""))}</li>`);
      continue;
    }

    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      if (!inList) { out.push("<ul>"); inList = true; }
      out.push(`<li>${inlineFormat(trimmed.slice(2))}</li>`);
      continue;
    }

    out.push(`<p>${inlineFormat(trimmed)}</p>`);
  }
  if (inSubList) out.push("</ul>");
  if (inList) out.push("</ul>");
  return out.join("\n");
}

function esc(s) { return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

function inlineFormat(s) {
  return esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>');
}

const body = mdToHtml(md);

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CV</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #111;
    background: #fff;
    max-width: 21cm;
    margin: 0 auto;
    padding: 2cm 2.2cm;
  }

  h1 {
    font-size: 20pt;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin-bottom: 2px;
    page-break-after: avoid;
  }

  h2 {
    font-size: 11.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 14px;
    margin-bottom: 4px;
    border-bottom: 1.5px solid #ccc;
    padding-bottom: 2px;
    page-break-after: avoid;
  }

  h3 {
    font-size: 10.5pt;
    font-weight: 700;
    margin-top: 8px;
    margin-bottom: 1px;
    page-break-after: avoid;
  }

  p {
    margin-bottom: 3px;
  }

  ul {
    margin: 3px 0 6px 18px;
    padding: 0;
  }

  ul.sub {
    margin-left: 30px;
    margin-top: 1px;
  }

  li {
    margin-bottom: 2px;
  }

  hr.section-rule {
    border: none;
    border-top: 1.5px solid #ddd;
    margin: 10px 0;
  }

  strong { font-weight: 700; }
  em { font-style: italic; }
  code {
    font-family: "SFMono-Regular", Consolas, monospace;
    font-size: 9.5pt;
    background: #f4f4f4;
    padding: 1px 3px;
    border-radius: 2px;
  }
  a { color: #1a56db; text-decoration: none; }

  br { display: block; margin: 3px 0; content: ""; }

  @page {
    size: A4;
    margin: 2cm 2.2cm;
  }

  @media print {
    body { padding: 0; max-width: none; }
    a { color: #111; text-decoration: underline; }
    h2 { page-break-after: avoid; }
    li { page-break-inside: avoid; }
  }
</style>
</head>
<body>
${body}
</body>
</html>`;

const outDir = path.dirname(outFile);
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(outFile, html);
console.error(`CV HTML written: ${outFile}`);
console.error("Open in browser → Cmd+P (Mac) / Ctrl+P (Windows) → Save as PDF");
console.log(outFile);
