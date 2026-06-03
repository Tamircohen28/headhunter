---
description: Analyze a job offer and get a specific counter-offer script with market data, levers to pull, and what to say. Pass an application ID, or describe the offer inline ("they offered ₪42k base").
allowed-tools: Read, Bash, WebSearch, Task
---

# Salary Negotiation

Run the `salary-negotiation` skill for the offer in `$ARGUMENTS`.

Follow the `salary-negotiation` skill end-to-end:
1. Load candidate profile (floor, target, current salary).
2. Resolve offer from application record or inline text.
3. Pre-research market data via WebSearch.
4. Spawn salary-negotiator agent → counter-offer script, levers, walk-away number.
5. Offer to update application record with offer details.
