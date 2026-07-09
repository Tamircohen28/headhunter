.PHONY: install update uninstall test lint clean seed \
	agent\:check agent-polish-gate repo-standards-gate assert-contract \
	check-agent-drift check-feature-equivalence check-platform-targets \
	platform-targets-sync platform-targets-assert

install:
	bash scripts/install.sh

update:
	bash scripts/update.sh

uninstall:
	bash scripts/uninstall.sh

test:
	bash scripts/test.sh

lint:
	@which shellcheck >/dev/null 2>&1 && shellcheck scripts/*.sh || echo "shellcheck not found — skipping shell lint"
	@node --check scripts/crud.js scripts/lib.js scripts/enums.js scripts/dashboard.js scripts/analytics.js

agent-check:
	bash scripts/agent-check.sh
	bash scripts/check-agent-drift.sh

check-agent-drift:
	bash scripts/check-agent-drift.sh .

check-feature-equivalence:
	bash scripts/check-feature-equivalence.sh .

check-platform-targets:
	bash scripts/check-platform-targets.sh .

platform-targets-sync:
	bash scripts/check-platform-targets.sh . --sync

platform-targets-assert:
	bash scripts/check-platform-targets.sh . --assert-current

agent\:check: check-agent-drift check-feature-equivalence check-platform-targets
	bash scripts/agent-check.sh

agent-polish-gate: platform-targets-sync platform-targets-assert agent\:check

assert-contract:
	bash scripts/contract/assert-contract.sh . app-gold --manifests-only

repo-standards-gate: agent-polish-gate assert-contract

seed:
	node scripts/crud.js seed

clean:
	rm -rf data/backups data/research data/*.json
	@echo "data/ cleared (gitignored — your real data is untouched outside this repo)"
