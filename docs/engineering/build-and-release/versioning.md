# Versioning & Changelog Policy

HeadHunter follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) and
keeps its changelog in [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

The version of record is the `version` field in
[`.claude-plugin/plugin.json`](../../../.claude-plugin/plugin.json). Git tags are `v<version>`
(e.g. `v1.5.0`).

## When to bump

Given a version `MAJOR.MINOR.PATCH`:

| Bump | When |
|------|------|
| **MAJOR** | A breaking change to the data model, CLI flags, or a removed/renamed command, skill, or script that existing users depend on. |
| **MINOR** | A new command, skill, agent, script, or integration added in a backward-compatible way. |
| **PATCH** | A bug fix, docs change, or internal quality fix that does not change the public surface. |

When in doubt, prefer the larger bump — under-bumping hides breaking changes from users.

## Changelog discipline

- Every user-facing change lands with a `CHANGELOG.md` entry under the `## [Unreleased]`
  section, grouped under `Added` / `Changed` / `Fixed` / `Removed`.
- Keep entries written for users ("what changed and why it matters"), not commit summaries.
- The [pull request checklist](../../CONTRIBUTING.md#pull-request-checklist) enforces this —
  a PR that changes behavior without a changelog entry is incomplete.

## Cutting a release

Releases are cut through the manual **Release** GitHub Actions workflow
([`.github/workflows/release.yml`](../../../.github/workflows/release.yml)):

1. Move the accumulated `## [Unreleased]` entries into a new
   `## [X.Y.Z] — YYYY-MM-DD` section in `CHANGELOG.md`, and leave `[Unreleased]` empty.
   Commit this on `main` (via PR).
2. Go to **Actions → Release → Run workflow** and enter the semver version (e.g. `1.5.0`).
3. The workflow validates the version format, runs `scripts/test.sh`, bumps `version` in
   `plugin.json`, commits the bump, creates and pushes the `v<version>` git tag, and
   publishes a GitHub Release pointing at the changelog.

The workflow is the **only** thing that writes the version bump and tag — do not bump
`plugin.json` or push tags by hand, so the manifest, tag, and release stay in lockstep.
