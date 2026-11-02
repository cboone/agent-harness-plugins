# Bash 3.2 empty-list ledger

## Authority and scope

- Worker: `433-bash32-empty-lists`, TOOLING conductor, Codex `normal-max-default`.
- Go-ahead: Inbox “Tooling overnight batch, Oct 28”, 9:16 PM EDT,
  2026-10-28, through a PR ready for review. Worker never merges.
- Repository: `cboone/agent-harness-plugins`; active, not a fork, no upstream.
- Base: `7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`, the actual merge base
  with `origin/main` at start. Working tree initially clean.
- Issue read in full, including its empty comments array. No separate
  “Done when” section exists in the retrieved body.
- Hook scripts remain unchanged. The notify and focus-pane positional-list
  sites mentioned in the issue are already fixed at this base.

## Implementation

Replace braced positional lists throughout the Bash scripts and fixtures,
including embedded `$*` diagnostics. Guard `segments` in `pr/branch-issues`:
an empty string or `/` yields no segments. Guard the curl fixture's `args`
when it logs a request with no flags. Neither changes argument boundaries.

Patch versions: `pr` 1.11.1 to 1.11.2, `workmux` 1.1.4 to 1.1.5,
`publish-report-board` 1.3.3 to 1.3.4. The launch helper now belongs to
`workmux`, rather than the two older plugin paths named in the issue.
Regenerate mirrors with `make build`.

`make test-bash32` checks `/bin/bash` is 3.2 before running the empty-list
document. The normal suite also runs this document on Linux's native Bash;
that Linux run alone does not establish Bash 3.2 compatibility. No CI job or
installed shell is added.

## Inventory disposition

The searches below cover `bin`, canonical `plugins` and test fixtures,
including nonexecutable `.bash` libraries and the nested version-audit
template. Markdown examples, JSON, jq and HTML are excluded. Generated
mirrors are regenerated, not audited as separate sources.

- Braced positional lists: all matches fixed, including sites already
  receiving arguments, for consistent forwarding. Hook matches: none.
- Empty arrays fixed: `pr/branch-issues` `segments`, and
  `tests/fixtures/ntfy-curl-stub` `args`.
- Already guarded: `sources`, `WORKTREE_PATHS`, `MESSAGE_TAGS`,
  `client_owners`, `names`, `RUNNING_GROUPS`, `RUNNING_PIDS`,
  `uninitialized_gitlinks`, `GUIDE_NAMES`, `args` in `cmd_gate`,
  `extra_args`, `base_args`, `helper_args`, `sound_args` and
  `candidates` in cross-reference checking.
- Length-guarded: cross-reference `files` and `candidates`, fixture-checker
  `files`, corpus `requested`, resource-claim `keys`, attention-log `files`,
  launcher `env_args` and `candidates`, document runner `documents` and
  `failed`, report `owners`, version-audit `drift_rows`, aspect `reviews`,
  `aspects` and `gate_inputs`. Length and arithmetic-only uses are safe.
- Fixed nonempty lists: `SHARED_REFERENCES`, validator required-field and
  allowlist arrays, `CASE_FILES`, `SCAN_PATHS`, `REVIEW_GIT_OPTIONS`,
  `REVIEW_DIFF_OPTIONS`, `KNOWN_ASPECTS`, cleanup `angles`, `curl_args`,
  launcher `dirs`, `command` and detached `cmd`.
- Input-derived nonempty lists: cross-reference `prefix_list` starts from
  `plugins|dist/codex`; launcher `issues` receives a validated numeric issue;
  cleanup `files` receives four required paths before expansion; aspect
  `statuses` follows a required nonempty aspect list; fixture `recorded`
  contains required `--output-last-message` before logging.
- Notify `words` length is checked before indexed access. Its slice from
  index 1 safely expands to nothing for a one-word list on `/bin/bash` 3.2,
  confirmed directly. The sound array is already guarded. No hook edit.

## Validation and plants

- Dependencies restored with `YARN_ENABLE_SCRIPTS=false corepack yarn install --immutable`.
- `/bin/bash --version`: 3.2.57(1)-release, arm64-apple-darwin25.
- `make build`: passed.
- `make test-bash32`: 15 cases passed, none failed or skipped.
- Four plants restored the original generator forwarding, report-board render
  dispatch, branch segment expansion and curl argument logging, one at a time.
  Every planted run failed exactly its corresponding case: 14 passed, 1 failed,
  none skipped, `make` exit 2. The generator, branch and curl runs showed the
  expected unbound-variable diagnostic; render failed its expected usage-status
  assertion. Source restored after each plant. Logs are in
  `/tmp/433-bash32-evidence.TEE1Y0/{generator,dispatch,segments,curl}-plant.log`.
