# Style

## Commits

```
<type>(<scope>): <short description>

Types: feat | fix | refactor | docs | test | chore
```

Branch from `main` (`git checkout -b feat/my-change`), open a PR against `main`, and let CI go green before merge.

## Dependency policy

- **No npm dependencies in core scripts** — `scripts/*.js` must run with `node` alone (Node.js ≥ 18). Only optional deep-research helpers may use peer tools.
- No build/compile step for the core CRM.

## Data mutation rules

- Status moves are **forward-only** — use `crud.js update` (patch) to correct a mistake, not `move`.
- All entity changes go through `scripts/crud.js` so the event log and `updated_date` stay consistent.
