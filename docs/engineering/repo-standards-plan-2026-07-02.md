# Repo standards remediation plan — headhunter

_From review 2026-07-02 · Profile: app-gold · Branch: `feat/repo-standards-setup`_

## Phase 0 — IP scan & docs hygiene (P1)
- IP scan already CLEAN (only `${VAR}` placeholders). No scrubbing needed.
- **S6-01:** Move `docs/ARCHITECTURE.md` → `docs/engineering/ARCHITECTURE.md` and `docs/CONTRIBUTING.md` → `docs/CONTRIBUTING` stays as project-level? Keep CONTRIBUTING discoverable: move to repo root `CONTRIBUTING.md` (GitHub convention) and update `docs/README.md` links. Move ARCHITECTURE under `engineering/`.

## Phase 1 — README + CLAUDE↔AGENTS (P1/P2)
- **L2-02:** Add an `## Agent guidelines` section to `CLAUDE.md` pointing to `AGENTS.md` as canonical agent instructions.
- **S1-03:** Add `## Prerequisites` section to README (Node.js >= 18, no npm deps for core CRM).
- **S1-04:** Add `## Quick Start` section to README (clone → `make seed` → `make test`).

## Phase 2 — CHANGELOG + agent-guidelines (P2)
- **S2-03:** Add `docs/CHANGELOG.md` as a pointer to root `CHANGELOG.md` (keep root as canonical per keep-a-changelog convention).
- **L5-01:** Create `docs/agent-guidelines/` with a README (delegated to `multi-agent-repo` in phase 5 if it owns this).

## Phase 4 — governance + agent validation (P1/P2)
- **L6-03 / L6-04:** Add `make agent-check` target that validates agent/skill/command manifests + runs `node --check`; document it and wire into CI.
- **L7-01:** Add `scripts/check-agent-drift.sh` (delegated to `multi-agent-repo`).
- **S4-01:** Add `CODEOWNERS` (`* @TamirCohen28`).
- **S4-03:** INTENTIONAL DEVIATION — leave required reviews at 0 (solo repo; self-approval impossible; keep status checks as gate).

## Phase 5 — multi-agent
- Run `multi-agent-repo` on the same branch (step 3 of the maintenance pass) — owns AGENTS.md canonicalization, agent-guidelines, drift script.

## Phase 6 — docs/changelog review
- Ensure `docs/README.md` index reflects moved files.

## Phase 7 — exit gate
- `assert-contract.sh` P1/P2/P3 counts acceptable (S4-03 deviation documented).
- Open PR; do not merge (pr-dev drives merge).
