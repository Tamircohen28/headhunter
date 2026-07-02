# HeadHunter — Documentation

## Quick navigation

| I want to… | Go to |
|------------|-------|
| Get started fast | [user/quick-start.md](user/quick-start.md) |
| Understand how HeadHunter works | [user/concepts.md](user/concepts.md) |
| Fix something that's broken | [user/troubleshooting.md](user/troubleshooting.md) |
| Understand the system design | [engineering/architecture/overview.md](engineering/architecture/overview.md) |
| Set up a dev environment | [engineering/build-and-release/development-workflow.md](engineering/build-and-release/development-workflow.md) |
| See what CI checks | [engineering/build-and-release/ci-workflow.md](engineering/build-and-release/ci-workflow.md) |
| Read design decisions | [engineering/decisions/README.md](engineering/decisions/README.md) |
| Contribute | [../CONTRIBUTING.md](../CONTRIBUTING.md) |
| See what changed | [CHANGELOG.md](CHANGELOG.md) |
| Read the full architecture | [engineering/ARCHITECTURE.md](engineering/ARCHITECTURE.md) |

## Doc tree

```
docs/
├── README.md                   ← you are here
├── CHANGELOG.md                ← pointer to the root changelog
│
├── user/
│   ├── README.md               ← user doc index
│   ├── concepts.md             ← key concepts: pipeline, skills, agents, data model
│   ├── quick-start.md          ← zero to first dashboard in ~5 minutes
│   └── troubleshooting.md      ← common errors + fixes
│
└── engineering/
    ├── README.md               ← engineering doc index
    ├── ARCHITECTURE.md         ← full system architecture, storage model, pipeline diagrams
    ├── architecture/
    │   └── overview.md         ← layers, data flow, design rationale
    ├── build-and-release/
    │   ├── development-workflow.md
    │   └── ci-workflow.md
    └── decisions/
        ├── README.md           ← ADR index
        └── 001-local-json-store.md
```

CONTRIBUTING lives at the repo root ([../CONTRIBUTING.md](../CONTRIBUTING.md)) so GitHub surfaces it in the PR and issue UI.
