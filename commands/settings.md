---
name: headhunter:settings
description: View or update HeadHunter settings — default currency, study weeks, hours per week, stale threshold, and data directory. Triggers on settings, configure headhunter, change currency, set stale threshold, update config.
allowed-tools: Read, Write, Edit, Bash
---

# HeadHunter Settings

Settings live in `${CLAUDE_PLUGIN_ROOT}/settings.json`. Read and display them; apply changes the user requests.

## View current settings

Read and display `settings.json` as a formatted table:

| Setting | Current value | Description |
|---------|--------------|-------------|
| defaultStatus | Saved | Status assigned to new applications |
| defaultCurrency | USD | Currency for salary fields |
| staleThresholdDays | 7 | Days before an active application is flagged as stale |
| dataDir | ${CLAUDE_PLUGIN_ROOT}/data | Where JSON data files are stored |
| research.studyWeeks | 4 | Number of weeks in a generated study plan |
| research.hoursPerWeek | 10 | Hours per week in the study plan |
| research.maxTopicsPerAgent | 4 | Max topics per topic-researcher subagent |
| research.minTopics | 15 | Minimum topics for the research pipeline |
| research.maxTopics | 25 | Maximum topics for the research pipeline |

Also show env-var overrides that are currently active:
- `HEADHUNTER_DATA_DIR` — overrides `dataDir`
- `GOOGLE_CALENDAR_ID` — Calendar ID for sync
- `GOOGLE_TASKS_LIST_ID` — Tasks list ID for sync
- `NOTION_DATABASE_ID`, `NOTION_TASKS_DATABASE_ID` — Notion sync targets
- `TODOIST_API_TOKEN` — Todoist integration

## Change a setting

When the user asks to change a value (e.g. "set currency to GBP", "change study weeks to 6"):

1. Read the current `settings.json`.
2. Apply the patch to the correct nested key.
3. Write the updated file back.
4. Confirm the change: "Updated `defaultCurrency` → GBP".

### Valid values

- `defaultStatus`: one of Saved, Applied, Phone Screen, Technical, Onsite, Offer, Accepted
- `defaultCurrency`: any ISO 4217 code (USD, EUR, GBP, etc.)
- `staleThresholdDays`: positive integer (recommended 5–14)
- `research.studyWeeks`: positive integer (recommended 2–8)
- `research.hoursPerWeek`: positive integer (recommended 5–20)

## Reset to defaults

If the user asks to reset settings, replace `settings.json` with:

```json
{
  "headhunter": {
    "defaultStatus": "Saved",
    "defaultCurrency": "USD",
    "staleThresholdDays": 7,
    "dataDir": "${CLAUDE_PLUGIN_ROOT}/data",
    "research": {
      "studyWeeks": 4,
      "hoursPerWeek": 10,
      "maxTopicsPerAgent": 4,
      "minTopics": 15,
      "maxTopics": 25,
      "outputDir": "${CLAUDE_PLUGIN_ROOT}/data/research"
    }
  }
}
```
