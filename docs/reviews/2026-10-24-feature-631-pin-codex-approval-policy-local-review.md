# Local review ledger: feature/631-pin-codex-approval-policy

Issue #631. Base `7846aee7`. Local review order: structural reviews, `review-pr-with-codex`, trims, semgrep, `lint-and-fix --no-push`. Copilot does not review this branch. Commit hashes below name the branch's commits before the tidy step.

## Before review: planted defects

Planting against the first version of rule 23 found that a failed `grep` or `awk` inside its process substitutions passed as a clean scan, and that a multi-line run and a run with another policy were uncovered. Fixed in `bd41adc9` before the first review round.

## Step 1, round 1 (Nit): `review-anti-patterns` and `/simplify`, report only

Reviewed head: `bd41adc9`.

- **`review-anti-patterns`:** installed 1.1.1 through Codex, with `--config 'approval_policy="never"'` added by hand, as this branch's reference now requires. Model `gpt-6.1-sol`, effort `high`, window `872000`, read-only sandbox, output schema `result-schema.json`. Completion checks: exit 0, non-empty reply, one JSON value, schema check passed. Result: `success`, `complete: true`, 2 Important. Unverified: `make validate`, scrut, Markdown lint and planted defects (no `--run-checks`; this session ran them), the live sandbox check, and a GitHub metadata lookup the sandbox could not reach.
- **`/simplify`:** read-only general-purpose subagent, Opus at `high`, report only. One bug, reported as outside its scope, and four quality findings.

| #   | Finding                                                                                                                                                           | Reviewer label             | Our severity                                                                     | Decision                                                                                                                                                                                        |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Sibling input forms: rule 23's start pattern takes `if` or `!` but not both, so an unpinned `if ! codex exec` passes, and the escaped-setting case tested nothing | important (both reviewers) | Important: an unpinned run of that form would pass the merge gate                | Fixed: any sequence of `if` and `!`. The failing scenario's last run starts with `if !`; restoring a single prefix fails the case                                                               |
| 2   | Validator gaps: the setting's text anywhere in a run satisfies rule 23, including inside a prompt                                                                 | important                  | Important: a run with the text only in its prompt would pass without the setting | Fixed: only a `--config` or `-c` argument counts. The failing scenario has a run with the text only in its prompt; accepting any text fails the case                                            |
| 3   | Track a pinned flag instead of joining the run's lines                                                                                                            | Nit                        | Nit                                                                              | Fixed                                                                                                                                                                                           |
| 4   | The end-of-run check is written twice                                                                                                                             | Nit                        | Nit                                                                              | Fixed: one `pending` rule handles every line of a run, and a fence always ends a run                                                                                                            |
| 5   | The rationale is repeated in about ten places                                                                                                                     | Nit                        | Nit                                                                              | Partly fixed: the READMEs keep one short sentence each, and the rule comment points to the docs section. The two invocation references and the docs keep the full reason; step 3 trims the rest |
| 6   | Two comment blocks for one rule, and the docs restate the definition of a run                                                                                     | Nit                        | Nit                                                                              | Fixed: the definition lives in `docs/plugin-development.md`; the rule comment links to it                                                                                                       |

Fixes committed as `2be7bb31`. Round 1 took Important findings and the fixes change behavior, so step 1 runs an Important round.

## Scope widened: web search off

Relayed by the conductor (Chris, Inbox, 2026-10-24): every scripted run also passes `web_search="disabled"`, rule 23 requires both settings, and the READMEs say both keep a run offline. Codex 0.163.0 names the setting `web_search`, with values `live`, `indexed`, `cached` and `disabled`, accepts the override and rejects an unknown value at configuration load (`codex -c 'web_search="bogus"' features list` fails). Committed as `204661cc`; the next review round covers it.

## Planted defects

Each plant was applied to the committed tree, checked, and reverted. "Validate" is `bin/validate-plugins` on the real tree.

