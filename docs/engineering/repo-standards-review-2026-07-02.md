# Repo standards review — headhunter

_Profile: app-gold · Reviewed 2026-07-02_

## Executive summary

`headhunter` is in good shape: README has badges + banner, CI runs lint/test/secret-scan on `ubuntu-latest`, branch protection is enabled with 3 required checks, PR template + Dependabot present, and AGENTS.md + CLAUDE.md both exist. Gaps are incremental polish: docs-tree hygiene, a couple of missing README sections, an agent-validation command, and multi-agent wiring (CLAUDE.md ↔ AGENTS.md cross-reference). No employer (Wix) IP present.

## Severity summary

| Severity | Count |
|----------|-------|
| P1 | 4 |
| P2 | 7 |
| P3 | 0 |

## Standards gaps (S1–S7)

| ID | Sev | Finding | Phase |
|----|-----|---------|-------|
| S6-01 | P1 | `docs/ARCHITECTURE.md` and `docs/CONTRIBUTING.md` sit at docs root; standard expects only `docs/README.md` there, with content filed under `user/` or `engineering/` | 0 |
| S1-03 | P2 | README missing an explicit Prerequisites section | 1 |
| S1-04 | P2 | README missing an explicit Quick Start section | 1 |
| S2-03 | P2 | `docs/CHANGELOG.md` missing (root `CHANGELOG.md` exists — needs a pointer or move) | 2 |
| S4-01 | P2 | `CODEOWNERS` missing | 4 |
| S4-03 | P2 | Branch protection requires 0 approving reviews | 4 |

## Multi-agent appendix (S8 / L*)

| ID | Sev | Finding | Phase |
|----|-----|---------|-------|
| L2-02 | P1 | `CLAUDE.md` does not reference `AGENTS.md` | 1 |
| L6-03 | P1 | No `agent:check` / validate command in Makefile | 4 |
| L6-04 | P1 | CI exists but no documented agent-validation command | 4 |
| L5-01 | P2 | `docs/agent-guidelines/` missing | 2 |
| L7-01 | P2 | No `check-agent-drift` script | 4 |

Full multi-agent setup is delegated to `multi-agent-repo` (step 3 of this maintenance pass).

## Employer IP scan

**CLEAN of Wix IP.** The scanner flagged 5 lines in `.mcp.json`, `.cursor/mcp.json`, and `README.md`, but all are `${VAR}` placeholder env references (`NOTION_TOKEN`, `GITHUB_PERSONAL_ACCESS_TOKEN`, `LINKEDIN_PASSWORD`) — no literal secrets, no Wix registry hosts, credentials, or internal references. No action required.

## Intentional deviations

- **S4-03 (require ≥1 approving review):** `headhunter` is a solo personal repo. GitHub forbids approving your own PR, so requiring 1 review would make every PR unmergeable and break the `pr-dev` auto-merge flow. Recommend **leaving required reviews at 0** and relying on required status checks (Lint/Test/Secret scan) as the merge gate. Not fixing.

## Docs read-only notes

- `docs/README.md` is a solid index. After moving ARCHITECTURE/CONTRIBUTING it must be updated to point at the new locations.
- README prose is thorough; only the structured Prerequisites/Quick Start headers are missing.

## Next steps

Proceed to plan mode, then polish on `feat/repo-standards-setup`.
