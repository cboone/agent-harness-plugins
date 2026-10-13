---
name: use-semgrep
description: >-
  Run a report-only Semgrep comparison of a branch against its merge base.
  Report new findings, scanner errors and coverage; keep evidence locally.
---

# Use Semgrep

Draft for iteration. This file is not installed or registered as a plugin.

Scan committed branch changes with the existing Semgrep login and configured policy. Run in a temporary clone, keep metrics off, and report findings separately from scan completeness.

## Boundaries

- Use `semgrep ci --dry-run --metrics off --no-suppress-errors`. Do not upload findings, apply fixes, install tools, or change policy, CI, hooks or schedules.
- Dry-run still authenticates and sends repository metadata to fetch configuration. It prevents findings submission, not all network traffic. Use existing authorization for that contact; obtain it if the scan has not been authorized.
- Let Semgrep resolve the existing login. Never inspect credential files, print tokens, or put secrets in command arguments.
- Use the working Semgrep installation already selected for the environment. A writable clone and temporary storage are required; authentication or engine access may also need permissions the sandbox lacks. Diagnose the actual restriction rather than assuming every sandbox is unsuitable.
- Stop on authentication, configuration, network or baseline failures. Do not fall back to a full scan, `--config auto`, another policy or another engine.
- Keep local evidence until reviewed. Raw JSON and logs may contain source snippets or sensitive matches; restrict file permissions and redact sensitive values from the report.

## 1. Bind the scope

From the repository root, check repository ownership and archived status under the applicable project rules. Determine the default branch and confirm its remote-tracking ref. Record:

- Repository name and URL, branch name, Semgrep version and executable.
- Branch `HEAD`, default-branch tip and their merge base.
- Whether the default-branch ref was refreshed or is only the last fetched state.
- Staged, unstaged and untracked changes. A clone at `HEAD` excludes them; report them as outside the scan.

Use the merge base for `--baseline-commit`. Semgrep compares findings against that commit internally; a separate full scan of the default branch is not required. A dashboard baseline upload is a separate action and is not part of this workflow.

If a default branch or merge base cannot be resolved, stop and name the missing reference. Do not substitute another comparison silently.

## 2. Prepare an isolated clone

Create a private temporary directory outside the real worktree. Clone the repository locally with `--shared`, check out the recorded head, and verify the baseline commit exists there. Keep the source checkout available while scanning: the shared clone borrows its Git objects.

The clone protects the real worktree from Semgrep's baseline checkout operations. It is not a sandbox for Semgrep or the fetched rules.

Set repository metadata explicitly. A local clone's `origin` points to a filesystem path, and checking out the head SHA detaches the branch. Use the actual repository name, URL and branch in `SEMGREP_REPO_NAME`, `SEMGREP_REPO_URL` and `SEMGREP_BRANCH`.

## 3. Run once and retain the exit code

The following Bash example assumes the executable, default-branch ref and repository metadata have been confirmed. Replace the example inputs before running it. Keep secrets out of these assignments.

```bash
set -euo pipefail
umask 077

semgrep_bin='/absolute/path/to/semgrep'
base_ref='origin/main'
repo_name='OWNER/REPO'
repo_url='https://github.com/OWNER/REPO'

branch=$(git branch --show-current)
test -n "${branch}" || { echo 'Supply branch metadata for detached HEAD' >&2; exit 1; }
head_sha=$(git rev-parse HEAD)
base_tip=$(git rev-parse "${base_ref}")
base_sha=$(git merge-base HEAD "${base_ref}")
repo_root=$(git rev-parse --show-toplevel)
temp_root=$(cd "${TMPDIR:-/tmp}" && pwd -P)
case "${temp_root}/" in
  "${repo_root}/"*) echo 'Temporary storage must be outside the worktree' >&2; exit 1 ;;
esac
scan_dir=$(mktemp -d "${temp_root}/semgrep-branch.XXXXXX")
printf 'Evidence: %s\n' "${scan_dir}"
printf 'head=%s\nbase_tip=%s\nbaseline=%s\nbranch=%s\n' \
  "${head_sha}" "${base_tip}" "${base_sha}" "${branch}" \
  > "${scan_dir}/scope.txt"

git clone -q --shared . "${scan_dir}/clone"
git -C "${scan_dir}/clone" checkout -q "${head_sha}"
git -C "${scan_dir}/clone" cat-file -e "${base_sha}^{commit}"

scan_exit=0
(
  cd "${scan_dir}/clone"
  SEMGREP_REPO_NAME="${repo_name}" \
    SEMGREP_REPO_URL="${repo_url}" \
    SEMGREP_BRANCH="${branch}" \
    "${semgrep_bin}" ci --dry-run --metrics off --no-suppress-errors \
    --json --json-output="${scan_dir}/semgrep.json" \
    --baseline-commit "${base_sha}"
) > "${scan_dir}/semgrep.log" 2>&1 || scan_exit=$?
printf '%s\n' "${scan_exit}" > "${scan_dir}/exit-code.txt"
printf 'Semgrep exit: %s\n' "${scan_exit}"
```

