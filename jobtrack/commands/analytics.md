---
description: Show pipeline funnel analytics — conversion rates at each stage, offer rate, ghost rate, top performing sources, and scanner score averages.
allowed-tools: Read, Bash
---

# Pipeline Analytics

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/analytics.js
```

Display the funnel with bar charts, conversion rates, ghost rate, source performance, and scanner score averages.

If the user asks for raw JSON:
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/analytics.js --json
```

After displaying, offer:
- "Which source should I focus on?" → Recommend the source with the highest screen rate
- "What's dragging my conversion down?" → Identify the biggest drop-off stage
- "Show my active applications" → `/jobtrack:pipeline`
