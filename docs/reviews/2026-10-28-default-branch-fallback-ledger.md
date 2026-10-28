# Default branch fallback review ledger

## Status

Local work verified. The focused review loop ended clean at Critical.
Publication, CI and exact-tree tidy proof are recorded in the worker checkpoint
and TOOLING handoff. TOOLING retains the merge step.

## Authority and scope

Worker: `565-default-branch-fallback`, reporting to TOOLING. Chris's go-ahead:
Inbox, 2026-10-28 at 9:16 AM ET, "Tooling next batch", build through a PR ready
for review. TOOLING merges; the worker never merges.

Issue: [Default-branch fallback resolves to HEAD](https://github.com/cboone/agent-harness-plugins/issues/565).
Base: `main`; comparisons use the actual merge base with `origin/main`.
Full local review order applies because executable helper behavior changed.

## Implementation and sweep

- Reproduction in `/tmp/565-default-branch.Z3Dinb`: origin configured, no remote
  HEAD. Old pipeline printed `HEAD`, status 0. `symbolic-ref` printed nothing,
  status 1.
- Updated the two issue locations, five `remote show | grep | sed` fallbacks,
  `wtaf`'s variable-remote query and guessed names, both shared review helpers,
  and the review/trim instructions that could accept a stale local base.
- Helpers retain their existing partial-coverage JSON contract when no base is
  known. Consumers must ask for an explicit base before claiming full coverage.
- Historical review reports and completed plans remain evidence of past runs.
  Other `rev-parse` pipelines concern upstream reporting or commit metadata,
  not default-base success. GitHub-only queries have no local fallback to fix.
- Each changed plugin receives one patch bump; generated files come from
  `make build`.

## Validation

- `corepack yarn install --immutable`: passed.
- `make build`: passed.
- Skill fallback contract: seven commands executed without pipefail, passed.
- Helper tests: 48/48 passed after the fatal-validation regression was added. Restoring the swallowed-error behavior failed exactly that regression (47 passed, 1 failed); restoring the fix passed 48/48 again. Skill contract: 2/2 passed, covering seven missing-ref and seven nonstandard-default lookups.

## Planted defects

| Planted defect                            | Instrument                       | Observed result                                        | Regression coverage                                        |
| ----------------------------------------- | -------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------- |
| Restore old pipeline in review-branch     | Skill fallback contract          | Failed: invalid review-branch fallback; restore passed | `default-branch-fallback.md`                               |
| Restore shared helper's old base resolver | Helper scope tests               | Failed: 2 coverage/base assertions; restore 47/47      | `review-scope.md`                                          |
| Swallow unexpected validation status 128  | Injected-error helper regression | Failed: 47 passed, 1 failed; restore 48/48             | `review-scope.md` unexpected inferred-base validation case |

## Review rounds

- Structural Nit round: fresh read-only Codex CLI runs, `gpt-6.1-sol`, `high`, window `872000`. Both exited 0 with nonempty, valid JSON. Simplify: no findings. Anti-patterns: one Nit, `Docs drift: fallback descriptions still name remote show`. Our severity: Nit, stale fallback descriptions; take the README and error-handling updates, plus matching workmux recommended command examples. Docs only; ended: fixes changed no behavior. No lasting tree changes from review.
- Reviewer did not run tests/network; worker separately verified ownership, test execution and both plants. Its workmux help read could not initialize a log in the read-only sandbox; no workmux options changed here.
- Focused Nit round: installed `codex-aspects` helper, standalone read-only `gpt-6.1-sol`, `high`, window `872000`, parallel code/errors/tests/comments. All four exited 0 and passed schema/snapshot checks. No lasting changes (`scope_changed: false`). Types skipped because no types changed; simplify already ran report-only in structural review.
- Comments reviewer label `important`: `write-markdown: Commands and output: Base validation precedes the fetch that can establish it.` Our severity: Important, supported newly created remote bases can be rejected. Take: validate after successful fetch in both sync paths and preserve explicit bases. Review again: yes, agent behavior changes.
- Comments reviewer label `important`: `write-markdown: Commands and output: Remote-ref validation excludes documented alternative base sources.` Our severity: Important, supported local and pinned-commit comparisons can be rejected. Take: validate resolved `base_ref` for the selected source. Review again: yes, agent behavior changes.
- Sibling check: workmux default detection now explicitly exempts a user-supplied base and passes the verified remote-tracking ref for an automatic base, avoiding later selection of stale local names. This preserves explicit local overrides.
- Focused Important round 1: all four aspects completed successfully, same settings. Prior instruction findings did not recur. Errors label `important`: `write-bash-scripts: Checked commands: Unexpected base-validation failures become ordinary missing bases.` Our severity: Important, Git object-read failures can produce misleading successful partial-coverage JSON. Take: distinguish expected missing-ref status 1 from unexpected validation failures, preserve diagnostic and exit status in both helpers. Review again: yes, executable behavior changes. This is an error-propagation defect, distinct from the prior instruction-ordering and supported-source defects.
- Focused Important round 2: all four aspects exited 0 and passed helper validation. Before/after snapshot `fbc847403b8b9e0ee6eae8b478cfc90a606e4298` is recorded in the attached JSON evidence; `scope_changed: false`, no lasting changes. Code/tests/comments found none. Errors label `important`: `write-bash-scripts: Checked commands: Missing base objects are treated as absent refs.` Our severity: Important, an existing base with an unavailable commit object can still yield successful partial-coverage JSON because Git returns status 1 for this case too. Take or record: record at the required recurrence stop, do not apply another incremental fix. Review again: blocked pending TOOLING's structural decision. End state: stopped: recurring defect.
- Recurrence class: base-validation failures become ordinary missing-base success. The previous round fixed status 128; this round demonstrates the same class through status 1. Reviewer evidence and all aspect outputs are in [Important round 2](2026-10-28-default-branch-fallback-important-2.json).
- Suggested structural direction for TOOLING to assess: first distinguish an absent symbolic target from an existing ref, then require every existing target to validate as a commit. Add an actual missing-object fixture, not only an injected status 128. This is a proposal, not implemented work.
- Validity note: the Important round 1 after-snapshot was captured after authorized fixes, so it measured those known six-path edits rather than an unchanged review tree. Its findings were taken, not reported clean. The complete Important round 2 re-reviewed the final tree and its before/after snapshot held.
- Comment and prose trims: completed after the Critical-only round; see resumed trim record.
- Semgrep baseline-aware scan: passed; see final validation record.
- Final lint, test-all and versions: passed; exact-tree tidy protocol and proof destination are below.

## Recurrence design call and resumed work

TOOLING authorized the structural fix in the worker conversation: distinguish
only absent refs or symbolic targets as not found; return found with a verified
commit; propagate all other errors with status and diagnostic. One resolver
owns initial and closing checks in both byte-identical helper distributions.
Callers no longer repeat commit validation or absorb failures with `|| true`.
Not-found and found are explicit JSON outcomes; errors retain nonzero Git status.

Dedicated outcome tests cover absent targets, valid inferred/explicit/object
bases, a real missing loose commit object with an independent valid HEAD,
unexpected existence-query failure, non-commit objects and the closing check.
All outcome plants and the Critical-only review are pending.

### Resumed outcome validation

`base-resolution.md`: 6/6 passed. Existing `review-scope.md`: 48/48 passed.
All six plants changed both helper copies together, preserving the copy-drift
control. Each failed its named boundary; restoration passed 6/6.

| Plant                                     | Intended boundary          | Observed result                                        | Durable coverage                                           |
| ----------------------------------------- | -------------------------- | ------------------------------------------------------ | ---------------------------------------------------------- |
| Return an error for an absent target      | Not found                  | 5 passed, 1 failed; absent-target case                 | `base-resolution.md` absent symbolic target                |
| Return an invalid found commit            | Found with verified commit | 4 passed, 2 failed; valid-ref case and closing case    | `base-resolution.md` inferred, explicit and object callers |
| Convert existence status 128 to not found | Real missing object        | 5 passed, 1 failed; real missing-object case           | `base-resolution.md` real loose-object fixture             |
| Convert existence status 73 to not found  | Unexpected error           | 4 passed, 2 failed; unexpected-query and closing cases | `base-resolution.md` committed Git function stub           |
| Add `--quiet` to commit verification      | Commit diagnostic          | 5 passed, 1 failed; non-commit-object case             | `base-resolution.md` ref to a blob                         |
| Ignore the closing resolver failure       | Closing caller             | 5 passed, 1 failed; closing case                       | `base-resolution.md` closing lookup failure                |

Next focused round is Critical-only, with counts preserved: one Nit and two
Important rounds have run. A further instance of the recurrence class stops
again regardless of that round's reporting threshold.

### Critical-only round 1

Installed helper, same Sol/high/872000 read-only settings. All four aspects
completed with valid results. Snapshot `03f5d7823dfda096a46762e380674efe11c5f14a`
held; no lasting changes. No Critical finding.

- Code reviewer label `important`: `write-bash-scripts: Checked commands: Valid fully qualified base expressions are rejected.` Errors independently reported `write-bash-scripts: Checked commands: Valid qualified revisions are reported as missing bases.` Our severity: Important, supported explicit revision expressions were rejected. This is a sibling-input classification regression, distinct from turning Git object failures into successful partial coverage; no further instance of the error-propagation class was found. Take: trivial local fix tracks whether Git returned a symbolic name instead of inferring that from the input prefix, with qualified expression cases in the existing valid-outcome test. No design change or severity downgrade.
- Comments reviewer label `suggestion`: `write-markdown: Commands and output: Invalid base refs do not always produce partial-coverage JSON.` Our severity: Nit, documentation for this branch's changed error boundary. Take: distinguish absent targets from invalid objects and Git errors.
- Review again: no. Under the threshold advancement rule, no Critical finding was taken, so this loop ends rather than opening another round for a below-threshold local fix. Counts remain one Nit, two Important, one Critical-only. End state: clean at Critical.

### Trims and qualified-expression plant

The qualified-expression regression passed 6/6. Replanting prefix-based ref
classification failed the valid-ref case (5 passed, 1 failed); restore passed
6/6. The final helper source passed ShellCheck and shfmt checks.

One read-only Codex round per trim skill: `gpt-6.1-sol`, `low`, window `872000`.
Both processes exited 0 with nonempty output and progressed beyond stdin.
Comment output met its shape, classified both canonical helpers and proposed
no changes. Text output classified the eligible files and gave full before/after
rows, but included extra commentary outside its strict output shape. Recorded
as a shape failure, not a clean automated trim. The skill's inline fallback
classified the changed prose, preserved quoted evidence, fences and constraints,
and shortened three units: the two sync fallback introductions and the
partial-coverage explanation. No code or requirement changed. No lasting
changes were found before applying the accepted inline edits.

## Final validation and publication preparation

- Semgrep 1.180.0: `scan --config auto --baseline-commit 84b350efe84c04abedaf3aadbf0b7f96dde520ee`, with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, in disposable shared clone `/tmp/565-semgrep.HnyKqg/repo`. No metrics-off flag. Exit 0, 131 rules, 29 targets, 0 findings, JSON `errors: []`. The baseline-aware scan limited its targets to changed files; Semgrep skipped the baseline checkout because the current scan had no findings.
- `lint-and-fix --no-push`: success, no formatting fixes or commit needed. Scoped Prettier and shfmt write passes found no changes. Markdownlint ran check-only because supplied project instructions prohibit reformatting Scrut documents; the other checks ran through the project commands. No required lint work was skipped.
- `make test-all`: exit 0. Markdownlint, Prettier, ShellCheck, shfmt, actionlint, JSON and plugin validation passed; all 37 Scrut documents passed. The final result was observed, not inferred from a partial log.
- Repository `check-versions`: clean against actual `origin/main` merge base `84b350efe84c04abedaf3aadbf0b7f96dde520ee`. All 60 catalog entries and manifests match, Codex manifests match where present, and version ownership remains manifest-only. All ten changed plugins have one patch increment.
- PR body drafted and trimmed inline under `pr-and-issue-bodies`; no scope conditions or closing references removed. Ready PR targets `cboone/agent-harness-plugins`, base `main`, closing issue 565. No other repository or service is a publication destination.

### Version check report

| Plugin               | Base  | Branch | Status |
| -------------------- | ----- | ------ | ------ |
| review-anti-patterns | 1.1.3 | 1.1.4  | OK     |
| review-branch        | 1.2.7 | 1.2.8  | OK     |
| review-pr-with-codex | 2.1.3 | 2.1.4  | OK     |
| review-until-clean   | 3.1.3 | 3.1.4  | OK     |
| sync-with-main       | 1.0.0 | 1.0.1  | OK     |
| trim-comments        | 2.1.2 | 2.1.3  | OK     |
| trim-text            | 1.2.0 | 1.2.1  | OK     |
| use-git              | 1.3.3 | 1.3.4  | OK     |
| workmux              | 1.1.0 | 1.1.1  | OK     |
| wtaf                 | 2.0.1 | 2.0.2  | OK     |

### Tidy protocol

Back up the validated head as `fix/565-default-branch-fallback-pre-tidy`, soft
reset to the recorded merge base, and rebuild logical signed feature, test and
documentation commits. Require `git diff --quiet` against the backup before
pushing. The worker checkpoint and TOOLING handoff hold the resulting head,
exact-tree comparison result, PR URL and final CI result; no post-tidy source
edit is authorized by this protocol.

## Authorized base sync after publication

TOOLING authorized merging `origin/main` into the published branch with a merge
commit, preserving both sides and bumping conflicting plugin versions above
main. No rebase, amend or force push. Main at the merge is
`78386666cdce00aa7efd09eff6cc9252335f034d`, including Codex compatibility milestone
2 and the existing resource-claims race work.

Only version fields conflicted in canonical sources: `review-branch` main
`1.3.0` becomes `1.3.1`; `sync-with-main` main `1.1.0` becomes `1.1.1`.
`use-git` also becomes `1.3.5` above main's `1.3.4`, since both branches used the
same prior patch. Other plugin bumps remain forward. Both sides' other changes
merged automatically; fallback instructions and the new capability/continuation
sections are retained. Generated conflicts are resolved by `make build`.

The earlier exact-tree tidy proof covers the published pre-merge head. This
merge adds main's changes and the version reconciliation; pushed history stays
intact. Validation and CI completion for this sync are recorded in the worker
checkpoint and TOOLING handoff after the requested checks finish. Review counts
remain one Nit, two Important and one Critical-only; no new review loop starts.
