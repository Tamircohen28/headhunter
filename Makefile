.PHONY: install test lint agent-check seed clean

install:
	@echo "HeadHunter has no npm dependencies for the core CRM."
	@echo "Node.js >= 18 required. Run 'make seed' to load demo data."

test:
	bash scripts/test.sh

lint:
	@which shellcheck >/dev/null 2>&1 && shellcheck scripts/parse-csv-import.sh scripts/test.sh || echo "shellcheck not found — skipping shell lint"
	@node --check scripts/crud.js scripts/lib.js scripts/enums.js scripts/dashboard.js scripts/analytics.js

# agent:check — validate the agent surface (manifests, JS syntax, frontmatter)
# and confirm thin adapters still reference AGENTS.md (agent drift).
agent-check:
	bash scripts/agent-check.sh
	bash scripts/check-agent-drift.sh

seed:
	node scripts/crud.js seed

clean:
	rm -rf data/backups data/research data/*.json
	@echo "data/ cleared (gitignored — your real data is untouched outside this repo)"
