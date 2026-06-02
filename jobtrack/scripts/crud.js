#!/usr/bin/env node
// Generic CRUD for jobtrack local JSON store, enforcing pipeline rules.
// Usage:
//   node crud.js list <entity> [--json]
//   node crud.js add <entity> '<json>'
//   node crud.js update <entity> <id> '<json-patch>'
//   node crud.js move <appId> "<Stage>"        # status change with rule check
//   node crud.js complete-task <taskId>
//   node crud.js seed                            # load references/sample-data.json into data/
//
// entity: applications | interviews | tasks | contacts | notes
const path = require("path");
const fs = require("fs");
const { load, save, nowISO, genId } = require("./lib");

const PIPELINE = ["Saved", "Applied", "Phone Screen", "Technical", "Onsite", "Offer", "Accepted"];
const TERMINAL = ["Declined", "Rejected", "Ghosted"];
const ID_PREFIX = { applications: "app", interviews: "int", tasks: "task", contacts: "con", notes: "note" };

const [, , cmd, ...rest] = process.argv;

function out(obj) { console.log(JSON.stringify(obj, null, 2)); }
function die(msg) { console.error(msg); process.exit(1); }

function add(entity, json) {
  const records = load(entity);
  const rec = JSON.parse(json);
  rec.id = rec.id || genId(ID_PREFIX[entity] || "rec");
  rec.created_date = rec.created_date || nowISO();
  rec.updated_date = nowISO();
  if (entity === "applications") {
    rec.status = rec.status || "Saved";
    rec.priority = rec.priority || "Medium";
    rec.currency = rec.currency || "USD";
  }
  if (entity === "interviews" && rec.round_number == null) {
    const same = records.filter((r) => r.application_id === rec.application_id);
    rec.round_number = same.length + 1;
  }
  if (entity === "tasks" && rec.completed == null) rec.completed = false;
  records.push(rec);
  save(entity, records);
  out(rec);
}

function update(entity, id, patchJson) {
  const records = load(entity);
  const rec = records.find((r) => r.id === id);
  if (!rec) die(`No ${entity} record with id ${id}`);
  Object.assign(rec, JSON.parse(patchJson), { updated_date: nowISO() });
  save(entity, records);
  out(rec);
}

function move(appId, stage) {
  if (![...PIPELINE, ...TERMINAL].includes(stage)) die(`Invalid status: ${stage}`);
  const apps = load("applications");
  const app = apps.find((a) => a.id === appId);
  if (!app) die(`No application with id ${appId}`);
  const curIdx = PIPELINE.indexOf(app.status);
  const newIdx = PIPELINE.indexOf(stage);
  const isTerminal = TERMINAL.includes(stage);
  if (!isTerminal && newIdx !== -1 && curIdx !== -1 && newIdx < curIdx) {
    die(`Refusing backward move: ${app.status} -> ${stage}. ` +
        `Pipeline is forward-only (terminal statuses ${TERMINAL.join(", ")} allowed from any stage). ` +
        `Pass an explicit confirmation by updating directly if this is a correction.`);
  }
  app.status = stage;
  app.updated_date = nowISO();
  save("applications", apps);
  out(app);
}

function completeTask(id) {
  const tasks = load("tasks");
  const t = tasks.find((x) => x.id === id);
  if (!t) die(`No task with id ${id}`);
  t.completed = true;
  t.updated_date = nowISO();
  save("tasks", tasks);
  out(t);
}

function seed() {
  const root = process.env.CLAUDE_PLUGIN_ROOT || path.join(__dirname, "..");
  const sample = JSON.parse(fs.readFileSync(path.join(root, "references", "sample-data.json"), "utf8"));
  for (const entity of Object.keys(sample)) save(entity, sample[entity]);
  console.error("Seeded data/ from references/sample-data.json");
}

switch (cmd) {
  case "list": out(load(rest[0])); break;
  case "add": add(rest[0], rest[1]); break;
  case "update": update(rest[0], rest[1], rest[2]); break;
  case "move": move(rest[0], rest[1]); break;
  case "complete-task": completeTask(rest[0]); break;
  case "seed": seed(); break;
  default:
    die("Commands: list|add|update|move|complete-task|seed");
}
