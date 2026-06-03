// Canonical enums and pipeline ordering — single source of truth for validation.
const PIPELINE = ["Saved", "Applied", "Phone Screen", "Technical", "Onsite", "Offer", "Accepted"];
const TERMINAL = ["Declined", "Rejected", "Ghosted"];
const ACTIVE_STAGES = ["Applied", "Phone Screen", "Technical", "Onsite", "Offer"];

const RESEARCH_STATUS = ["not_started", "in_progress", "complete", "stale"];

const ENUMS = {
  status: [...PIPELINE, ...TERMINAL],
  priority: ["High", "Medium", "Low"],
  remote_type: ["Remote", "Hybrid", "On-site"],
  research_status: RESEARCH_STATUS,
  round_type: ["Recruiter Call", "Phone Screen", "Technical", "System Design",
    "Behavioral", "Take-Home", "Onsite", "Panel", "Final", "Reference Check"],
  interview_status: ["Scheduled", "Completed", "Cancelled", "No-show"],
  outcome: ["Pending", "Passed", "Failed", "Cancelled"],
  overall_feeling: ["Great", "Good", "Neutral", "Nervous", "Poor"],
  note_type: ["General", "Follow-Up", "Offer Details", "Rejection Reason", "Research"],
  currency: ["USD", "EUR", "GBP", "CAD", "AUD", "INR", "JPY", "CHF"],
};

// Which field on which entity maps to which enum (and the interview `status`
// field is validated separately because it shares a name with application status).
const FIELD_ENUMS = {
  applications: { status: "status", priority: "priority", remote_type: "remote_type", currency: "currency", research_status: "research_status" },
  interviews: { round_type: "round_type", status: "interview_status", outcome: "outcome", overall_feeling: "overall_feeling" },
  tasks: { priority: "priority" },
  notes: { note_type: "note_type" },
  contacts: {},
};

const STATUS_EMOJI = {
  Saved: "⚪", Applied: "🔵", "Phone Screen": "🟣", Technical: "🟦",
  Onsite: "🟠", Offer: "🟢", Accepted: "✅",
  Declined: "🚫", Rejected: "🔴", Ghosted: "👻",
};

function validate(entity, record) {
  const map = FIELD_ENUMS[entity] || {};
  const errors = [];
  for (const [field, enumKey] of Object.entries(map)) {
    const val = record[field];
    if (val !== undefined && val !== null && val !== "" && !ENUMS[enumKey].includes(val)) {
      errors.push(`${field}="${val}" invalid; allowed: ${ENUMS[enumKey].join(", ")}`);
    }
  }
  return errors;
}

module.exports = { PIPELINE, TERMINAL, ACTIVE_STAGES, RESEARCH_STATUS, ENUMS, FIELD_ENUMS, STATUS_EMOJI, validate };
