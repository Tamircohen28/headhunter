# Engineering Documentation

Fast-lane table for contributors and maintainers.

| I need to… | Go to |
|------------|-------|
| Understand the system design | [architecture/overview.md](architecture/overview.md) |
| Understand the full storage model + pipelines | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Set up a dev environment | [build-and-release/development-workflow.md](build-and-release/development-workflow.md) |
| Understand what CI checks and why | [build-and-release/ci-workflow.md](build-and-release/ci-workflow.md) |
| Read design decisions | [decisions/README.md](decisions/README.md) |
| Contribute | [../../CONTRIBUTING.md](../../CONTRIBUTING.md) |

## Codebase orientation

```
scripts/        Deterministic I/O — CRUD, sync, scoring, export. No AI in the loop.
skills/         Agent workflow instructions (Claude Code plugin skill format).
agents/         Subagent prompts spawned by skills.
commands/       Slash-command entry points (/headhunter:<name>).
references/     Schemas and integration specs (data-model, pipeline-output, etc.).
hooks/          hooks.json — Claude Code event hooks (SessionStart, PostToolUse).
```

The test suite (`scripts/test.sh`) is the primary correctness signal. Run it after every change.
