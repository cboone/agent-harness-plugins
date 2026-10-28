def actions:
  ["read-axis", "read-review", "triage-review", "sync", "repair",
   "classify-review", "process-review", "request-review", "wait-review",
   "confirm-review", "merge", "post-merge", "file-deferred", "notify",
   "report", "escalate"];

def action_member($list; $candidate):
  if ($candidate | type) != "string" then error("action candidate must be a string")
  elif ($list | type) != "array" then error("action list must be an array of strings")
  elif ($list | all(type == "string") | not) then error("action list must contain only strings")
  else $list | any(. == $candidate) end;

def checked_action:
  . as $candidate
  | if action_member(actions; $candidate) then $candidate else error("unknown action name") end;

def checked_actions:
  if type != "array" then error("action list must be an array of known strings")
  else map(checked_action) end;

def without_actions($list; $excluded):
  ($excluded | checked_actions) as $checked
  | $list | checked_actions | map(select(action_member($checked; .) | not));

def no_fix_actions:
  ["triage-review", "sync", "repair", "process-review", "request-review",
   "wait-review", "confirm-review", "merge", "post-merge", "file-deferred", "notify"];

def pause_actions:
  ["read-review", "triage-review", "classify-review", "process-review",
   "request-review", "wait-review", "confirm-review", "merge"];

def lifecycle_actions:
  {OPEN: actions, MERGED: ["post-merge"], CLOSED: []}
  | with_entries(.value |= checked_actions);

def lifecycle:
  if type != "string" then error("snapshot state must be OPEN, MERGED or CLOSED")
  elif . == "OPEN" or . == "MERGED" or . == "CLOSED" then .
  else error("snapshot state must be OPEN, MERGED or CLOSED") end;

def eligibility($life; $policy; $action):
  ($action | checked_action) as $action
  | if action_member($policy.lifecycleActions[$life]; $action) | not then "inapplicable"
    elif action_member($policy.allowedActions; $action) then "eligible"
    else "forbidden" end;

# This closed registry owns every pending-read kind, permission and fallback diagnostic.
def observation_kinds:
  {snapshot: {action: "read-axis", retryable: false, requires: [], diagnostic: "PR metadata read failed"},
   "review-metadata": {action: "read-axis", retryable: true, requires: [], diagnostic: "review metadata read failed"},
   triage: {action: "read-review", retryable: true, requires: ["triage-review", "classify-review"], diagnostic: "earlier-review batch read failed"},
   threads: {action: "read-review", retryable: true, requires: ["classify-review"], diagnostic: "feedback thread fetch failed"},
   "review-id": {action: "read-review", retryable: true, requires: ["classify-review"], diagnostic: "review identity read failed"},
   "review-body": {action: "read-review", retryable: true, requires: ["classify-review"], diagnostic: "classification body read failed"},
   audit: {action: "read-review", retryable: true, requires: ["classify-review"], diagnostic: "feedback audit failed"},
   mergeability: {action: "read-axis", retryable: true, requires: [], diagnostic: "mergeability unknown"}};

def observation_counts:
  observation_kinds as $kinds
  | if type != "object" or (keys - ($kinds | keys) | length) != 0
    then error("invalid observation counters") else . end
  | . as $counts
  | reduce ($kinds | keys[]) as $name ({}; .[$name] = (if $counts | has($name) then $counts[$name] else 0 end))
  | if all(.[]; type == "number" and . >= 0 and . <= 2 and floor == .)
    then . else error("observation counters must be integers from zero through two") end;

