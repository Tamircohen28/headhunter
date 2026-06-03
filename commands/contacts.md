---
description: List and search contacts across all applications.
allowed-tools: Read, Bash
---

# Contacts

List all contacts with their linked application (section 5.7):

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/crud.js list contacts
```

Join each contact's `application_id` to the application name. If `$ARGUMENTS`
is a search term, filter by name, company, or role. Render: Name | Role | Company | Email | LinkedIn.
