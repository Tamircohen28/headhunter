# Gmail Status Detection Fixtures

The Gmail scanner classifies these fixtures. The `detect-gmail-status.js`
script parses the fenced `json` blocks below (an array of fixtures) and emits
the detected status + matched application for each.

Expected results:

| # | Company | Subject keyword | Expected status |
|---|---------|-----------------|-----------------|
| 1 | Acme Corp | technical interview | Technical |
| 2 | Globex | pleased to offer | Offer |
| 3 | Initech | unfortunately | Rejected |
| 4 | Umbrella | phone screen | Phone Screen |
| 5 | Hooli | final round / onsite | Onsite |

```json
[
  {
    "id": "msg1", "from": "recruiting@acme.com",
    "subject": "Next steps: Technical interview for Senior Backend Engineer",
    "body": "Hi, the team at Acme Corp would love to invite you to a technical interview / coding challenge next week."
  },
  {
    "id": "msg2", "from": "talent@globex.io",
    "subject": "We are pleased to offer you the Staff Engineer role!",
    "body": "Attached is your offer letter. We are pleased to offer you a position at Globex."
  },
  {
    "id": "msg3", "from": "noreply@initech.com",
    "subject": "Update on your Platform Engineer application",
    "body": "Unfortunately, we have decided not to move forward with your application at this time."
  },
  {
    "id": "msg4", "from": "hr@umbrella.co",
    "subject": "Schedule your phone screen with Umbrella",
    "body": "Let's set up an intro call / phone screen with our recruiter."
  },
  {
    "id": "msg5", "from": "people@hooli.xyz",
    "subject": "Invitation: Final round onsite interview",
    "body": "Congrats on reaching the final round! Please join us for an onsite panel interview."
  }
]
```