def checked_observations:
  observation_kinds as $kinds
  | if type != "array" then error("observations must be an array") else . end
  | map(if type != "object" or (.name | type) != "string"
          or (.pending | type) != "boolean" or (.diagnostic | type) != "string"
          or ((keys - ["name", "pending", "diagnostic"]) | length) != 0
        then error("observation accepts only name, boolean pending and string diagnostic")
        else . end)
  | map(. as $obs | $kinds[$obs.name] as $kind
        | if $kind == null then error("unknown pending observation") else . end
        | ($kind.action | checked_action) as $action
        | ($kind.requires | checked_actions) as $requires
        | .action = $action | .requires = $requires | .retryable = $kind.retryable
        | .diagnostic = ($obs.name + ": " + (if $obs.diagnostic == "" then $kind.diagnostic else $obs.diagnostic end)))
  | if (map(.name) | length) != (map(.name) | unique | length)
    then error("duplicate observation in one tick") else . end;

def checked_candidates:
  if type != "array" then error("candidates must be an array") else . end
  | map(if type != "object" or (.detail | type) != "string"
          or ((keys - ["action", "detail"]) | length) != 0
        then error("candidate accepts only a known action and string detail")
        else (.action | checked_action) as $action | .action = $action end);

def resolve_policy:
  if type != "object" then error("restrictions must be an object") else . end
  | if (.noFix | type) != "boolean" or (.copilotPaused | type) != "boolean"
    or ((keys - ["noFix", "copilotPaused", "blockedActions"]) | length) != 0
    then error("unknown or malformed restriction") else . end
  | (if has("blockedActions") then .blockedActions else [] end) as $extra
  | ($extra | checked_actions) as $extra
  | (no_fix_actions | checked_actions) as $no_fix
  | (pause_actions | checked_actions) as $pause
  | {noFix, copilotPaused, blockedActions: ($extra | unique)} as $raw
  | (if .copilotPaused then $pause else [] end) as $paused
  | ((if .noFix then $no_fix else [] end) + $paused + $extra | checked_actions | unique) as $initial
  | ($initial
    + (if action_member($initial; "read-axis") then without_actions(actions; ["report", "escalate"]) else [] end)
    | checked_actions | unique) as $axis
  | ($axis
    + (if action_member($axis; "read-review") then ["triage-review", "classify-review", "process-review"] else [] end)
    | checked_actions | unique) as $reads
  | ($reads
    + (if action_member($reads; "classify-review") then ["triage-review", "process-review"] else [] end)
    + (if action_member($reads; "request-review") or action_member($reads; "wait-review") then ["confirm-review"] else [] end)
    + (if action_member($reads; "sync") or action_member($reads; "notify") then ["post-merge"] else [] end)
    | checked_actions | unique) as $blocked
  | {version: 1, restrictions: $raw, blockedActions: $blocked, pausedActions: $paused,
     lifecycleActions: lifecycle_actions,
     allowedActions: without_actions(actions; $blocked)};

def checked_state:
  if type != "object" then error("watch state must be an object") else . end
  | if has("restrictions") then error("prepare restrictions before using watch state") else . end
  | .policy as $policy
  | if ($policy | type) != "object" then error("resolved policy must be an object") else . end
  | ([$policy.blockedActions, $policy.allowedActions, $policy.pausedActions] | map(checked_actions)) as $lists
  | if ($policy.lifecycleActions | type) != "object" then error("invalid lifecycle actions") else . end
  | ($policy.lifecycleActions | map_values(checked_actions)) as $life_lists
  | ($policy.restrictions | resolve_policy) as $expected
  | if $policy != $expected then error("invalid resolved watch policy") else . end;

def gate($action):
  ($action | checked_action) as $action
  | .policy as $policy
  | action_member($policy.allowedActions; $action) as $allowed
  | {action: $action, allowed: $allowed,
     status: (if $allowed then "permitted"
              elif action_member($policy.pausedActions; $action)
              then "paused" else "unavailable" end)};

