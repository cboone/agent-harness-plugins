# Simplify parity verification ledger

## Authority and scope

Build through ready PR: Inbox Simplify plugin comparison, 2026-10-29 12:15 PM ET, relayed by CONDUCTOR. TOOLING merges. No installed plugins or user configuration changed. Base pinned to `1a42b4534ac873b070130b6be16ced1cbc8f687d`. Implementation and checks committed at `7dba92d8` before planting.

## Checks

Corepack yarn install --immutable passed. Initial focused Scrut: 93 existing cases and 16 cleanup cases passed. ShellCheck passed on the helper. Generated mirrors rebuilt with make build.

Prompt canaries verify delivery of cleanup requirements, not model compliance. Cost and mechanism use the existing finding detail field. The editor reports disposition and skip reasons there without changing the existing review schema. Cleanup results cannot substitute for correctness review.

## Plants

All eleven plants produced the expected failing case (make exit 2), with 15 other cleanup cases passing. Each plant changes canonical source, runs the cleanup Scrut document and restores the recorded original before the next plant. Scratch directory: `/tmp/simplify-parity.odHAIv`.

| Planted defect                     | Instrument                | Observed result           | Regression case               |
| ---------------------------------- | ------------------------- | ------------------------- | ----------------------------- |
| Cleanup gets write sandbox         | Cleanup Scrut             | Named case failed, exit 2 | Four cleanup reviewers        |
| Inline skips altitude              | Prompt canary             | Named case failed, exit 2 | Inline fallback               |
| Missing concrete cost              | Prompt canary             | Named case failed, exit 2 | Cleanup findings carry cost   |
| Missing mechanism deduplication    | Prompt canary             | Named case failed, exit 2 | Editor deduplicates           |
| Missing skipped-fix reporting      | Prompt canary             | Named case failed, exit 2 | Editor deduplicates           |
| Failed cleanup accepted            | Cleanup input validation  | Named case failed, exit 2 | Failed cleanup process        |
| Stale cleanup accepted             | Snapshot validation       | Named case failed, exit 2 | Stale cleanup snapshot        |
| Cleanup accepted as public review  | Selection boundary        | Named case failed, exit 2 | Cleanup cannot authorize      |
| Critical review accepted           | Correctness gate          | Named case failed, exit 2 | Critical correctness findings |
| Failed correctness review accepted | Correctness gate          | Named case failed, exit 2 | Failed correctness review     |
| Tree change accepted               | Immediate scope recapture | Named case failed, exit 2 | Changed tree                  |

## Local review

Full order required. All review bases are commit SHAs. Structural Nit round used gpt-6.1-sol, high effort and window 872000, in standalone read-only runs. The project explicitly requires this route for Codex workers, overriding the shared reference's Codex-host fallback preference.

### Structural round 1, Nit

Reviewed HEAD `2cd373c5fc0ad8df1f81e5b4f6893dac14b9a72a` against the pinned base. Both standalone processes exited 0 with non-empty, schema-shaped replies. Anti-patterns result-check passed, status success and complete true; report-only simplify completed every cleanup angle. Both used actual read-only sandboxes and left a clean tree.

| Reviewer label                                     | Our severity                                         | Take or record                                                           | Review again       |
| -------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------ | ------------------ |
| simplify suggestion: repeated four-angle roster    | Nit: maintenance requires reconciling repeated lists | Take: derive loops, expected statuses and filenames from one local array | No behavior change |
| anti-patterns nit: plant ledger rows still Pending | Nit: report contradicts measured summary             | Take: populate each observed result                                      | Docs only          |

Structural loop ended: fixes changed no behavior. No Important or Critical findings. Unrun reviewer checks are covered by the parent's separate tests, plants and required final checks; prompt canaries do not establish model compliance. Raw results: scratch `anti.json` and `simplify.json`.

### Focused round 1, Nit

Reviewed `e190bb25` against the pinned base. All five aspects (code, errors, tests, comments, types) exited 0, passed schema/snapshot validation and returned status ok. Snapshot `f40428d1b68fa64a0755eb0632aff72a80e1d523` remained valid; changes found no lasting edits. This also exercised the expanded schema in real Codex runs.

| Reviewer label                                                | Our severity                                                                                 | Take or record                                                                           | Review again                |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | --------------------------- |
| errors important: preserve cleanup rejection reasons          | Important: blocking failures hide which reviewer failed and prevent an actionable recovery   | Take: report status-file errors and angle/path/reason for invalid replies                | Yes: error behavior changes |
| tests important: missing roster and membership negative cases | Important: cleanup completion could be claimed for incomplete or differently scoped coverage | Take: missing/duplicate angle and different-membership cases, asserting no editor launch | Tests only                  |
| tests suggestion: non-empty finding delivery                  | Nit: missing evidence for the new editor handoff                                             | Take: compare complete non-empty payloads with both rendered and launched editor prompts | Tests only                  |

All fixes stay within the existing simplify contract. New cleanup suite passes 21 cases; ShellCheck passes. The initial make test-all attempt stopped at MD012 in the new test document; the extra blank line is removed. Next focused round is Important, with the same explicit model settings and pinned base. No downgrade, scope expansion or design call.

The first follow-up plants caught missing/duplicate roster checks, changed membership, stripped finding payloads and suppressed diagnostics. The roster plant also exposed shared test-state contamination after an expected failure. Each roster/membership testcase now uses a separate cleanup directory and edit sentinel; the original cleanup inputs remain intact for later cases. This changes test isolation only. Follow-up plants will be repeated against that committed test tree.

### Resume after pause

