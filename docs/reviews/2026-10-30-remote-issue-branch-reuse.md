# Remote issue branch reuse review

Base: `origin/main` at `5205fada80635f7d9dd4a1967c94a256e60a99cb`.
Scope: issue 415, cached origin lookup, local preference, tracking creation and regression coverage.

## Review rounds

Structural Nit round: fresh, read-only Codex anti-pattern and report-only simplify reviews in parallel, `gpt-6.1-sol`, high effort, 872000-token window. Both completed with exit 0 and nonempty validated results. The anti-pattern JSON passed its schema check; simplify completed all four cleanup angles inline. Generated mirrors were excluded.

| Reviewer label                                         | Our severity                                           | Take or record                                                         | Review again   |
| ------------------------------------------------------ | ------------------------------------------------------ | ---------------------------------------------------------------------- | -------------- |
| Anti-patterns: `nit`, local-only workflow descriptions | Nit: naming prose omitted cached origin reuse          | Taken: update create-worktree and start-issue together                 | No: prose only |
| Simplify: `suggestion`, standalone Git DWIM probe      | Nit: repeated Git-only probe adds no launcher coverage | Taken: retain the measured result in the plan and remove the test case | No: tests only |

Structural loop: ended: fixes changed no behavior. The post-review snapshot capture overlapped those accepted edits and refused mixed-state output. That capture is incomplete, not clean; the review artifacts identify the unchanged committed input `71a6a054`. No reviewer edits occurred. The subsequent correctness review covers all final canonical changes and checks an unchanged snapshot.

Correctness Nit round: code, errors, tests and comments ran through the installed `codex-aspects` helper, fresh read-only Codex processes with `gpt-6.1-sol`, high effort and 872000-token window. Types was omitted because no types changed. All four exited 0 with validated, nonempty results and no findings. Snapshot `9120deb86318148b51ef27f36f135d493491250a`, head `bd3e8272`; before/after comparison reports `scope_changed: false`, no lasting changes found. Runtime probes in the code aspect were blocked by the read-only sandbox; runtime evidence comes from the worker's checks below. Result: clean at Nit.

The initial correctness invocation refused a helper inside the repository before starting any aspect. The installed helper was used instead. Its final command printed a macOS `child setpgid` diagnostic; all four recorded subprocess exits and validations succeeded.

Comment and text trims completed in fresh read-only Codex runs with low effort and an 872000-token window. Three wording proposals were accepted: the ref fixture comment, README reuse sentence and ambiguity instruction. No behavior changed. Semgrep baseline returned zero findings but is incomplete: `PartialParsing` covers launcher lines 3 through 905. A diagnostic parse of the unchanged base launcher reproduces `PartialParsing` from lines 3 through 872. The project baseline-scan rule initially required a stop. TOOLING then relayed the standing shell-file exception dated October 28: record coverage and unparsed spans for both runs, and require ShellCheck to pass on the partly parsed shell file. ShellCheck passed on the launcher after that message, allowing lint to proceed. This remains partial Semgrep coverage, not a clean scan. No non-shell parser error was reported. Lint-and-fix completed with the known baseline fixture failure described below. The allocated full suite completed with only the known baseline failure; its lock was released. Tidy, push and PR creation follow.

## Planted defects

Plants ran one at a time in a recorded disposable shared clone, restoring the source between plants. The committed remote document passed 14/14 before plants and again after restoration. The final document has 13 cases after removing the standalone Git probe.

| Planted defect                                                | Instrument                          | Actual result                                                                             | Regression                                 |
| ------------------------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------ |
| Scan only local heads                                         | Stub and real-Git remote document   | 6 passed, 8 failed; real preflight omitted the name and launch chose the generated branch | Remote preflight and origin-history launch |
| Create branch without tracking                                | Stub and real-Git remote document   | 10 passed, 4 failed; real Git reported no upstream                                        | Upstream query after launch                |
| Ignore the existing local head                                | Real-Git remote document            | 13 passed, 1 failed; tracking creation refused the existing branch                        | Local commit and configuration retained    |
| Remove the real upstream assertion while tracking is disabled | Remote document with weakened judge | 11 passed, 3 failed; the exact-command stub still rejected the tracking invocation        | Strict tracking-command fixture            |

