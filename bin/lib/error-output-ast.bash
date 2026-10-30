#!/usr/bin/env bash
# Parse bounded shell units without executing their contents.
OUTPUT_AST_LIBRARY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly OUTPUT_AST_LIBRARY_DIR
readonly OUTPUT_AST_NATIVE_LIMIT=10

function output_ast_reason() {
  jq -r --arg kind "${1}" --arg name "${2}" \
    '.[$kind][] | select(.name == $name) | .reason' bin/lib/error-output-policy.json
}

function output_ast_pack() {
  local manifest="${1}"
  awk -F '\t' -v input="${OUTPUT_AST_TMP}/input.bash" -v meta="${OUTPUT_AST_TMP}/packed.tsv" '
    BEGIN { line = 1; id = 0 }
    {
      print "__error_output_begin " id > input
      print "(" > input
      print ":" > input
      body = line + 3
      count = 0
      while ((status = (getline text < $4)) > 0) { print text > input; count++ }
      if (status < 0) { print "Cannot read " $4 > "/dev/stderr"; exit 1 }
      close($4)
      print "" > input
      closing = body + count + 1
      print ")" > input
      print "__error_output_end " id > input
      print $1 "\t" $2 "\t" $3 "\t" body "\t" line + 1 "\t" closing "\t" $5 > meta
      line = closing + 2
      id++
    }
  ' "${manifest}"
  jq -Rn '[inputs | split("\t") |
    {name: .[0], file: .[1], origin: (.[2]|tonumber), body: (.[3]|tonumber),
     open: (.[4]|tonumber), close: (.[5]|tonumber), stream: .[6]}]' \
    "${OUTPUT_AST_TMP}/packed.tsv" > "${OUTPUT_AST_TMP}/units.json"
}

function output_ast_parse() {
  local source="${1}"
  : > "${OUTPUT_AST_TMP}/parse.err" || return 2
  capture_child - --stdout "${OUTPUT_AST_TMP}/ast.json" -- \
    shfmt --language-dialect bash --to-json 2> "${OUTPUT_AST_TMP}/parse.err" < "${source}" # error-output-allow: parser and input-open failures are retained for classification
}

function output_ast_native_valid() {
  local classification
  classification="$(jq -er -s '
    if length != 1 or .[0].Type != "File" then "invalid"
    elif any(.[0] | .. | objects | select(has("Hash") and has("Text"));
      .Text | contains("\n")) then "continued-comment"
    else "valid" end' "${OUTPUT_AST_TMP}/ast.json")" || return 2
  case "${classification}" in
    valid) return 0 ;;
    continued-comment) return "${OUTPUT_AST_NATIVE_LIMIT}" ;;
    *) return 2 ;;
  esac
}

function output_ast_expected_syntax_failure() {
  [[ "${1}" -eq 1 ]] || return 1
  LC_ALL=C awk '
    NR == 1 { expected = $0 ~ /^[0-9]+:[0-9]+: .+/ }
    END { exit !expected }
  ' "${OUTPUT_AST_TMP}/parse.err"
}

function output_ast_analyze() {
  jq -n --argjson include_scope "${ast_scope:-false}" --slurpfile ast "${OUTPUT_AST_TMP}/ast.json" --slurpfile units "${OUTPUT_AST_TMP}/units.json" \
    --slurpfile excluded "${OUTPUT_AST_TMP}/excluded.jsonl" \
    -f "${OUTPUT_AST_LIBRARY_DIR}/error-output-ast.jq" > "${OUTPUT_AST_TMP}/report.json"
}

