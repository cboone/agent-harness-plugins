# Normalize only durable terminal failures and session identity.
def text: if type == "string" then gsub("\u0000"; "") else "" end;
if .type == "session_meta" then
  {action: "meta", id: (((.payload.id | text | select(length > 0)) // .payload.session_id) | text),
    subagent: (.payload.source | type == "object" and has("subagent"))}
elif .type == "event_msg" and .payload.type == "task_complete" then
  .payload
  | select(.error | type == "object")
  | select(.error.codex_error_info | (type == "string" or type == "object") and length > 0)
  | select(.turn_id | type == "string" and length > 0)
  | (.error.codex_error_info | . == "cyber_policy" or . == "bio_policy" or . == "misalignment_policy_violation") as $refusal
  | {action: "failure", turn_id: .turn_id,
      kind: (if $refusal then "refusal" else "error" end),
      message: (if $refusal then "Turn ended in a safeguard refusal."
        else ((.error.message | text) | if length > 0 then . else "Turn ended in an API error." end) end)}
else empty end
