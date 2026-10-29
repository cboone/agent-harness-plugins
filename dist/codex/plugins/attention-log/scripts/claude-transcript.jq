# Shared prompt and terminal-refusal classification for Claude transcripts.
def content: (.message | objects | .content) // "";
def is_user: .type == "user" or .type == "human";
def is_result: content | type == "array" and any(.[]?; type == "object" and .type == "tool_result");
def kind:
  content as $c
  | if .type == "assistant" then "assistant"
    elif is_user and .isMeta != true then
      (if is_result then "result"
       elif ($c | type) == "string" and ($c | test("^<local-")) then "other"
       else "prompt" end)
    else "other" end;
def turn:
  [label $out | inputs | (fromjson? // null) | objects
    | if kind == "prompt" then break $out else . end];
def blocks: content | if type == "array" then .[] | objects else empty end;

# Read the transcript tail oldest first; only prompts and ordinary replies reset it.
def shows_refusal:
  reduce (inputs | fromjson? | objects) as $record (false;
    if $record.type == "assistant" and $record.isApiErrorMessage != true then false
    elif ($record | kind) == "prompt" then false
    elif $record.type == "system" and $record.subtype == "model_refusal_no_fallback" then true
    elif $record.type == "assistant" and $record.message.stop_reason == "refusal" then true
    else . end);