- `make lint-shell`: ShellCheck and shfmt passed.
- Full `make test-scrut` with a recorded temporary PATH entry pointing `bash`
  at `/bin/bash`: several documents passed, including the focused regressions
  and `codex-failure-rollouts`. The run was stopped with TERM to its confirmed
  owned runner PID 4527 after the mandatory review stop. The runner exited,
  `make` returned 2. This is an incomplete suite, never a pass.
- Whole `make test-all`, baseline Semgrep, trims, final lint-and-fix,
  check-versions and tidy: not run because the review stop precedes them.
- `[*]` follow-up search found four sites: `KNOWN_ASPECTS` is fixed nonempty;
  report-board `names` and both GitHub fixtures' `variables` use defaults.
  None needs changing.

## Reviews

Full local order required. Every completed finding records reviewer label,
assessed severity, take or record, and whether behavior changed.

Structural Nit round started two standalone `codex exec` reviews in parallel:
anti-patterns and report-only simplify, each `gpt-6.1-sol`, high effort,
872000-token context, read-only sandbox, approvals never, web disabled,
ephemeral, stdin closed. Simplify was given all four cleanup angles inline.
The project process explicitly requires this standalone path for Codex workers.

Both processes failed tool initialization with the brief's mandatory stop:

```text
2026-10-29T21:32:54.613924Z ERROR codex_core::tools::router: error=timed out negotiating with the code-mode host
2026-10-29T21:32:56.410859Z ERROR codex_core::tools::router: error=timed out negotiating with the code-mode host
```

These occurred at 5:32:54 PM and 5:32:56 PM EDT on 2026-10-29. Neither review
produced a reply file. The worker sent TERM to its recorded reviewer PIDs
25157 and 25155; both exits were observed as 143. No fallback or retry ran.
The round is **incomplete**, with no findings available, not clean at any
threshold. No round advanced. Aspect review and trims have not started.

The scope before and after the reviews has identical tree
`19dc1e286463f8220244bbc0a49682073f2b0f9e`, `scope_changed=false`,
`changed=[]`, `outside_scope=[]`: no lasting changes found.

External evidence directory: `/tmp/433-bash32-evidence.TEE1Y0`, including
`structural/anti.log`, `structural/simplify.log`, scope files, plant logs and
`bash32-suite.log`. No push, PR, merge or live configuration change occurred.
Implementation and regression tests are committed.

### Authorized resumption

TOOLING relayed restart authority at 6:27 PM EDT on 2026-10-29: the approved
ramp rules, second revision, Inbox “Ramp goals”, answer “Resume after the
measurement” at 1:10 PM EDT. The rule at
`~/.local/state/conductor/ramp-goals.md` was read and verified: restarting a
stopped worker on its next step and reviews need no additional gate. This
opens the next local review step, not rebases, retargets or scope changes.
The two earlier attempts remain failed runs, not completed review rounds.
New evidence directory: `/tmp/433-resumed-review.5Y75to`.

### Structural Nit round

Both resumed reviewers exited 0 with valid, nonempty replies. Anti-patterns
passed `result-check.jq`, `status=success`, `complete=true`, no unread scope.
Simplify passed `codex-aspects validate`, all four cleanup angles reviewed
inline, no findings. No lasting changes: scope comparison returned
`scope_changed=false`, `changed=[]`, `outside_scope=[]`.

Anti-patterns reported two pre-existing defects with reviewer label `important`,
both assessed **Important** without a downgrade:

1. `bin/check-cross-references`, `check_file`: an unreadable explicitly named
   file is treated as no matching references. **Record**, outside the
   empty-list brief, and report to TOOLING. No behavior changed, no rerun.
1. `bin/build-codex-marketplace`, catalog-reading process substitutions: a
   failed producer such as missing jq can look like an empty catalog and
   produce an empty successful build. **Record**, outside the empty-list
   brief, and report to TOOLING. No behavior changed, no rerun.

The tool explicitly said its overall result was not clean because of these
pre-existing findings. For this branch's introduced changes: **clean at Nit**.
The structural loop ends with no takes or behavior changes. These are not a
recurrence: no earlier successful round fixed this class in this workstream.
Read-only reviewers did not rerun tests or plants; their unverified runtime
checks are covered by the worker's separately recorded validation. Ownership
and archive metadata were verified in the parent before review, despite the
review sandbox's unsuccessful API query.

