// Shared helpers for jobtrack scripts (no external deps).
const fs = require("fs");
const path = require("path");

const DATA_DIR =
  process.env.JOBTRACK_DATA_DIR ||
  path.join(process.env.CLAUDE_PLUGIN_ROOT || path.join(__dirname, ".."), "data");

function dataFile(name) {
  return path.join(DATA_DIR, `${name}.json`);
}

function load(name) {
  const f = dataFile(name);
  if (!fs.existsSync(f)) return [];
  try {
    return JSON.parse(fs.readFileSync(f, "utf8"));
  } catch (e) {
    throw new Error(`Corrupt JSON in ${f}: ${e.message}`);
  }
}

function save(name, records) {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(dataFile(name), JSON.stringify(records, null, 2) + "\n");
}

function nowISO() {
  return new Date().toISOString();
}

function genId(prefix) {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
}

// CSV writer (RFC-4180-ish): quote fields containing comma, quote, or newline.
function toCsv(rows, columns) {
  const esc = (v) => {
    if (v === null || v === undefined) v = "";
    v = String(v);
    return /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
  };
  const head = columns.join(",");
  const body = rows.map((r) => columns.map((c) => esc(r[c])).join(",")).join("\n");
  return head + "\n" + body + "\n";
}

// Minimal CSV parser supporting quoted fields.
function parseCsv(text) {
  const rows = [];
  let row = [], field = "", inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') inQuotes = false;
      else field += c;
    } else if (c === '"') inQuotes = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n") { row.push(field); rows.push(row); row = []; field = ""; }
    else if (c === "\r") { /* skip */ }
    else field += c;
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  return rows.filter((r) => r.length && r.some((c) => c !== ""));
}

module.exports = { DATA_DIR, load, save, nowISO, genId, toCsv, parseCsv, dataFile };