function output_ast_documents() {
  local file="${1}" index="${2}"
  awk -v file="${file}" -v source_index="${index}" -v dir="${OUTPUT_AST_TMP}" '
    function begin() {
      block++
      active = 1
      origin = FNR + (cram ? 0 : 1)
      stream = !cram && fence ~ /^\140\140\140+scrut[\t ]*$/ ? "stdout" : "unknown"
      source = dir "/source-" source_index "-" block
      printf "%s", "" > source
    }
    function finish() {
      if (!active) return
      close(source)
      print file "#block-" block "\t" file "\t" origin "\t" source "\t" stream
      active = 0
    }
    BEGIN { cram = file ~ /[.](t|cram)$/ }
    {
      fence = $0
      sub(/^[\t ]*/, "", fence)
      if (!cram && fence ~ /^\140\140\140+scrut([\t {]|$)/) {
        if (active) { print file ": nested Scrut fence" > "/dev/stderr"; exit 1 }
        opening = fence
        sub(/[^\140].*$/, "", opening)
        begin()
        next
      }
      if (!cram && active && fence ~ /^\140\140\140/) {
        ending = fence
        sub(/[^\140].*$/, "", ending)
        if (length(ending) >= length(opening)) { finish(); next }
      }
      if (cram && $0 ~ /^[\t ]*[$] /) { finish(); begin() }
      if (!active) next
      text = $0
      if (text ~ /^[\t ]*[$>] /) sub(/^[\t ]*[$>] /, "", text)
      else text = ""
      print text > source
    }
    END {
      if (active && !cram) {
        print file ": unterminated Scrut fence" > "/dev/stderr"
        exit 1
      }
      finish()
    }
  ' "${file}" >> "${OUTPUT_AST_TMP}/sources.tsv"
}

function output_ast_shell() {
  local file="${1}" first_line="${2}" interpreter arguments
  if [[ "${first_line}" == '#!'* ]]; then
    IFS=$' \t' read -r interpreter arguments <<< "${first_line:2}"
    if [[ "${interpreter##*/}" == env ]]; then
      IFS=$' \t' read -r interpreter arguments <<< "${arguments}"
      if [[ "${interpreter}" == -S ]]; then
        IFS=$' \t' read -r interpreter arguments <<< "${arguments}"
      fi
    fi
    [[ "${interpreter##*/}" == bash || "${interpreter##*/}" == sh ]]
  else
    [[ "${file}" == *.bash || "${file}" == *.sh ]]
  fi
}

function check_error_output_ast() {
  local file first_line index=0 reason name origin source stream parse_reason
  command -v shfmt > /dev/null || {
    echo 'shfmt is required for the error-output guard' >&2
    return 1
  }
  command -v jq > /dev/null || {
    echo 'jq is required for the error-output guard' >&2
    return 1
  }
  if ! jq -e -s '
    def entry: type == "object" and keys == ["name","reason"]
      and (.name | type == "string" and test("^[^\\t\\r\\n]+$"))
      and (.reason | type == "string" and test("\\S"));
    length == 1 and (.[0] | type == "object" and keys == ["non_bash","parse_exceptions"]
      and ([.non_bash,.parse_exceptions] | all(type == "array" and all(entry)))
      and ([.non_bash[].name,.parse_exceptions[].name] as $names |
        ($names | length) == ($names | unique | length)))
  ' bin/lib/error-output-policy.json > /dev/null; then
    echo 'error-output policy must contain unique names and nonempty reasons' >&2
    return 1
  fi
  OUTPUT_AST_TMP="$(mktemp -d "${TMPDIR:-/tmp}/output-ast.XXXXXX")"
  readonly OUTPUT_AST_TMP
  trap 'rm -r "${OUTPUT_AST_TMP}"' EXIT
  : > "${OUTPUT_AST_TMP}/sources.tsv"
  : > "${OUTPUT_AST_TMP}/excluded.jsonl"
  : > "${OUTPUT_AST_TMP}/used-policy"
  for file in "$@"; do
    index=$((index + 1))
    case "${file}" in
      Makefile | .github/workflows/*) continue ;;
      tests/scrut/*)
        output_ast_documents "${file}" "${index}"
        continue
        ;;
      *) ;;
    esac
    first_line=''
    case "${file}" in
      *.json | *.md | *.yaml | *.yml | *.graphql) ;;
      *) IFS= read -r first_line < "${file}" || true ;;
    esac
    if ! output_ast_shell "${file}" "${first_line}"; then
      reason="$(output_ast_reason non_bash "${file}")"
      if [[ -z "${reason}" ]]; then
        printf '%s: non-Bash source needs a named exclusion with a reason\n' "${file}"
        return 1
      fi
      jq -cn --arg name "${file}" --arg reason "${reason}" \
        '{name:$name, kind:"non-Bash", reason:$reason}' >> "${OUTPUT_AST_TMP}/excluded.jsonl"
      printf '%s\n' "${file}" >> "${OUTPUT_AST_TMP}/used-policy"
      continue
    fi
    source="${OUTPUT_AST_TMP}/source-${index}"
    cp "${file}" "${source}"
    printf '%s\t%s\t1\t%s\tscript\n' "${file}" "${file}" "${source}" >> "${OUTPUT_AST_TMP}/sources.tsv"
  done
  local parse_names
  parse_names=$'\n'"$(jq -r '.parse_exceptions[].name' bin/lib/error-output-policy.json)"$'\n'
  : > "${OUTPUT_AST_TMP}/accepted.tsv"
  while IFS=$'\t' read -r name file origin source stream; do
    parse_reason=''
    if [[ "${parse_names}" == *$'\n'"${name}"$'\n'* ]]; then
      parse_reason="$(output_ast_reason parse_exceptions "${name}")"
    fi
    if [[ -n "${parse_reason}" ]]; then
      local parser_status native_status
      if output_ast_parse "${source}"; then
        if output_ast_native_valid; then
          printf '%s: parse exception is unused; shell input parses successfully\n' "${name}"
          return 1
        else
          native_status=$?
        fi
        if [[ "${native_status}" -ne "${OUTPUT_AST_NATIVE_LIMIT}" ]]; then
          printf '%s: shfmt returned an invalid AST while checking a parse exception\n' "${name}"
          return 1
        fi
      else
        parser_status=$?
        if ! output_ast_expected_syntax_failure "${parser_status}"; then
          printf '%s: unexpected shfmt failure (status %s) while checking a parse exception\n' "${name}" "${parser_status}"
          cat "${OUTPUT_AST_TMP}/parse.err" >&2
          return 1
        fi
      fi
      jq -cn --arg name "${name}" --arg reason "${parse_reason}" \
        '{name:$name, kind:"parse exception", reason:$reason}' >> "${OUTPUT_AST_TMP}/excluded.jsonl"
      printf '%s\n' "${name}" >> "${OUTPUT_AST_TMP}/used-policy"
    else
      printf '%s\t%s\t%s\t%s\t%s\n' "${name}" "${file}" "${origin}" "${source}" "${stream}" >> "${OUTPUT_AST_TMP}/accepted.tsv"
    fi
  done < "${OUTPUT_AST_TMP}/sources.tsv"
  output_ast_pack "${OUTPUT_AST_TMP}/accepted.tsv"
  if ! output_ast_parse "${OUTPUT_AST_TMP}/input.bash"; then
    local error_line culprit='shell unit bundle'
    error_line="$(awk -F : 'NR == 1 && $1 ~ /^[0-9]+$/ { print $1 }' "${OUTPUT_AST_TMP}/parse.err")"
    if [[ -n "${error_line}" ]]; then
      name="$(jq -r --argjson line "${error_line}" \
        '.[] | select(.open <= $line and .close >= $line) | .name' "${OUTPUT_AST_TMP}/units.json")"
      [[ -z "${name}" ]] || culprit="${name}"
    fi
    printf '%s: shfmt cannot parse shell input; a named parse exception needs a reason\n' "${culprit}"
    cat "${OUTPUT_AST_TMP}/parse.err" >&2
    return 1
  fi
  if ! output_ast_analyze; then
    echo 'shfmt AST unit boundaries or structure are invalid; no shell units accepted'
    return 1
  fi
  jq -r '.non_bash[].name,.parse_exceptions[].name' bin/lib/error-output-policy.json | LC_ALL=C sort > "${OUTPUT_AST_TMP}/policy-names"
  LC_ALL=C sort "${OUTPUT_AST_TMP}/used-policy" > "${OUTPUT_AST_TMP}/used-names"
  if ! cmp -s "${OUTPUT_AST_TMP}/policy-names" "${OUTPUT_AST_TMP}/used-names"; then
    echo 'error-output policy contains unused exclusions'
    return 1
  fi
  if [[ "${ast_scope:-false}" != true ]]; then
    jq -r '.errors | group_by(.name)[] |
      .[0].name + (if any(.[]; .kind == "parse")
        then ": shfmt AST is unsafe for this shell input; a named parse exception needs a reason"
        elif any(.[]; .kind == "stream-context")
        then ": unresolved stream context (" + ([.[] | select(.kind == "stream-context") | .construct] | unique | join(", ")) + "); add # error-output-allow: reason"
        elif any(.[]; .kind == "discard")
        then ": retain child errors or add # error-output-allow: reason"
        else ": use capture_child for retained diagnostics" end)' "${OUTPUT_AST_TMP}/report.json"
  fi
}