Aspect review next: `code`, `errors`, `tests`, `comments`, same standalone
read-only `gpt-6.1-sol` / high / 872000 settings. `errors` includes the new
Bash-version failure guard; `types` omitted because no type or schema changed.

### Aspect Nit round

One completed round: `code`, `errors`, `tests`, `comments`. Each exited 0,
passed the helper's schema, snapshot and membership checks, and returned zero
findings. **Clean at Nit**. No behavior-changing fixes and no further round.
The before/after scope is unchanged, with no lasting changes found. Runtime
execution was not claimed by the sandboxed reviewers. `types` was omitted
because no types or schemas changed.

### Additional validation findings

The worker's broader Bash 3.2 suite exposed the new document's missing
Git-environment reset. The repository guard independently reproduced the
failure. **Take**: add the standard fail-fast source block before fixture
calls. Test setup only; production behavior unchanged, so no review rerun.
This is a local-check finding, not a reviewer severity downgrade.

The `record-traffic` document failed under Bash 3.2 with an unexpected EOF
parse error in `bin/record-traffic`. `/bin/bash -n` against that file from the
unchanged merge base reproduces the same error. **Record**, pre-existing
syntax compatibility outside the empty-list scope, reported to TOOLING.
The exploratory full Bash 3.2 suite is not green; the focused compatibility
target and required standard suite are reported separately.

### Trim round

`trim-comments` and `trim-text` each exited 0 with a nonempty, well-formed
proposal reply, using standalone read-only `gpt-6.1-sol`, low effort, 872000
context, approvals never, web disabled, stdin closed. No lasting changes:
`scope_changed=false`, `changed=[]`, `outside_scope=[]`.

No changed code comments were eligible. The comments run proposed two edits
to Markdown prose; both were rejected as outside that skill's comment scope.
The text run classified all three prose files under profile `none`. Its
three wording-only proposals were accepted: shorten the authorization wording,
the unchanged Important assessment, and the inventory introduction. Evidence,
requirements and fenced search results remain intact. No behavior changed.
One trim round completed; no rerun required.

### Semgrep baseline

Semgrep 1.180.0 ran in the disposable shared clone
`/tmp/433-resumed-review.5Y75to/semgrep-clone`, branch head `5ba1607d`,
with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, `--config p/default`,
`--metrics off`, and `--baseline-commit
7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`.
Exit 0: 54 applicable rules, 11 targets, zero findings. This is baseline mode,
limited to changed files. Semgrep skipped the second baseline checkout because
the current scan found nothing.

Coverage is limited: `plugins/publish-report-board/scripts/report-board` was
wholly unparsed; `plugins/workmux/scripts/launch-workmux` was partly parsed
(lines 3 through 872). The summary reported approximately 78.8 percent parsed
lines and 13 files excluded by ignore rules, including the fixture paths.
These parser gaps are not a full semantic pass. The brief permits partly or
wholly unparsed shell files when coverage is recorded and ShellCheck passes;
`make lint-shell` passed for every canonical shell script, including both.
JSON and log evidence are in the resumed evidence directory.

### Final formatting, lint and version checks

`lint-and-fix --no-push` followed repository commands: `make format` for
Markdownlint, Prettier and shfmt, then `make test-all`'s check-only lint for
Markdownlint, Prettier, ShellCheck, shfmt and Actionlint. Formatting removed
literal trailing spaces in three new snapshot lines. The snapshots now use
`sed -n l` to render those spaces explicitly; the GitHub error pipeline has
`pipefail` to retain the subject status. Test assertions only, no production
change. The focused document and formatting checks passed after correction.
The relevant fix was signed in `1f2b5b8a`; no push was performed by lint.

Lint status: **success**. No missing tools, unresolved findings or skipped
required lint checks. `make test-all` has passed lint and validation; its
standard Bash 5 Scrut phase remains in progress. `make test-bash32` now passes
16 cases, none failed or skipped.

The local `check-versions` skill passed: explicit default branch `main`, actual
merge base unchanged after fetch, forward patch bumps for `pr` 1.11.1 to
1.11.2, `workmux` 1.1.4 to 1.1.5 and `publish-report-board` 1.3.3 to 1.3.4.
All 60 plugin directories match catalog entries; all manifest versions are
valid, present Codex manifests agree, and no catalog entry or metadata owns a
version. `origin/main` still has the three original versions.

