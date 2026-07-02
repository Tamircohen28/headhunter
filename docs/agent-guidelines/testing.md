# Testing

## Running tests

```bash
bash scripts/test.sh     # or: make test
```

The suite is a self-contained bash harness (`scripts/test.sh`). It must run **fully offline** — no test may reach the network. Run it after any change to `scripts/`.

## Validating the agent surface

```bash
make agent-check         # runs scripts/agent-check.sh + scripts/check-agent-drift.sh
```

`agent-check.sh` validates that every JSON manifest parses, every `scripts/*.js` passes `node --check`, the canonical agent docs exist, and every skill/agent/command file carries YAML frontmatter. `check-agent-drift.sh` verifies the thin adapters (`CLAUDE.md`, `.cursor/rules/*.mdc`) still point at `AGENTS.md`.

## Adding tests

- Add checks to `scripts/test.sh`; keep them offline and deterministic.
- Never add a stub that calls a real external API — mock at the script boundary or skip.
- CI (`.github/workflows/ci.yml`) runs Lint, Agent check, Test, and Secret scan on every PR; all four are required to merge.