Do not append an `echo` inside the scan subshell and interpret its status as Semgrep's status. Give the scan enough execution time, or wait for its process to finish; do not rerun a scan merely because the shell tool yielded.

Record the enabled products, engine and rule counts from the actual run. Do not enable local builds, autofixes or additional products as a workaround. Supply Chain may inspect an unchanged lockfile to compare dependency findings.

## 4. Check findings and completeness separately

Validate that the JSON is readable and has `results`, `errors` and `paths.scanned` arrays before counting findings. Missing output or malformed JSON is a failed scan, not zero findings.

Interpret the exit code with the JSON and log. Exit 1 can indicate blocking findings rather than an execution failure. Exit 0 does not establish complete analysis, even with `--no-suppress-errors`.

Use these report statuses:

| Status     | Meaning                                                                                           |
| ---------- | ------------------------------------------------------------------------------------------------- |
| Complete   | The scan finished with usable output, no scanner errors, and coverage accounted for               |
| Incomplete | Usable output exists, but parser errors, timeouts or unexplained coverage gaps remain             |
| Failed     | The scan could not run or finish, or authentication, policy, baseline or output validation failed |

For each scanner error, report its type, affected path and span, and a concise message. Print only the message's first line or a redacted excerpt; errors can embed whole source files. Any nonempty `errors` list prevents a Complete result.

Compare changed files against `paths.scanned`. Account for generated mirrors, ignored or unsupported files, and files reached by generic rules. A path listed as scanned may still have a parser error; being listed does not establish full analysis. If skipped-path details are absent, say so rather than inventing exclusion reasons.

If no applicable targets or rules ran, report that explicitly instead of a clean security result.

Only call zero findings a clean comparison when the result is Complete. Qualify it by the configured policy, products and covered files. Semgrep does not establish that Markdown agent instructions behave correctly; keep semantic review separate.

## 5. Report and preserve evidence

Report:

- Status and number of new findings, even for an Incomplete result.
- Each finding's rule ID, path, line, severity and message, with sensitive values redacted.
- Head and baseline SHAs, default-branch freshness and excluded uncommitted work.
- Semgrep version, engine, products, rule counts and dependency coverage.
- Scanner errors and changed-file coverage, including omissions and unknown reasons.
- Exit code, metrics-off and dry-run settings, and paths to retained JSON, log and scope metadata.
- Whether the real worktree or head changed during the scan. A changed head means the result describes the recorded commit, not the latest branch.

Do not delete evidence automatically, fix findings, refresh dashboard baselines or file upstream reports. Those are separate tasks.

## Current evidence and next experiments

The first trial on issue #615 used Semgrep Pro 1.180.0 with Code and Supply Chain enabled. It reported zero new findings and exited 0, but emitted `PartialParsing` warnings spanning lines 3–509 in both canonical `review-scope` Bash scripts. The result was Incomplete. This observation motivates inspecting `errors` independently of exit status; it is not proof that every Bash script will fail.

Next, reproduce the warnings on the comparison commit and reduce the affected Bash syntax to a temporary example. Confirm Bash accepts that example, then check existing Semgrep reports or fixes. Avoid rewriting valid repository code solely to satisfy the scanner. Preserve the policy and engine while investigating; changing them would change the comparison.

The draft has not yet been exercised end to end as a reusable skill. Test its handling of blocking findings, missing output, authentication or baseline failures, parser warnings, and dirty worktrees before adding automation or packaging.

Reference: [Semgrep CLI options and exit codes](https://docs.semgrep.dev/cli-reference).
