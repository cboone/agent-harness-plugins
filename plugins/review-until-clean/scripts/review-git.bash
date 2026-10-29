# Shared Git policy for collecting scope and rendering reviewer commands.
# Sourced by the review helpers; this file does not execute a workflow.
REVIEW_GIT_OPTIONS=(-c diff.ignoreSubmodules=none)
REVIEW_DIFF_OPTIONS=(--ignore-submodules=none --submodule=diff --no-ext-diff --no-textconv --no-color --no-relative --no-renames)
readonly REVIEW_GIT_OPTIONS REVIEW_DIFF_OPTIONS

function review_git() {
  git "${REVIEW_GIT_OPTIONS[@]}" "$@"
}

function review_diff() {
  review_git diff "${REVIEW_DIFF_OPTIONS[@]}" "$@"
}

function review_prompt_diff_args() {
  printf '%q ' "${REVIEW_GIT_OPTIONS[@]}" diff "${REVIEW_DIFF_OPTIONS[@]}"
}

REVIEW_PATH_DEFS='
  def relative_path:
    type == "string" and length > 0
    and (startswith("/") | not)
    and (split("/") | all(. != "" and . != "." and . != ".."));
  def safe_path:
    relative_path and (startswith("~") | not) and (test("\\\\") | not);
'
readonly REVIEW_PATH_DEFS

REVIEW_MEMBERSHIP_DEFS="${REVIEW_PATH_DEFS}"'
  def review_paths($bucket):
    [.membership[] | select($bucket == "all" or (.buckets | index($bucket) != null)) | .path];
  def review_bucket_views:
    .committed = review_paths("committed") | .staged = review_paths("staged")
    | .unstaged = review_paths("unstaged") | .untracked = review_paths("untracked")
    | .empty = ((review_paths("all") | length) == 0);
  def review_compile_membership:
    [(.committed[] | {path: ., bucket: "committed"}),
     (.staged[] | {path: ., bucket: "staged"}),
     (.unstaged[] | {path: ., bucket: "unstaged"}),
     (.untracked[] | {path: ., bucket: "untracked"})]
    | group_by(.path) | map({path: .[0].path, buckets: (map(.bucket) | unique)});
  def review_membership_valid:
    type == "object"
    and (.membership | type == "array" and all(type == "object"
      and (keys == ["buckets", "path"]) and (.path | relative_path)
      and (.buckets | type == "array" and length > 0
        and all(IN("committed", "staged", "unstaged", "untracked")) and . == (unique))))
    and ((.membership | map(.path) | length) == (.membership | map(.path) | unique | length))
    and (.files | type == "array" and all(relative_path))
    and (.committed == review_paths("committed")) and (.staged == review_paths("staged"))
    and (.unstaged == review_paths("unstaged")) and (.untracked == review_paths("untracked"))
    and ((review_paths("untracked") - .files) | length == 0)
    and (.empty == ((review_paths("all") | length) == 0));
'
readonly REVIEW_MEMBERSHIP_DEFS

function review_read_membership() {
  jq -ce "${REVIEW_MEMBERSHIP_DEFS}"'
    if review_membership_valid then .membership else error("invalid review membership") end
  ' -- "${1}"
}

function review_membership_paths() {
  jq -c "${REVIEW_MEMBERSHIP_DEFS}"'{membership: .} | review_paths("all")' "${1}"
}

# Discovery and renderers use rooted operands while annotations keep relative paths.
function review_symlinks() {
  local scope="${1}" repo="${2}" directory="${3}"
  local path operand target
  review_read_membership "${scope}" > "${directory}/link-members.json" || return
  review_membership_paths "${directory}/link-members.json" > "${directory}/link-paths.json" || return
  jq -j '.[] | ., "\u0000"' "${directory}/link-paths.json" > "${directory}/link-paths.raw" || return
  : > "${directory}/link-records.jsonl" || return
  while IFS= read -r -d '' path; do
    if review_has_non_directory_parent "${repo}" "${path}"; then continue; fi
    operand="${repo}/${path}"
    if [[ -L "${operand}" ]]; then
      target="$(readlink -n "${operand}" && printf x)" || return
      target="${target%x}"
      jq -cn --arg path "${path}" --arg target "${target}" \
        '{path: $path, kind: "symlink", target: $target}' >> "${directory}/link-records.jsonl" || return
    fi
  done < "${directory}/link-paths.raw"
  jq -s --slurpfile paths "${directory}/link-paths.json" \
    '{membership_paths: $paths[0], links: .}' "${directory}/link-records.jsonl"
}