if length != 1 then error("needs exactly one watch snapshot") else .[0] end
| if $mode == "prepare" then
    if type != "object" then error("watch state must be an object") else . end
    | (.restrictions | resolve_policy) as $policy
    | del(.restrictions, .lifecycle) | .policy = $policy
    | if has("candidates") then .candidates |= checked_candidates else . end
  else
    checked_state
    | if $mode == "lifecycle" then .lifecycle = (.snapshot.state | lifecycle)
      elif $mode == "gate" then gate($action)
      elif $mode == "triage" then
        . as $state
        | (if has("earlierReviewCount") then .earlierReviewCount else null end) as $count
        | if (.triageAfter != "never" and ((.triageAfter | type) != "number"
              or .triageAfter < 0 or (.triageAfter | floor) != .triageAfter))
            or ($count != null and (($count | type) != "number" or $count < 0 or ($count | floor) != $count))
          then error("invalid triage metadata") else . end
        | gate("triage-review") as $gate
        | {status: (if $gate.allowed | not then $gate.status
                    elif $state.triageAfter == "never" or $count != null then "not-needed"
                    else "needed" end), count: $count,
           needsRead: ($gate.allowed and $state.triageAfter != "never" and $count == null)}
      elif $mode == "dispatch" then
        (if has("observationFailures") then .observationFailures else {} end | observation_counts) as $counts
        | (if has("observations") then .observations else [] end | checked_observations) as $observations
        | [$observations[] | select(.pending and (.retryable | not)) | .diagnostic] as $fatal
        | if ($fatal | length) > 0 then
            {lifecycle: null, route: null, wouldDo: [], wait: false, terminal: true,
             status: "failure", observationFailures: $counts, diagnostics: $fatal}
          else
        (.lifecycle | lifecycle) as $life
        | if $life != .snapshot.state then error("refresh lifecycle before collecting candidates") else . end
        | if (.candidates | type) != "array" or (.runningPermittedCheck | type) != "boolean"
          then error("dispatch needs candidates and runningPermittedCheck") else . end
        | .candidates |= checked_candidates
        | . as $state
        | (reduce $observations[] as $obs
            ({counts: $counts, candidates: [], would: [], exhausted: []};
             ([ $obs.action ] + $obs.requires | map(eligibility($life; $state.policy; .))) as $eligibilities
             | (if $eligibilities | any(. == "inapplicable") then "inapplicable"
                elif $eligibilities | any(. == "forbidden") then "forbidden" else "eligible" end) as $eligible
             | if $eligible == "inapplicable" then .
               elif $eligible == "forbidden" then
                 if $obs.pending then .would += [{action: $obs.action, detail: $obs.diagnostic, observation: $obs.name}] else . end
               elif $obs.pending then
                 .counts[$obs.name] = ([2, (.counts[$obs.name] + 1)] | min)
                 | if .counts[$obs.name] >= 2 then
                     .exhausted += [($obs.diagnostic + " (two-tick observation bound)")]
                   else .candidates += [{action: $obs.action, detail: $obs.diagnostic, observation: $obs.name, retry: true}] end
               else .counts[$obs.name] = 0 end)) as $observed
        | (reduce ($state.candidates + $observed.candidates)[] as $candidate
            ({route: null, would: []};
             eligibility($life; $state.policy; $candidate.action) as $eligible
             | if $eligible == "forbidden" then .would += [$candidate]
               elif $eligible == "eligible" and .route == null then .route = $candidate
               else . end)) as $selected
        | (if ($observed.exhausted | length) > 0 then null else $selected.route end) as $route
        | ($life == "OPEN" and ($observed.exhausted | length) == 0 and
           $state.runningPermittedCheck and action_member($state.policy.allowedActions; "read-axis")) as $running
        | ($route == null and ($running | not)) as $terminal
        | {lifecycle: $life, route: $route, wouldDo: ($selected.would + $observed.would), wait: ($route == null and $running),
           terminal: $terminal, status: (if $terminal then "unavailable" else null end),
           observationFailures: $observed.counts, diagnostics: $observed.exhausted}
          end
      elif $mode == "observation-kinds" then observation_kinds
      else error("unknown policy operation") end
  end
