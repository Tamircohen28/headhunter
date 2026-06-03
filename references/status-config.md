# Status Configuration & Pipeline Rules

## PIPELINE_STAGES (ordered)

| Order | Status | Color | Emoji |
|-------|--------|-------|-------|
| 0 | Saved | slate | ⚪ |
| 1 | Applied | blue | 🔵 |
| 2 | Phone Screen | purple | 🟣 |
| 3 | Technical | indigo | 🟦 |
| 4 | Onsite | orange | 🟠 |
| 5 | Offer | green | 🟢 |
| 6 | Accepted | emerald | ✅ |

## Terminal statuses (not in forward pipeline)

| Status | Color | Emoji |
|--------|-------|-------|
| Declined | gray | 🚫 |
| Rejected | red | 🔴 |
| Ghosted | zinc | 👻 |

## Progression rules

```
Saved → Applied → Phone Screen → Technical → Onsite → Offer → Accepted
Terminal: Declined, Rejected, Ghosted
```

- **Advance only forward** through the ordered pipeline.
- **Rejected / Declined** may be applied from ANY stage (early exit).
- **Ghosted** may be applied from any active stage.
- Never move backward unless the user explicitly confirms a correction.

## ACTIVE_STAGES (for stale reminders & analytics)

`Applied, Phone Screen, Technical, Onsite, Offer`

## Stale threshold

An application is **stale** if its `status` is in ACTIVE_STAGES and
`updated_date` is older than **7 days**.

## Priority

`High, Medium, Low` (default `Medium`). Todoist map: High→4, Medium→3, Low→2.

## Currencies

`USD, EUR, GBP, CAD, AUD, INR, JPY, CHF` (default `USD`).
