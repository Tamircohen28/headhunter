#!/usr/bin/env node
// Generic CRUD for headhunter local JSON store, with enum validation, pipeline
// rule enforcement, and an event log (powers the Timeline view).
// Usage:
//   node crud.js list <entity> [--json]
//   node crud.js get <entity> <id>
//   node crud.js add <entity> '<json>'
//   node crud.js update <entity> <id> '<json-patch>'
//   node crud.js delete <entity> <id> --confirm
//   node crud.js move <appId> "<Stage>"        # status change with rule check
//   node crud.js complete-task <taskId>
//   node crud.js events [appId]                 # raw event log
//   node crud.js seed                            # load references/sample-data.json
//
// entity: applications | interviews | tasks | contacts | notes
const path = require("path");
const fs = require("fs");
const { load, save, nowISO, genId } = require("./lib");
const { PIPELINE, TERMINAL, validate } = require("./enums");

const ID_PREFIX = { applications: "app", interviews: "int", tasks: "task", contacts: "con", notes: "note", events: "evt" };
const VALID_ENTITIES = Object.keys(ID_PREFIX).filter((e) => e !== "events");

const [, , cmd, ...rest] = process.argv;

function out(obj) { console.log(JSON.stringify(obj, null, 2)); }
function die(msg) { console.error(msg); process.exit(1); }
function checkEntity(e) { if (!VALID_ENTITIES.includes(e)) die(`Unknown entity: ${e} (use ${VALID_ENTITIES.join(", ")})`); }

function logEvent(application_id, type, summary, meta = {}) {
  if (!application_id) return;
  const events = load("events");
  events.push({ id: genId("evt"), ts: nowISO(), type, application_id, summary, meta });
  save("events", events);
}

function companyOf(appId) {
  const a = load("applications").find((x) => x.id === appId);
  return a ? `${a.company} — ${a.role}` : appId;
}

function add(entity, json) {
  checkEntity(entity);
  const records = load(entity);
  const rec = JSON.parse(json);
  const errs = validate(entity, rec);
  if (errs.length) die("Validation failed:\n  - " + errs.join("\n  - "));
  rec.id = rec.id || genId(ID_PREFIX[entity]);
  rec.created_date = rec.created_date || nowISO();
  rec.updated_date = nowISO();
  if (entity === "applications") {
    rec.status = rec.status || "Saved";
    rec.priority = rec.priority || "Medium";
    rec.currency = rec.currency || "USD";
  }
  if (entity === "interviews" && rec.round_number == null) {
    rec.round_number = records.filter((r) => r.application_id === rec.application_id).length + 1;
  }
  if (entity === "tasks" && rec.completed == null) rec.completed = false;
  records.push(rec);
  save(entity, records);

  if (entity === "applications") logEvent(rec.id, "application_created", `Added ${rec.company} — ${rec.role} (${rec.status})`);
  if (entity === "interviews") logEvent(rec.application_id, "interview_added", `Logged ${rec.round_type} round (#${rec.round_number})`, { interview_id: rec.id });
  if (entity === "tasks" && rec.application_id) logEvent(rec.application_id, "task_added", `Task: ${rec.title}`, { task_id: rec.id });
  if (entity === "notes") logEvent(rec.application_id, "note_added", `Note (${rec.note_type || "General"})`, { note_id: rec.id });
  out(rec);
}

function update(entity, id, patchJson) {
  checkEntity(entity);
  const records = load(entity);
  const rec = records.find((r) => r.id === id);
  if (!rec) die(`No ${entity} record with id ${id}`);
  const patch = JSON.parse(patchJson);
  const errs = validate(entity, patch);
  if (errs.length) die("Validation failed:\n  - " + errs.join("\n  - "));
  Object.assign(rec, patch, { updated_date: nowISO() });
  save(entity, records);
  out(rec);
}

function del(entity, id) {
  checkEntity(entity);
  if (!process.argv.includes("--confirm")) die("Refusing to delete without --confirm (data is never deleted silently).");
  const records = load(entity);
  const next = records.filter((r) => r.id !== id);
  if (next.length === records.length) die(`No ${entity} record with id ${id}`);
  save(entity, next);
  console.error(`Deleted ${entity} ${id}.`);
}

function move(appId, stage) {
  if (![...PIPELINE, ...TERMINAL].includes(stage)) die(`Invalid status: ${stage}`);
  const apps = load("applications");
  const app = apps.find((a) => a.id === appId);
  if (!app) die(`No application with id ${appId}`);
  const from = app.status;
  const curIdx = PIPELINE.indexOf(from);
  const newIdx = PIPELINE.indexOf(stage);
  const isTerminal = TERMINAL.includes(stage);
  if (!isTerminal && newIdx !== -1 && curIdx !== -1 && newIdx < curIdx) {
    die(`Refusing backward move: ${from} -> ${stage}. Pipeline is forward-only ` +
        `(terminal statuses ${TERMINAL.join(", ")} allowed from any stage). ` +
        `Use \`update applications ${appId} '{"status":"${stage}"}'\` to override a correction.`);
  }
  if (from === stage) die(`Already in ${stage}.`);
  app.status = stage;
  app.updated_date = nowISO();
  save("applications", apps);
  logEvent(appId, "status_change", `${from} → ${stage}`, { from, to: stage });
  out(app);
}

function completeTask(id) {
  const tasks = load("tasks");
  const t = tasks.find((x) => x.id === id);
  if (!t) die(`No task with id ${id}`);
  t.completed = true;
  t.updated_date = nowISO();
  save("tasks", tasks);
  if (t.application_id) logEvent(t.application_id, "task_completed", `Completed: ${t.title}`, { task_id: id });
  out(t);
}

function seed() {
  const root = process.env.CLAUDE_PLUGIN_ROOT || path.join(__dirname, "..");
  const sample = JSON.parse(fs.readFileSync(path.join(root, "references", "sample-data.json"), "utf8"));
  for (const entity of Object.keys(sample)) save(entity, sample[entity]);
  save("events", []);
  console.error("Seeded data/ from references/sample-data.json");
}

switch (cmd) {
  case "list": checkEntity(rest[0]); out(load(rest[0])); break;
  case "get": { checkEntity(rest[0]); const r = load(rest[0]).find((x) => x.id === rest[1]); r ? out(r) : die("not found"); break; }
  case "add": add(rest[0], rest[1]); break;
  case "update": update(rest[0], rest[1], rest[2]); break;
  case "delete": del(rest[0], rest[1]); break;
  case "move": move(rest[0], rest[1]); break;
  case "complete-task": completeTask(rest[0]); break;
  case "events": { const e = load("events"); out(rest[0] ? e.filter((x) => x.application_id === rest[0]) : e); break; }
  case "seed": seed(); break;
  default:
    die("Commands: list|get|add|update|delete|move|complete-task|events|seed");
}
