# Candidate Profile Schema

Stored at `${HEADHUNTER_DATA_DIR}/candidate-profile.json` (outside the repo — never committed).

Used by: `/headhunter:brief` (personalization), `/headhunter:search` (job filtering),
and application auto-fill.

```json
{
  "personal": {
    "name": "",
    "email": "",
    "phone": "",
    "linkedin_url": "",
    "github_url": "",
    "portfolio_url": "",
    "location": "",
    "timezone": "Asia/Jerusalem"
  },

  "cv": {
    "file_path": "",
    "text": "",
    "last_updated": ""
  },

  "experience": {
    "years_total": null,
    "current_title": "",
    "current_company": "",
    "years_at_current": null,
    "summary": "",
    "key_skills": [],
    "specializations": [],
    "open_source_projects": [],
    "certifications": [],
    "education": ""
  },

  "preferences": {
    "target_roles": [],
    "target_companies": [],
    "exclude_companies": [],
    "industries": [],
    "locations": [],
    "remote_type": "",
    "company_stage": [],
    "company_size": "",
    "must_haves": [],
    "deal_breakers": [],
    "why_looking": "",
    "career_goal_3yr": ""
  },

  "salary": {
    "current_base_ils": null,
    "current_total_ils": null,
    "target_base_ils": null,
    "target_total_ils": null,
    "floor_ils": null,
    "notes": ""
  },

  "availability": {
    "available_from": "",
    "notice_period_days": null,
    "actively_looking": true
  },

  "application_defaults": {
    "cover_letter_template": "",
    "languages": [],
    "visa_status": "Citizen",
    "work_authorization": "IL"
  }
}
```

## Field notes

| Field | Purpose |
|-------|---------|
| `cv.text` | Full CV text, extracted from file or pasted. Used by brief + auto-fill. |
| `preferences.why_looking` | Why you're looking now. Used in elevator pitch and motivation answers. |
| `preferences.career_goal_3yr` | Long-term goal. Used to filter roles and craft "why this role?" answers. |
| `salary.floor_ils` | Hard minimum. `/headhunter:brief` flags roles whose band appears below this. |
| `application_defaults.cover_letter_template` | Template with `{{company}}`, `{{role}}`, `{{reason}}` placeholders for auto-fill. |
