# Passes only a reply that matches result-schema.json. Run as
# `jq -e -f result-check.jq <reply>`; keep the two files in step.
def strings: type == "array" and all(.[]; type == "string");
def finding:
  type == "object"
  and (keys == ["detail", "evidence", "file", "line", "severity", "title"])
  and ([.detail, .evidence, .file, .title] | all(type == "string"))
  and (.line == null or (.line | type == "number" and . == floor and . >= 1))
  and (.severity | IN("important", "nit"));

type == "object"
and (keys == ["complete", "excluded", "findings", "not_reviewed", "report", "reviewed", "status", "unverified"])
and (.status | IN("success", "no-op", "failure", "unavailable"))
and (.complete | type == "boolean")
and (.reviewed | type == "string")
and (.report | type == "string")
and (.findings | type == "array" and all(.[]; finding))
and ([.excluded, .not_reviewed, .unverified] | all(strings))
