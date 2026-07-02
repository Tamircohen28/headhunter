# Contributing to HeadHunter

Thanks for your interest in contributing. HeadHunter is a personal-use tool but welcomes improvements that benefit all job seekers using it.

---

## Before you start

- Check [open issues](https://github.com/TamirCohen28/headhunter/issues) to see if your idea or bug is already tracked.
- For non-trivial features, open an issue first to discuss the approach before writing code.

---

## Development setup

```bash
git clone https://github.com/TamirCohen28/headhunter.git
cd headhunter
node --version   # must be >= 18
node scripts/crud.js seed   # load demo data
bash scripts/test.sh        # all 21 checks should pass
```

No `npm install` needed. The core CRM runs with Node.js built-ins only.

---

## What's in scope

- Bug fixes in `scripts/*.js`
- New or improved agent prompts in `agents/` and `skills/`
- New slash commands in `commands/` with matching skill in `skills/`
- Integration scripts in `scripts/sync-*.js`
- Documentation improvements in `docs/` and `references/`

**Out of scope:** Replacing the local-JSON storage model, adding a UI server, or adding npm runtime dependencies to the core CRM scripts.

---

## Making a change

1. Fork the repo and create a feature branch: `feat/my-improvement`
2. Make your changes.
3. Run the test suite: `bash scripts/test.sh` — all 21 checks must pass.
4. Update `CHANGELOG.md` under `[Unreleased]` with a brief entry.
5. Update `references/data-model.md` if you changed any entity schema.
6. Update `AGENTS.md` if you added or changed a CLI command or script.
7. Open a pull request against `main`.

---

## Code style

- **Scripts:** plain Node.js (no TypeScript, no bundler). `require()` only — no ES module syntax in scripts.
- **No external dependencies** in `scripts/` — only Node.js built-ins (`fs`, `path`, `readline`, `https`, `child_process`).
- **Error handling:** exit with code 1 and a clear message on failure; don't swallow errors silently.
- **Dry-run support:** any script that sends data to an external service must accept a `--dry-run` flag.
- **`--confirm` on destructive ops:** `delete` and `restore` must require `--confirm`.

---

## Commit messages

```
<type>(<scope>): <short description>

Types: feat | fix | refactor | docs | test | chore
```

Examples:
- `feat(scanner): add tier-based success-score calibration`
- `fix(crud): reject backward status moves via update`
- `docs(quick-start): add first-run GIF`

---

## Pull request checklist

- [ ] `bash scripts/test.sh` passes (all 21 green)
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] Schema docs updated if entity fields changed
- [ ] `--dry-run` supported if PR touches external sends