| #   | Planted defect                                                           | Expected to catch it             | What happened                                                                           | Covered now by                                                |
| --- | ------------------------------------------------------------------------ | -------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 1   | Approval setting dropped from the shared `codex-exec.md` source, rebuilt | Validate                         | Rule 23 failed the source and both copies                                               | Validate (merge gate)                                         |
| 2   | Approval setting dropped from `codex-aspects`                            | `codex-aspects.md`, validate     | 3 `codex-aspects.md` cases failed; validate failed                                      | `codex-aspects.md`, validate                                  |
| 3   | Rule 23 never reports                                                    | `validate-plugins-codex-exec.md` | Failing scenario failed                                                                 | `validate-plugins-codex-exec.md`                              |
| 4   | A run does not end at its first line without a backslash                 | Same                             | First version: survived, since only one-line runs were planted. Now fails               | Same                                                          |
| 5   | Prose outside a fence counts as a run                                    | Same                             | Passing scenario failed                                                                 | Same                                                          |
| 6   | Any `approval_policy` value accepted                                     | Same                             | First version: survived. Now fails, through the `on-request` run                        | Same                                                          |
| 7   | The scan's `awk` program fails                                           | Validate                         | First version: validate passed, the failure unseen. Now validate fails, naming the rule | Validate, `validate-plugins-codex-exec.md`                    |
| 8   | The `grep` search fails                                                  | Validate                         | Validate fails, naming the rule                                                         | Same                                                          |
| 9   | The start pattern takes one prefix, as before round 1                    | `validate-plugins-codex-exec.md` | Failing scenario failed through its `if !` run                                          | Same                                                          |
| 10  | The setting's text anywhere in a run counts, as before round 1           | Same                             | Failing scenario failed through its prompt-only run                                     | Same                                                          |
| 11  | Escaped quotes not accepted                                              | Same                             | Passing scenario failed                                                                 | Same                                                          |
| 12  | A closing fence does not end a run                                       | Same                             | Survived                                                                                | Nothing: needs a backslash-continued line just before a fence |
| 13  | Rule 23 ignores `web_search`                                             | Same                             | Failing scenario failed                                                                 | Same                                                          |
| 14  | Web search setting dropped from `codex-aspects`                          | `codex-aspects.md`, validate     | 3 `codex-aspects.md` cases failed; validate failed                                      | `codex-aspects.md`, validate                                  |
| 15  | Web search setting dropped from the shared source, rebuilt               | Validate                         | Rule 23 failed the source and both copies                                               | Validate                                                      |
| 16  | `simplify`'s network setting dropped from `codex-aspects`                | `codex-aspects.md`               | The `simplify` case failed                                                              | `codex-aspects.md`                                            |

## Step 1, round 2 (Important): `review-anti-patterns` and `/simplify`, report only

Reviewed head: `0fa08fcc`. Same reviewers and settings, with `--severity important` for Codex, and `web_search="disabled"` added to its run.

- **`review-anti-patterns`:** Codex completion checks passed. Result: `success`, `complete: true`, 2 Important.
- **`/simplify`:** one borderline finding; rule 23's structure and the tests judged proportionate.

| #   | Finding                                                                                                                                                                                 | Reviewer label       | Our severity                                                                                                                                                                            | Decision                                                                                                                                                                                                                                              |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Sibling input forms: flag-shaped text inside a quoted prompt, such as `"Review --config 'approval_policy=\"never\"' ..."`, still satisfies rule 23, as can a trailing comment           | important            | Nit: rule 23 guards against a maintainer omitting the settings, and this needs the flags written into a prompt while the real ones are missing. Another instance of round 1's finding 2 | Stopped the loop for a design decision                                                                                                                                                                                                                |
| 2   | Unenforced trust boundary: `simplify` runs under `workspace-write` and inherits the user's `sandbox_workspace_write.network_access`, so the docs' offline claim fails when that is true | important            | Important: the change claims every run offline, `simplify` included                                                                                                                     | Fixed after the stop, with the conductor's go-ahead: `codex-aspects` passes `sandbox_workspace_write.network_access=false` on the `simplify` run, which Codex 0.163.0 accepts while rejecting an invalid value. Dropping it fails the `simplify` case |
| 3   | The review-anti-patterns README's new sentence separates "Otherwise nothing but its instructions does" from the sentence it refers to                                                   | borderline important | Nit: ambiguous wording, the right action still follows                                                                                                                                  | Fixed after the stop, with the conductor's go-ahead: the offline sentence follows the one about instructions                                                                                                                                          |

Step 1 ends **stopped: recurring defect**. Chris chose to record finding 1 as a limitation (option A): `docs/plugin-development.md` says rule 23 reads lines, not shell words, so flag-shaped text in a quoted prompt or a trailing comment can satisfy it. The alternatives were accepting only each setting on its own continuation line, and shell-aware parsing.

## Step 2, round 1 (Nit): `review-pr-with-codex`

Reviewed snapshot `6ec39e5f` at head `b34c230f`. Installed `review-pr-with-codex` 2.1.0 through `codex exec` (codex-cli 0.163.0), `gpt-6.1-sol` at `xhigh`, window `872000`, guide name `CLAUDE.md`. That release predates this fix, so a wrapper first on `PATH`, in the session's scratch directory, added `approval_policy="never"` and `web_search="disabled"` to each `codex exec` it started; no setting changed. Aspects `code`, `errors`, `tests` and `comments` ran in parallel and all succeeded. `types` was skipped: no type, schema or data-structure definitions changed. `simplify` was not selected. The tree check found no lasting changes and the snapshot was unchanged. `code` found nothing to report.