The exploratory all-Bash-3.2 run also reported one `launch-workmux` testcase
failure: its pre-existing cleanup testcase passes `BASHPID` as the issue
number, but Bash 3.2 has no `BASHPID`. The subject receives an empty issue,
returns its expected usage error and the test expects the wrong diagnostic.
The other 67 cases passed. **Record**, test portability outside the empty-list
brief; no production fix or test expansion taken. Diagnostics were retained
in `launch-workmux-bash32-details.log`. The earlier environment-isolation
failures came from the missing reset now fixed in the new document.

### Final results and publication handoff

`SCRUT_JOBS=4 make test-all` completed with exit 0 on 2026-10-29 at
6:55 PM EDT: all 53 documents, 1,839 cases succeeded, zero failed or skipped.
This includes the corrected fixture reset, explicit-space snapshots, the
launcher, both validators and `codex-failure-rollouts`. Markdownlint,
Prettier, ShellCheck, shfmt, Actionlint, JSON, fixture isolation, plugin and
mirror validation all passed. `make test-bash32` separately passed all
16 native Bash 3.2 cases. No source code changed after the final lint run.

The exploratory full-suite Bash 3.2 run finished with 50 of 53 documents
passing, exit 2 from make. The three failures were environment-isolation
(the new reset subsequently fixed and verified by the required standard
suite), `record-traffic` (base-confirmed parser incompatibility) and the
launcher test's pre-existing `BASHPID` use. This run is not a compatibility
pass for the entire repository. The two remaining portability concerns and
the structural review's pre-existing Important findings were reported to
TOOLING for separate triage. None required a hook change.

The repeatable search covers every executable Bash script: all 94 paths
returned by `bin/list-shell-scripts` are under `bin`, `plugins` or `tests`.
The inventory additionally includes nonexecutable shell libraries. Empty
positional slices such as `"${@:3}"` were directly checked under Bash 3.2
and expand to zero words without an unbound-variable failure.

Completed local sequence: structural Nit round (branch changes clean at Nit,
pre-existing concerns recorded); aspect Nit round **clean at Nit**; one trim
round; baseline Semgrep with recorded parser limits; lint-and-fix **success**;
version check **clean**; `make test-all` and focused compatibility **passed**;
four detected original-defect plants restored. The two earlier host failures
are failed attempts, not completed rounds.

Publication proceeds through the pre-push tidy required by the process:
create a backup branch, soft-reset to the recorded merge base, form logical
signed feature, test and documentation commits, and compare the resulting
HEAD tree with the backup. The measured tidy result and ready PR URL are
reported in the worker's final TOOLING mailbox handoff. No merge is authorized
for this worker.

## Repeatable search results

Results captured before editing. After the fixes, the first search returns
no matches (exit 1).

```bash
rg -n '\$\{[@*]\}' bin plugins tests \
  --glob '!*.md' --glob '!*.json' --glob '!*.jq' --glob '!*.html'
```

```text
bin/build-codex-marketplace:267:main "${@}"
bin/check-cross-references:677:    for file in "${@}"; do
bin/check-cross-references:721:main "${@}"
plugins/publish-report-board/scripts/report-board:1059:  printf '%s: %s\n' "${SCRIPT_NAME}" "${*}" >&2
plugins/publish-report-board/scripts/report-board:1557:    validate) cmd_validate "${@}" ;;
plugins/publish-report-board/scripts/report-board:1558:    render) cmd_render "${@}" ;;
plugins/publish-report-board/scripts/report-board:1559:    extract) cmd_extract "${@}" ;;
plugins/publish-report-board/scripts/report-board:1560:    compare) cmd_compare "${@}" ;;
plugins/publish-report-board/scripts/report-board:1561:    starter) cmd_starter "${@}" ;;
plugins/publish-report-board/scripts/report-board:1566:main "${@}"
plugins/workmux/scripts/launch-workmux:154:  "${@}"
plugins/workmux/scripts/launch-workmux:344:  local -a command=(workmux "${@}")
plugins/workmux/scripts/launch-workmux:372:  run_workmux_command "${@}"
plugins/workmux/scripts/launch-workmux:546:  run_workmux_and_cleanup_prompt "${prompt_file}" "${@}" > "${state_dir}/log" 2>&1 || status=$?
tests/fixtures/backlog-gather-gh-stub:23:  [[ "${1:-} ${2:-}" == "api graphql" ]] || die "unexpected invocation: gh ${*}"
tests/fixtures/cross-reference-fixture:40:main "${@}"
tests/fixtures/gh-stub:76:  for arg in "${@}"; do
tests/fixtures/gh-stub:105:  for arg in "${@}"; do
tests/fixtures/gh-stub:230:    printf 'gh %s\n' "${*}" >> "${STUB_GH_LOG}"
tests/fixtures/gh-stub:246:    *) die "unexpected invocation: gh ${*}" ;;
tests/fixtures/gh-stub:250:main "${@}"
tests/fixtures/tmux-stub:197:          "${command_name//-/_}" "${socket}" "${@}"
tests/fixtures/workmux-resource-stub:77:      case "${STUB_RESOURCE_SCENARIO:-success}:${*}" in
tests/fixtures/workmux-resource-stub:113:      if [[ "${STUB_RESOURCE_SCENARIO:-success}" == owner-write && "${*}" == *'/dev/fd/8' ]]; then
```

