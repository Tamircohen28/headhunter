---
description: Export applications as CSV or JSON to the current directory.
allowed-tools: Read, Bash
---

# Export Data

Export the user's applications. Default format CSV; honor `$ARGUMENTS` for
`json` or a custom output path.

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/export-applications.js --format csv  --out ./jobtrack-export.csv
node ${CLAUDE_PLUGIN_ROOT}/scripts/export-applications.js --format json --out ./jobtrack-export.json
```

Report the output path and row count.