## Local validation

- Remote document: 13/13 passed on the final source, both normal Bash and native macOS Bash 3.2.
- Launcher document: initial 67/68 run observed a transient parse error because a script process read the file during an implementation edit; settled-tree rerun reported 66/68 because two no-tmux cases omitted the Git stub and ran outside a repository. Both now stub Git explicitly and verify resolution. These failures were test-isolation gaps, corrected without production edits; final rerun passed 68/68.
- ShellCheck: changed launcher and both stubs passed.
- Fixture environment validation: passed after adding the shared reset to the workmux stub's new Git consumer.
- Mirrors rebuilt with `make build`; no generated source edited by hand.
- Check-versions: workmux `1.1.5` to `1.1.6`, appropriate patch fix; generated manifest matches. All 60 plugins have matching catalog coverage, versions belong only to manifests, and optional Codex manifests match. Issue 424 also bumps workmux on its open branch; carry that coordination note into the PR.
- Semgrep artifacts retained at `/tmp/issue415-semgrep.cjzbML/result.json` and `baseline-parser.json`. The configured baseline-mode scan ran in its own shared clone at branch head `14324bed`; the separate base parse is diagnostic evidence, not a replacement baseline scan.
- Known baseline: `tests/fixtures/review-submodule-fixture` fails the review-path environment check and the corresponding environment-isolation assertion. Outside scope and unchanged.

## Semgrep coverage exception

Configured baseline-mode scan: 131 rules, eight targets, approximately 60.8 percent parsed lines, zero reported findings. Launcher unparsed span: line 3 column 1 through line 905 column 11. The unchanged base diagnostic parse has an unparsed span from line 3 column 1 through line 872 column 11. Both are Bash files. TOOLING relayed the standing exception in peer message `1051ac24-61e7-47d3-bd23-4de7338e837b`; ShellCheck on `plugins/workmux/scripts/launch-workmux` passed. No rule suppression or parser workaround was added.

## Lint and validation

`lint-and-fix --no-push` used scoped Markdown fixes and Prettier on editable prose and metadata, plus shfmt on changed shell files. Scrut files stayed in check mode by project policy; snapshots were not reformatted. No code or formatting fixes were needed. `make lint` passed Markdown, Prettier, ShellCheck and shfmt, then failed only at the known review-path operand checks in `tests/fixtures/review-submodule-fixture`, lines 132 through 134 and 254. The brief explicitly excludes that baseline failure. Actionlint passed separately because the make dependency failure prevented its recipe. `make validate` passed JSON, fixture environment reset and all plugin/mirror/catalog checks. Lint is not reported as fully green.

Status: failure, limited to the known baseline file. Commit records the results; no automatic lint fixes were needed. The allocated full suite is recorded below; tidy and PR creation follow.

## Full suite

TOOLING allocated the slot in peer message `f89653b6-1e53-468f-94a8-212d76e30745`. The atomic directory lock recorded `415-reuse-remote-issue-branch` as its holder and was released by the cleanup trap. One `SCRUT_JOBS=2 make -k test-all` run completed with exit 2: 57 documents, 1894 cases, 1893 passed, one failed, none skipped. All launcher, remote, options, combined-issue and sandbox cases passed. The sole Scrut failure is `environment-isolation.md:39`, the unchanged review-submodule fixture operand contract already excluded by the brief. Lint fails for the same known baseline file. Validation passed. Full log: `/tmp/issue415-full-suite.log`.

A final wording search found the start-issue ambiguity note still said local branches. The same correction as create-worktree was applied after the suite, and mirrors rebuilt. Local finding, no reviewer label; our severity Nit, taken; docs only, so no further review round. No runtime code changed after the full suite. The full suite was not repeated.

## Handoff

All 81 focused cases pass, with the 13 remote cases also passing native macOS Bash 3.2. The full-suite baseline caveat and shell Semgrep coverage exception remain explicit. Final version/catalog and documentation checks, signed exact-tree tidy, push and ready PR creation complete the handoff. TOOLING merges.