# Check each parent before descending, so a replaced directory cannot redirect
# a real-index gitlink into a symlink target outside the disk snapshot.
function review_has_non_directory_parent() {
  local current="${1}" remaining="${2}"
  while [[ "${remaining}" == */* ]]; do
    current="${current}/${remaining%%/*}"
    if [[ -L "${current}" ]]; then return 0; fi
    if [[ -e "${current}" && ! -d "${current}" ]]; then return 0; fi
    remaining="${remaining#*/}"
  done
  return 1
}

# Raw diff records keep modes and object IDs beside each NUL-delimited path.
# Expand only initialized, captured gitlinks, using their exact transitions.
function collect_diff_paths() {
  local repo="${1}" modules="${2}" prefix="${3}" disk="${4}" output="${5}"
  shift 5
  local raw entry path old_mode new_mode old_id new_id _status child child_modules
  local before after lookup_status child_repo
  raw="$(mktemp "${TMP_DIR}/diff-records.XXXXXX")" || die "could not create diff records"
  review_git -C "${repo}" diff "${REVIEW_DIFF_OPTIONS[@]}" --raw -z --no-abbrev "$@" > "${raw}" \
    || die "could not collect review paths in ${repo}"
  while IFS= read -r -d '' entry; do
    IFS= read -r -d '' path || die "Git returned a truncated raw diff"
    printf '%s\0' "${prefix}${path}" >> "${output}" || die "could not record a changed path"
    read -r old_mode new_mode old_id new_id _status <<< "${entry#:}"
    if [[ "${old_mode}" != 160000 && "${new_mode}" != 160000 ]]; then continue; fi
    child="$(mktemp "${TMP_DIR}/diff-child.XXXXXX")" || die "could not create child diff records"
    if jq -ec --arg path "${path}" '.[] | select(.path == $path and .initialized)' \
      "${modules}" > "${child}"; then
      :
    else
      lookup_status=$?
      [[ "${lookup_status}" -eq 4 ]] && continue
      die "could not locate captured submodule: ${path}"
    fi
    [[ "${old_mode}" == 160000 ]] || old_id=""
    if [[ "${new_mode}" != 160000 ]]; then
      new_id=""
    elif [[ "${disk}" == true ]]; then
      new_id="$(jq -r '.scope.head' "${child}")" || die "could not read child HEAD"
    fi
    [[ "${old_id}" != "${new_id}" ]] || continue
    child_repo="${repo}/${path}"
    if [[ -n "${old_id}" ]]; then
      before="$(review_git -C "${child_repo}" rev-parse --verify "${old_id}^{commit}^{tree}")" \
        || die "could not read prior gitlink object: ${prefix}${path}"
    else
      before="$(review_git -C "${child_repo}" mktree < /dev/null)" || die "could not create empty tree"
    fi
    if [[ -n "${new_id}" ]]; then
      after="$(review_git -C "${child_repo}" rev-parse --verify "${new_id}^{commit}^{tree}")" \
        || die "could not read current gitlink object: ${prefix}${path}"
    else
      after="$(review_git -C "${child_repo}" mktree < /dev/null)" || die "could not create empty tree"
    fi
    child_modules="${child}.modules"
    jq '.scope.submodules' "${child}" > "${child_modules}" || die "could not read nested submodules"
    collect_diff_paths "${child_repo}" "${child_modules}" "${prefix}${path}/" false \
      "${output}" "${before}" "${after}" || die "could not expand submodule: ${path}"
  done < "${raw}"
}

function write_diff_bucket() {
  local bucket="${1}" disk="${2}"
  shift 2
  : > "${TMP_DIR}/${bucket}.raw" || die "could not create diff bucket"
  collect_diff_paths "${top_level}" "${TMP_DIR}/submodules.json" "" "${disk}" \
    "${TMP_DIR}/${bucket}.raw" "$@" || die "could not collect ${bucket} paths"
  paths_to_json < "${TMP_DIR}/${bucket}.raw" > "${TMP_DIR}/${bucket}.json" \
    || die "could not encode ${bucket} paths"
}

# Inventory includes disk files, symlink entries and uninitialized gitlinks.
# Initialized gitlinks are replaced with the child's own recursive inventory.
function write_file_inventory() {
  GIT_INDEX_FILE="${TMP_DIR}/index" review_git ls-files --stage -z > "${TMP_DIR}/files.raw" \
    || die "could not inventory working-tree files"
  jq -Rs --slurpfile modules "${TMP_DIR}/submodules.json" '
    [split("\u0000")[] | select(length > 0 and (startswith("160000 ") | not))
      | .[index("\t") + 1:]]
    + [$modules[0][] | .path as $path | if .initialized
       then .scope.files[] | $path + "/" + . else $path end] | unique
  ' "${TMP_DIR}/files.raw" > "${TMP_DIR}/files.json" || die "could not encode file inventory"
}

function extend_submodule_buckets() {
  local bucket
  # Expand Git's embedded-repository dir/ entries into captured file paths.
  jq --slurpfile modules "${TMP_DIR}/submodules.json" '
    map(. as $entry | if endswith("/") then
      ([$modules[0][] | select(.initialized and (.path + "/") == $entry)]
       | if length == 1 then .[0] else error("uncaptured untracked repository: " + $entry) end) as $module
      | $module.scope.files[] | $module.path + "/" + .
      else . end) | unique
  ' "${TMP_DIR}/untracked.json" > "${TMP_DIR}/untracked.expanded" \
    || die "could not expand untracked repository files"
  mv "${TMP_DIR}/untracked.expanded" "${TMP_DIR}/untracked.json" || die "could not store untracked files"
  for bucket in staged unstaged untracked; do
    jq --arg bucket "${bucket}" --slurpfile modules "${TMP_DIR}/submodules.json" "${REVIEW_MEMBERSHIP_DEFS}"'
      . + [$modules[0][] | select(.initialized) | .path as $path
           | .scope | review_paths($bucket)[] | $path + "/" + .] | unique
    ' "${TMP_DIR}/${bucket}.json" > "${TMP_DIR}/${bucket}.extended" \
      || die "could not extend ${bucket} with submodule paths"
    mv "${TMP_DIR}/${bucket}.extended" "${TMP_DIR}/${bucket}.json" \
      || die "could not store ${bucket} paths"
  done
}

# Compute the canonical path records once from transitions and child-local views.
function review_build_membership() {
  local top_level="${1}" TMP_DIR="${2}" merge_base="${3}" head="${4}"
  if [[ -n "${merge_base}" && "${merge_base}" != "${head}" ]]; then
    write_diff_bucket committed false "${merge_base}" "${head}"
  else
    write_empty_bucket committed
  fi
  write_diff_bucket staged false --cached
  write_diff_bucket unstaged true
  write_bucket untracked review_git ls-files -z --others --exclude-standard
  cp "${TMP_DIR}/untracked.json" "${TMP_DIR}/untracked-parent.json" || die "could not preserve parent paths"
  write_file_inventory
  extend_submodule_buckets
  jq -cn "${REVIEW_MEMBERSHIP_DEFS}"'
    {committed: $c[0], staged: $s[0], unstaged: $u[0], untracked: $n[0]} | review_compile_membership
  ' --slurpfile c "${TMP_DIR}/committed.json" --slurpfile s "${TMP_DIR}/staged.json" \
    --slurpfile u "${TMP_DIR}/unstaged.json" --slurpfile n "${TMP_DIR}/untracked.json" \
    > "${TMP_DIR}/membership.json" || die "could not build canonical membership"
}