TOOLING relayed the Ramp goals go-ahead from the Inbox at 1:16 PM ET on 2026-10-29. Commit `0ae860d5` survived the interruption. Inspection found no remaining plant process and one recorded membership-check plant still applied. That exact change was restored, and the cleanup document passed all 21 cases. The earlier 20-of-21 result was a defect-plant run, not a clean-tree regression. The plan now records a primary-source community survey and why each source was used or set aside; no design or scope change follows.

### Follow-up plants after fixture isolation

All five plants ran against committed checks, returned make exit 2 and were restored individually. Only the intended cases failed; no cascade remained.

| Planted defect      | Instrument    | Observed result                                      | Regression cases                                                                                                                                                                                      |
| ------------------- | ------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| angle-roster        | Cleanup Scrut | 21 testcase(s): 19 succeeded, 2 failed and 0 skipped | Missing cleanup angle blocks launch with an actionable reason; Duplicated cleanup angle blocks launch with an actionable reason                                                                       |
| cleanup-membership  | Cleanup Scrut | 21 testcase(s): 20 succeeded, 1 failed and 0 skipped | Different cleanup membership blocks launch with an actionable reason                                                                                                                                  |
| finding-delivery    | Cleanup Scrut | 21 testcase(s): 19 succeeded, 2 failed and 0 skipped | Non-empty findings reach the rendered editor prompt unchanged; Non-empty findings also reach the standalone editor prompt unchanged                                                                   |
| reviewer-diagnostic | Cleanup Scrut | 21 testcase(s): 20 succeeded, 1 failed and 0 skipped | A stale cleanup snapshot blocks the editor prompt                                                                                                                                                     |
| status-diagnostic   | Cleanup Scrut | 21 testcase(s): 18 succeeded, 3 failed and 0 skipped | Missing cleanup angle blocks launch with an actionable reason; Duplicated cleanup angle blocks launch with an actionable reason; Different cleanup membership blocks launch with an actionable reason |

### Focused round 2, Important

Reviewed `1f58ce7d` against the pinned base, snapshot `d891d52ace0b3ebfb809fe9462727c5ee7a87e2b`. All five aspects exited 0 with validated status ok and no findings. The after-scope comparison reported scope_changed false and no lasting changes. Focused loop: clean at Important. Counts remain one Nit and one Important round; no confirmation review or Copilot round ran.

Both full-check attempts stopped in Markdown lint before the test suite, on extra blank lines in the new document. Those spacing errors are fixed; full make test-all remains required. Formatting failures do not consume review rounds.

### Trims and versions

One trim round ran through standalone read-only Codex, gpt-6.1-sol, low effort and window 872000. Both processes exited 0 with non-empty replies, complete file classifications and the required proposal shape. Comment trim proposed nothing. Text trim proposed two local wording edits: active voice for failed fan-out reporting and removal of the plan's Assessment prefix. Both were checked and taken without changing requirements. No further review round follows prose-only edits.

Check-versions verified main and the pinned merge base, the only changed plugin's forward minor bump `2.2.0` to `2.3.0`, all 60 marketplace registrations and manifest-only version ownership, including present Codex manifests. No version issues found.

### Semgrep baseline

Semgrep 1.180.0 ran in the disposable shared clone at scratch `semgrep-clone`, on HEAD `329b44d5`, with SEMGREP_REPO_NAME=cboone/agent-harness-plugins, config p/default, metrics off and --baseline-commit `1a42b4534ac873b070130b6be16ced1cbc8f687d`. Exit 0, 131 rules, 13 targets, zero findings. This was baseline mode limited to changed files; the scanner skipped the second baseline checkout because the current scan had no findings.

Coverage was partial: approximately 33.3 percent parsed lines. The only parsing diagnostic was Bash PartialParsing in `plugins/review-pr-with-codex/scripts/codex-aspects`, lines 3–1332. ShellCheck passed on that exact file after the scan. No non-shell parse errors occurred. The scanner reported 13 ignored paths; generated mirrors and the two Scrut documents were not in its scanned list. This follows the brief's explicit shell exception, not a claim of complete Semgrep coverage.

### Final lint procedure

Apply lint-and-fix with --no-push. Project commands cover Markdownlint, Prettier, ShellCheck, shfmt and actionlint. Protected Scrut snapshots are check-only by project policy; no formatter rewrites those files. Changed prose and shell were already formatted with the project's pinned tools. Run make lint and make validate to verify the final tree, committing any in-scope fixes without pushing. Full make test-all is still running and is not yet reported as passed.

### Final local result

The completed make test-all process exited 0: all 52 Scrut documents passed, covering 1823 cases (1823 succeeded, 0 failed, 0 skipped). Both affected documents passed, including all 21 cleanup cases and all 93 existing aspect cases. Final make lint and make validate also passed. No code changed after the successful focused review; the subsequent two prose trims preserve requirements. Generated mirrors were rebuilt from canonical sources.

Lint-and-fix --no-push result: no-op, no remaining lint fixes, no skipped required checks. Protected Scrut files were checked without reformatting. The only check-only policy is the existing snapshot preservation rule. No push occurred during lint. Fresh fetch still resolved origin/main to the pinned base; no integration merge is needed.

Local review end states: structural ended: fixes changed no behavior; focused clean at Important; one trim round completed. Sixteen unique plants were measured, including prompt-delivery canaries, with restored-tree passes. Semgrep's shell coverage exception remains as recorded above. No Important downgrade, recurring-defect stop or scope/design expansion occurred. Copilot was neither requested nor awaited.

Before publication, back up the unpushed branch and rebuild feature, tests and documentation as signed logical commits. The exact-tree comparison with that backup is mandatory; the publication handoff records its measured result. TOOLING owns merging. No installed plugins, user configuration or software installations were changed.