| #   | Finding                                                                                                                                         | Reviewer label | Our severity                                                          | Decision                                                                                                                                            |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Under bash 3.2 a here-string needs a temporary file; when that fails, rule 23's loop is skipped and validation passes without scanning (errors) | important      | Nit: needs a failed temporary file, and older rules share the pattern | Fixed as a trivial local change: both loops read through process substitution. Not planted: a failed temporary file cannot be staged in the fixture |
| 2   | No case covers rule 23's search and scan failure guards (tests)                                                                                 | important      | Important: a missing test for the change's own behavior               | Fixed: wrappers make the rule's own `grep` or `awk` call exit 2; plants 17 and 18 show each case fails without its guard                            |
| 3   | "Offline" overstates the guarantee: MCP servers in the user's configuration still reach the network (comments)                                  | important      | Important: the docs promise more than the settings give               | Fixed: the docs say the settings keep a run's commands and web search offline, and name MCP servers as not covered                                  |
| 4   | The general recipe in `docs/plugin-development.md` omits the `workspace-write` network override (comments)                                      | important      | Important: a helper following it could leave a writable run online    | Fixed: a `workspace-write` run also passes `sandbox_workspace_write.network_access=false`, which rule 23 does not check                             |

Round 1 took Important findings and fix 1 changes behavior, so step 2 runs an Important round.

## Step 2, round 2 (Important): `review-pr-with-codex`

Reviewed snapshot `120e745b` at head `1cbbe6dc`. Same entry point, wrapper, model, effort, window, guide name and aspects as round 1; all four succeeded. The tree check found no lasting changes and the snapshot was unchanged. `code`, `errors` and `tests` found nothing to report.

| #   | Finding                                                                                                | Reviewer label | Our severity | Decision                                                                           |
| --- | ------------------------------------------------------------------------------------------------------ | -------------- | ------------ | ---------------------------------------------------------------------------------- |
| 1   | The plan says text in a prompt cannot satisfy rule 23, which holds only for a plain mention (comments) | suggestion     | Nit          | Fixed: the plan states the line-based limitation and Chris's decision to record it |

Step 2 ends **clean at Important**.

## Step 3: `trim-comments` and `trim-text` through Codex

Both ran as read-only Codex dry runs on `gpt-6.1-sol` at `low`, window `872000`, with both settings added, since the installed releases predate them. Completion checks passed: exit 0, a non-empty reply in the expected shape, and every file in scope listed.

- **`trim-comments`** (installed 2.1.0), default scope: `bin/validate-plugins`, `codex-aspects` and the fixture, plus four JSON manifests with no comments. Seven proposals. One was rejected: deleting the justification for a `shellcheck disable`, which the skill never touches. The rest were taken in this session's own wording, keeping the pointer to `docs/plugin-development.md`, the reason both statuses are checked and the meaning of grep's exit 1, which the proposals dropped. Committed as `5a0d965f`.
- **`trim-text`** (installed 1.1.0), the 11 Markdown files the branch changed, limited to the units it added or changed. Thirteen proposals. The four README rewrites were adjusted to keep that the sandbox holds only with the approval setting, which the brief requires. The plan keeps the issue's request and Chris's decision. Committed as `48875476`.

## Step 4: semgrep

One baseline scan of head `48875476` in a disposable `git clone --shared`: semgrep 1.180.0, `semgrep scan --config auto --baseline-commit 7846aee7` with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`. It ran 131 rules on 19 files changed since the base; 17 more fell under its ignore patterns. Result: 0 findings, so it skipped the baseline comparison. It parsed about 69% of lines.

## Step 5: `lint-and-fix --no-push`

Installed `lint-and-fix` 1.4.3, following the repository's documented commands: `make format` as the fixer, then `make lint` (markdownlint, Prettier, shellcheck, shfmt, actionlint), `make validate` and the CI drift check of the generated mirrors. The agent config forbids no fixer. Nothing needed fixing, every check passed, and no commit was made.

## Tests

`make test-all` on head `31ca3262`: lint and validation passed, and 29 of 30 scrut documents passed, `validate-plugins-codex-exec.md` (4 cases) and `codex-aspects.md` (78) among them. `launch-workmux.md`, which this branch does not touch, failed four cases under the parallel run, as it did with `notification-tiers.md` in an earlier full run; each passed every case when run alone (62 and 23). Its cases wait a fixed three seconds for the launcher, which a loaded machine can exceed.

## Step 6: tidy

The branch was backed up as `feature/631-pin-codex-approval-policy-pre-tidy` and rebuilt from `7846aee7` as four signed commits: the fix to the skills and helper, validator rule 23, the tests, and these records. `git diff --quiet` against the backup confirmed the same tree.
