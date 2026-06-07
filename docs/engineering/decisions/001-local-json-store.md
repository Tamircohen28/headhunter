# ADR 001 — Local flat-JSON store instead of a database

**Status:** Accepted  
**Date:** 2026-05-01

---

## Context

HeadHunter is a personal job-search tool that runs entirely on the user's machine. It needs to persist structured data (applications, interviews, tasks, contacts, notes, events) and support CRUD operations, pipeline stage transitions, and audit logging.

The two main options were:
1. A lightweight embedded database (SQLite, LevelDB, or a local MongoDB instance)
2. Plain JSON files on disk, with a thin Node.js script layer for all writes

---

## Decision

Store all CRM data as one JSON array file per entity type in a `data/` directory. All writes go through `scripts/crud.js`, which enforces validation, updates `updated_date`, and appends to `events.json`.

---

## Rationale

**Zero install friction.** JSON files require no database setup, no daemon, no migration runner. A new user clones the repo, runs `node scripts/crud.js seed`, and has data immediately. This directly supports the "no npm install" goal.

**No supply-chain risk on the data layer.** The core CRM scripts use only Node.js built-ins (`fs`, `path`, `readline`). There are no runtime dependencies that can be compromised via a supply-chain attack. Job-search data — CVs, salary figures, interview notes — is sensitive; keeping it in a dependency-free store reduces the attack surface.

**Readable and portable.** `data/*.json` files can be opened in any text editor, imported into Excel, backed up with `cp`, or migrated to any other tool. Users own their data in an open format.

**Git-native backup.** Although `data/` is gitignored (personal data should not ship), the format is git-friendly — JSON diffs are human-readable if a user chooses to version their own data directory.

**Sufficient performance for the use case.** HeadHunter is single-user; a realistic pipeline has at most a few hundred applications. Full-file reads and writes at this scale are fast enough that query optimization is not a concern.

---

## Alternatives considered

**SQLite** — better query performance and ACID guarantees. Rejected because it requires `better-sqlite3` or `sqlite3` npm packages, adding a build step (native binaries) and a supply-chain dependency. For a few hundred records, the trade-off is not worth it.

**LevelDB / LMDB** — fast key-value store. Rejected for the same dependency reason, and because the relational queries needed (e.g. join applications to interviews by `application_id`) are easy enough to implement with `Array.filter` at this data size.

**Local MongoDB (mongod)** — requires a running daemon, port, and mongosh. Rejected as too heavy for a personal CLI tool.

---

## Consequences

- **Concurrency is not safe.** Concurrent writes from two processes would corrupt files. This is acceptable: HeadHunter is single-user and single-session.
- **No ad-hoc SQL queries.** Complex analytics must be implemented as JavaScript in `scripts/analytics.js` and `scripts/dashboard.js`. This has been manageable so far.
- **Write discipline required.** Code must never hand-edit `data/*.json` directly — all writes must go through `crud.js`. This is enforced by the `validate-data.js` PostToolUse hook and documented as a hard constraint in `CLAUDE.md` and `AGENTS.md`.