```bash
rg -n '\[@\]' bin plugins tests \
  --glob '!*.md' --glob '!*.json' --glob '!*.jq' --glob '!*.html'
```

```text
bin/build-review-checklists:201:  for source in ${sources[@]+"${sources[@]}"}; do
bin/build-review-checklists:210:  write_copies "${output_dir}" ${sources[@]+"${sources[@]}"}
bin/build-shared-references:58:  for entry in "${SHARED_REFERENCES[@]}"; do
bin/build-shared-references:78:  for entry in "${SHARED_REFERENCES[@]}"; do
bin/build-shared-references:88:  echo "Shared references: ${#SHARED_REFERENCES[@]} copied (${written} written)."
bin/check-cross-references:191:  for prefix in "${prefix_list[@]}"; do
bin/check-cross-references:691:    if [[ ${#files[@]} -gt 0 ]]; then
bin/check-cross-references:692:      candidate_files="$(files_matching "${CANDIDATE_PREFILTER}" "${files[@]}")"
bin/check-cross-references:698:    if [[ ${#candidates[@]} -gt 0 ]]; then
bin/check-cross-references:699:      directive_files="$(files_matching "${DIRECTIVE_PATTERN}" "${candidates[@]}")"
bin/check-cross-references:702:    for file in ${candidates[@]+"${candidates[@]}"}; do
bin/check-fixture-environments:29:  [[ ${#files[@]} -gt 1 ]] || {
bin/check-fixture-environments:185:  ' "${files[@]}"
bin/copilot-rounds-report:387:  [[ ${#owners[@]} -gt 0 ]] || die "at least one --owner is required"
bin/copilot-rounds-report:389:  for login in "${owners[@]}" ${client_owners[@]+"${client_owners[@]}"}; do
bin/copilot-rounds-report:394:  searched=" $(printf '%s ' "${owners[@]}" | tr '[:upper:]' '[:lower:]')"
bin/copilot-rounds-report:395:  for login in ${client_owners[@]+"${client_owners[@]}"}; do
bin/copilot-rounds-report:424:  for owner in "${owners[@]}"; do
bin/copilot-rounds-report:454:  owners_json="$(jq -n -c '$ARGS.positional' --args "${owners[@]}")"
bin/copilot-rounds-report:456:    --args ${client_owners[@]+"${client_owners[@]}"})"
bin/materialize-case:317:    [[ ${#positional[@]} -eq 0 ]] \
bin/materialize-case:326:  if [[ ${#positional[@]} -ne 2 ]]; then
bin/run-scrut-documents:183:  local count="${#documents[@]}"
bin/run-scrut-documents:243:  if ((${#failed[@]} == 0 && xargs_status == 0)); then
bin/run-scrut-documents:248:  printf '%s of %s scrut documents failed:\n' "${#failed[@]}" "${count}"
bin/run-scrut-documents:249:  if ((${#failed[@]} > 0)); then
bin/run-scrut-documents:250:    printf '  %s\n' "${failed[@]}"
bin/run-scrut-documents:304:  if ((${#documents[@]} == 0)); then
bin/run-scrut-documents:310:    printf '%s\n' "${documents[@]}"
bin/run-scrut-documents:323:  if ((${#documents[@]} == 1)); then
bin/run-scrut-documents:339:  run_parallel "${jobs}" "${documents[@]}"
bin/validate-corpus:261:  for name in "${CASE_FILES[@]}"; do
bin/validate-corpus:274:  for name in "${CASE_FILES[@]}"; do
bin/validate-corpus:530:  if [[ ${#requested[@]} -gt 0 ]]; then
bin/validate-corpus:531:    for case_id in "${requested[@]}"; do
bin/validate-plugins:93:  missing="$(missing_fields "${PLUGIN_REQUIRED_FIELDS[@]}" < "${local_json}")"
bin/validate-plugins:168:  | "\($sep)\($entry.name | raw)\($sep)\($field)"' --args "${MARKETPLACE_REQUIRED_FIELDS[@]}" < "${MARKETPLACE}")"
bin/validate-plugins:222:  missing="$(missing_fields "${PLUGIN_REQUIRED_FIELDS[@]}" < "${codex_json}")"
bin/validate-plugins:246:  for field in "${DUAL_MANIFEST_SHARED_FIELDS[@]}"; do
bin/validate-plugins:936:  for allowed in "${SKILL_FRONTMATTER_ALLOWLIST[@]}"; do
bin/validate-plugins:1069:if [[ ${#codex_exec_files[@]} -gt 0 ]]; then
bin/validate-plugins:1115:    ' "${codex_exec_files[@]}"
bin/version-audit:250:  if ((${#drift_rows[@]} == 0)); then
bin/version-audit:261:  for row in "${drift_rows[@]}"; do
plugins/attention-log/scripts/attention-log:705:        for name in ${names[@]+"${names[@]}"}; do
plugins/attention-log/scripts/attention-log:774:    ((${#files[@]} > 0)) || return 0
plugins/attention-log/scripts/attention-log:775:    output="$(jq -Rnr --argjson older "${older}" "${PENDING_JQ}" "${files[@]}")"
plugins/monitor-pr/scripts/merge-flow:568:  for ((i = 0; i < ${#WORKTREE_PATHS[@]}; i++)); do
plugins/monitor-pr/scripts/merge-flow:641:       | select($tree != null) | {pane, worktree: $tree}]' --args ${WORKTREE_PATHS[@]+"${WORKTREE_PATHS[@]}"} <<< "${CAPTURED_OUT}"
plugins/notify/scripts/notify:601:  [[ "${#words[@]}" -gt 0 && "${words[0]##*/}" == codex ]] || return 0
plugins/notify/scripts/notify:602:  for word in "${words[@]:1}"; do
plugins/notify/scripts/notify:822:    ${sound_args[@]+"${sound_args[@]}"} \
plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template:520:  done < <(grep -rHE 'uses:[[:space:]]+[a-zA-Z0-9._/-]+@[a-f0-9]{40}' "${SCAN_PATHS[@]}" 2> /dev/null || true)
plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template:559:  done < <(grep -rHE 'npx[[:space:]]+@?[a-zA-Z0-9._/-]+@[0-9]+\.[0-9]+\.[0-9]+' "${SCAN_PATHS[@]}" 2> /dev/null || true)
plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template:638:  done < <(grep -rHE 'go install [a-zA-Z0-9._/~-]+@v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?' "${SCAN_PATHS[@]}" 2> /dev/null || true)
plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template:674:  done < <(grep -rHE 'cargo install (--locked )?--version [0-9]+\.[0-9]+' "${SCAN_PATHS[@]}" 2> /dev/null || true)
plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template:737:  done < <(grep -rHE '(pip install|uv (pip install|add|tool install)|uvx)[[:space:]].*==[0-9]' "${SCAN_PATHS[@]}" 2> /dev/null || true)
plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template:743:  if ((${#drift_rows[@]} == 0)); then
plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template:754:  for row in "${drift_rows[@]}"; do
plugins/pr/scripts/branch-issues:13:  for segment in "${segments[@]}"; do
plugins/publish-report-board/scripts/backlog-gather:398:  for ((index = 0; index < ${#JOB_PIDS[@]}; index++)); do
plugins/publish-report-board/scripts/bugs-gather:980:  for ((index = 0; index < ${#JOB_PIDS[@]}; index++)); do
plugins/push-notification/scripts/push-notification:321:  tags_json="$(printf '%s\n' ${MESSAGE_TAGS[@]+"${MESSAGE_TAGS[@]}"} | jq -R . | jq -s -c 'map(select(length > 0))')" || return 1
plugins/push-notification/scripts/push-notification:373:  if ! response="$(printf '%s' "${payload}" | curl "${curl_args[@]}" --data-binary @- "${url}" 2>&1)"; then
plugins/review-pr-with-codex/scripts/codex-aspects:77:    for group in ${RUNNING_GROUPS[@]+"${RUNNING_GROUPS[@]}"}; do
plugins/review-pr-with-codex/scripts/codex-aspects:89:  for pid in ${RUNNING_PIDS[@]+"${RUNNING_PIDS[@]}"}; do
plugins/review-pr-with-codex/scripts/codex-aspects:219:  for known in "${KNOWN_ASPECTS[@]}"; do
plugins/review-pr-with-codex/scripts/codex-aspects:506:    for gitlink_path in ${uninitialized_gitlinks[@]+"${uninitialized_gitlinks[@]}"}; do
plugins/review-pr-with-codex/scripts/codex-aspects:584:    for name in AGENTS.override.md AGENTS.md ${GUIDE_NAMES[@]+"${GUIDE_NAMES[@]}"} CLAUDE.md; do
plugins/review-pr-with-codex/scripts/codex-aspects:633:  for aspect in "${KNOWN_ASPECTS[@]}"; do
plugins/review-pr-with-codex/scripts/codex-aspects:734:    for angle in "${angles[@]}"; do
plugins/review-pr-with-codex/scripts/codex-aspects:742:  expected="$(printf '%s\n' "${angles[@]}" | jq -Rs 'split("\n") | map(select(length > 0)) | sort')" || return 1
plugins/review-pr-with-codex/scripts/codex-aspects:758:  for angle in "${angles[@]}"; do
plugins/review-pr-with-codex/scripts/codex-aspects:770:  jq -s '.' "${files[@]}"
plugins/review-pr-with-codex/scripts/codex-aspects:794:  [[ ${#reviews[@]} -gt 0 ]] || die "simplify requires at least one review aspect; use all simplify"
plugins/review-pr-with-codex/scripts/codex-aspects:795:  printf '%s\n' "${reviews[@]}" | jq -Rs --argjson all "${all}" --argjson simplify "${simplify}" \
plugins/review-pr-with-codex/scripts/codex-aspects:824:  [[ -s "${statuses}" && ${#aspects[@]} -gt 0 ]] || die "--statuses and selected --aspect names are required"
plugins/review-pr-with-codex/scripts/codex-aspects:831:  expected="$(printf '%s\n' "${aspects[@]}" | jq -Rs 'split("\n") | map(select(length > 0)) | sort')"
plugins/review-pr-with-codex/scripts/codex-aspects:872:  gate="$(cmd_gate ${args[@]+"${args[@]}"})" || die "could not validate the final review"
plugins/review-pr-with-codex/scripts/codex-aspects:1026:  [[ ${#aspects[@]} -gt 0 ]] || die "--aspect is required"
plugins/review-pr-with-codex/scripts/codex-aspects:1030:  for aspect in "${aspects[@]}"; do
plugins/review-pr-with-codex/scripts/codex-aspects:1041:  if [[ "${seen}" == *" simplify "* && ${#aspects[@]} -gt 1 ]]; then
plugins/review-pr-with-codex/scripts/codex-aspects:1050:    for ((index = 0; index < ${#gate_args[@]}; index += 2)); do
plugins/review-pr-with-codex/scripts/codex-aspects:1057:    [[ ${#gate_inputs[@]} -eq 6 && ${#reviewed_aspects[@]} -gt 0 ]] \
plugins/review-pr-with-codex/scripts/codex-aspects:1059:    gate="$(cmd_gate "${gate_inputs[@]}" --after "${scope}" "${reviewed_aspects[@]}")" \
plugins/review-pr-with-codex/scripts/codex-aspects:1063:  elif [[ ${#gate_args[@]} -gt 0 ]]; then
plugins/review-pr-with-codex/scripts/codex-aspects:1100:  for aspect in "${aspects[@]}"; do
plugins/review-pr-with-codex/scripts/codex-aspects:1126:    current="$(cd "${top_level}" && "${SCRIPT_DIR}/review-scope" ${base_args[@]+"${base_args[@]}"})" \
plugins/review-pr-with-codex/scripts/codex-aspects:1134:  for index in "${!aspects[@]}"; do
plugins/review-pr-with-codex/scripts/codex-aspects:1159:      ${extra_args[@]+"${extra_args[@]}"} \
plugins/review-pr-with-codex/scripts/codex-aspects:1172:  for index in "${!aspects[@]}"; do
plugins/review-pr-with-codex/scripts/codex-aspects:1182:  combined="$(printf '%s\n' "${statuses[@]}" | jq -s '.')"
plugins/review-pr-with-codex/scripts/codex-aspects:1198:  review_git -C "${repo}" diff-tree "${REVIEW_DIFF_OPTIONS[@]}" -r -z --name-only "${before_tree}" "${after_tree}" > "${raw}" \
plugins/review-pr-with-codex/scripts/review-git.bash:8:  git "${REVIEW_GIT_OPTIONS[@]}" "$@"
plugins/review-pr-with-codex/scripts/review-git.bash:12:  review_git diff "${REVIEW_DIFF_OPTIONS[@]}" "$@"
plugins/review-pr-with-codex/scripts/review-git.bash:16:  printf '%q ' "${REVIEW_GIT_OPTIONS[@]}" diff "${REVIEW_DIFF_OPTIONS[@]}"
plugins/review-pr-with-codex/scripts/review-git.bash:110:  review_git -C "${repo}" diff "${REVIEW_DIFF_OPTIONS[@]}" --raw -z --no-abbrev "$@" > "${raw}" \
plugins/review-until-clean/scripts/review-git.bash:8:  git "${REVIEW_GIT_OPTIONS[@]}" "$@"
plugins/review-until-clean/scripts/review-git.bash:12:  review_git diff "${REVIEW_DIFF_OPTIONS[@]}" "$@"
plugins/review-until-clean/scripts/review-git.bash:16:  printf '%q ' "${REVIEW_GIT_OPTIONS[@]}" diff "${REVIEW_DIFF_OPTIONS[@]}"
plugins/review-until-clean/scripts/review-git.bash:110:  review_git -C "${repo}" diff "${REVIEW_DIFF_OPTIONS[@]}" --raw -z --no-abbrev "$@" > "${raw}" \
plugins/workmux/scripts/launch-workmux:212:  for dir in "${dirs[@]}"; do
plugins/workmux/scripts/launch-workmux:359:  if ((${#env_args[@]} > 0)); then
plugins/workmux/scripts/launch-workmux:360:    env "${env_args[@]}" "${command[@]}"
plugins/workmux/scripts/launch-workmux:362:    "${command[@]}"
plugins/workmux/scripts/launch-workmux:407:    for number in "${issues[@]}"; do
plugins/workmux/scripts/launch-workmux:423:    printf '  %s\n' "${candidates[@]}" >&2
plugins/workmux/scripts/launch-workmux:689:  { run_detached_launch "${state_dir}" "${prompt_file}" "${cmd[@]}" < /dev/null > /dev/null 2>&1 & } 2> /dev/null
plugins/workmux/scripts/launch-workmux:704:    for ((index = 0; index < ${#branches[@]}; index++)); do
plugins/workmux/scripts/launch-workmux:827:    if [[ -n "${issue}${base_branch}${config_file}${agent}" || "${generated_mode}" == true || "${await_completion}" == true || ${#positional[@]} -gt 0 ]]; then
plugins/workmux/scripts/launch-workmux:848:    if [[ ${#positional[@]} -ne 0 ]]; then
plugins/workmux/scripts/launch-workmux:850:      die "--generated-name takes no branch-name argument, got ${#positional[@]}"
plugins/workmux/scripts/launch-workmux:863:  if [[ ${#positional[@]} -ne 1 ]]; then
plugins/workmux/scripts/launch-workmux:865:    die "expected 1 argument (branch-name), got ${#positional[@]}"
plugins/workmux/scripts/manage-resource-claims:269:  if [[ "${#keys[@]}" -eq 0 ]]; then
plugins/workmux/scripts/manage-resource-claims:276:            | {path: $a[.], branch: $a[. + 1], gitdir: $a[. + 2]}]' --args "${keys[@]}"
tests/fixtures/check-owner-call-contract:12:  ((${#files[@]} > 0)) || return 1
tests/fixtures/check-owner-call-contract:28:  ' "${files[@]}"
tests/fixtures/codex-stub:148:      printf '%s\n' "${recorded[@]}"
tests/fixtures/copilot-ancestry-case:112:    bash "${helper}" ${helper_args[@]+"${helper_args[@]}"} verify-fix o r 7 "${head}" "${fix}" || :
tests/fixtures/ntfy-curl-stub:45:      printf 'arg: %s\n' "${args[@]}"
```
