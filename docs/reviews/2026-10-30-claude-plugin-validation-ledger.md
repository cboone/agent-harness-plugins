# Claude plugin validation review ledger

Scope: [issue 480](https://github.com/cboone/agent-harness-plugins/issues/480), branch `ci/480-claude-plugin-validate`, fixed merge base `5205fada80635f7d9dd4a1967c94a256e60a99cb`. TOOLING merges. No installed configuration, credentials or plugin content changes.

## Authentication and baseline validation

Installed Claude Code 2.1.314 validated the marketplace and every canonical plugin under `env -i`, a recorded scratch HOME and system-only PATH. `claude auth status` in that environment returned exit 1, `loggedIn: false`, `authMethod: none`. No credentials were copied. All schema validations passed, with informational README installation advice. The npm registry confirms that exact release and its platform packages exist. A separate scratch manifest with an author object passed; changing only that author to a string returned exit 1 with the schema error "expected object, received string". This real-CLI negative control used the same unauthenticated HOME.

The isolated real `make validate` passed after the plant edits were restored. An earlier overlapping run read the helper while plants rewrote it and encountered a syntax error; that run was discarded. Focused Scrut passed all seven cases on the restored code.

## Plants

Each plant changed one production boundary, ran the focused Scrut document, then restored the exact original file in a `finally` block. All six initial runs exited 2 with a failing behavioral assertion; no compilation failure was counted as detection.

| Planted defect                 | Instrument         | Observed result                                                       | Regression case             |
| ------------------------------ | ------------------ | --------------------------------------------------------------------- | --------------------------- |
| Missing CLI returns success    | Scrut through Make | Missing-CLI case observed exit 0 instead of 2                         | `missing`                   |
| Older CLI returns success      | Scrut through Make | Old-CLI case observed exit 0 instead of 2                             | `old`                       |
| Marketplace failure suppressed | Scrut through Make | Marketplace case observed exit 0 and later plugin calls               | `marketplace-failure`       |
| Plugin failure suppressed      | Scrut through Make | Plugin case observed exit 0 and the next plugin call                  | `plugin-failure`            |
| Plugin loop bypassed           | Scrut through Make | Successful coverage lacked plugin calls; failure case stopped failing | `success`, `plugin-failure` |
| Make integration removed       | Scrut through Make | Call log empty and rejection cases returned success                   | All validation cases        |

## Structural loop

Nit round at `4106c99d`: independent anti-pattern and report-only simplify reviews ran in parallel through fresh `codex exec` contexts, model `gpt-6.1-sol`, high effort, window 872000, read-only sandbox, approval never, web search disabled, stdin closed. Both exited 0 with non-empty schema-valid replies; all nine changed files were read, and the working tree stayed clean. Anti-patterns reported no findings. Simplify completed all four cleanup angles inline under the report-only brief.

| Reviewer's label                                                               | Our severity and impact                                                       | Take or record                                                   | Review again                                       |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------- |
| `nit`, `cleanup-reuse: Reuse the configured version for successful validation` | Nit: duplicate test version makes a pin upgrade require an extra fixture edit | Take: fixture reads its copied pin and supplies the stub version | No: test setup only; production behavior unchanged |

Structural end state: **ended: fixes changed no behavior**. No Important or Critical findings, no recurring defect. The anti-pattern review could not reach GitHub from its sandbox; the parent verified repository ownership and archive status before work and supplied that no PR existed. Runtime checks intentionally stayed outside the reviewers.

## Focused review

Nit round at `7fa35aa2`: code, errors, tests and comments ran in parallel with `gpt-6.1-sol`, high effort, window 872000 and the same read-only settings. All four exited 0, passed the installed helper's schema and membership checks, and returned no findings. Types was inapplicable because no data types changed; simplify belonged to the structural step. Before/after scope snapshots matched, with no changed or outside-scope paths. Focused end state: **clean at Nit**.

The first helper invocation refused before launching reviewers because it came from the checkout under review. The installed 2.3.1 helper then ran successfully. This was a preflight correction, not a repeated review round.

## Trims

One fresh read-only run each of trim-comments and trim-text used `gpt-6.1-sol`, low effort, window 872000, approval never, web search disabled and closed stdin. Both exited 0 and returned the required classified file list and complete proposals. Comments needed no edits. Took two prose rewrites: use "verify" in the plan and split the pin-update instruction into two sentences. No requirements or historical evidence changed.

## Semgrep parser compatibility

The first native baseline scan, in a disposable shared clone of `7fa35aa2`, exited 0 with zero findings but reported a syntax error for the new helper. It was incomplete, not clean. Semgrep 1.180.0's AST diagnostic isolated `10#${...}` arithmetic as the unsupported syntax. A quoted arithmetic spelling parsed but failed Bash execution and was rejected in the scratch experiment. Decimal-prefixed variables parse in Semgrep and evaluate correctly in Bash 3.2, including 0, 00, 08, 09, 314 and 000314. The helper now supplies those decimal-prefixed values directly to its arithmetic comparison, preserving behavior. No additional review round: this syntax adjustment preserves behavior; the added boundary test only strengthens coverage.

Added a leading-zero version case. Removing the decimal prefix made the leading-zero case fail with exit 2 instead of 0; the other seven cases passed. The original helper was restored afterward. Seven plants were caught before the integration fixture adjustment. The full focused document passed all eight cases before planting.

The baseline recheck at `1ed90cbf`, in a second disposable shared clone, completed with exit 0, zero findings and zero errors, 85 rules, seven targets and approximately 100 percent parsed lines. Default ignores excluded three test paths. Native baseline mode scoped the scan to changes from the fixed merge base; with zero current findings, Semgrep skipped its second comparison pass. Test paths are covered by Scrut and shell checks rather than claimed as Semgrep coverage.

## Full suite and integration finding

The shared lock was acquired atomically, with handle `480-claude-plugin-validate` in its owner file and trap cleanup. Ran `SCRUT_JOBS=2 make test-all` without silent flags. It exited 2 on the brief-named `review-submodule-fixture` operand guard. Since that prevented later prerequisites, ran `make validate` and one full `make test-scrut`, both with `SCRUT_JOBS=2`, while retaining the lock. Validation passed. Full Scrut completed all 57 documents and all 1,889 cases: 1,885 passed, four failed, none skipped. The only failing document was environment-isolation: one known baseline guard assertion and three snapshot mismatches introduced by the new Make step. The Claude-validation document passed all eight cases. The driver released its lock on exit. No second full run was started.

The three budget tests also exposed a CI dependency: their real `make validate` invocation now needed Claude in a Scrut job that does not install it. Fixed their fixture to copy the committed Claude stub, verify its PATH resolution, and supply the copied version pin and an owned log; changed the three snapshots to include the new helper command. The baseline operand-contract assertion is unchanged.

| Reviewer's label                       | Our severity and impact                                                                          | Take or record                                             | Review again                                                     |
| -------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- | ---------------------------------------------------------------- |
| Manual post-review integration finding | Important: three budget tests would fail their snapshots locally and require an absent CLI in CI | Take: isolated committed stub and three matching snapshots | No: fixture and test changes only; production behavior unchanged |

## Final checks and publication

The lint-and-fix pass used scoped Markdown and Bash fixers, preserving Scrut snapshots from reformatting, followed by `make lint` and Actionlint. Markdown, Prettier, ShellCheck, shfmt and Actionlint passed. `make lint` remains failed only on the explicitly excluded baseline fixture operand guard; the brief authorizes carrying that known failure through the PR. `make build` left no generated drift. Check-versions verified all 60 registrations, catalog coverage, manifest-only version ownership and matching Codex versions. No plugin content changed, so no plugin bump applies.

The affected environment-isolation rerun completed all 51 cases: 50 passed, with only the known baseline operand-contract assertion failing. All three repaired budget cases passed. No full suite was repeated after this test-only fix. Removing the stub PATH selection made its preflight return 1 before Make ran, establishing that it refuses the real CLI; the fixture was restored byte-for-byte. This is the eighth detected plant, separate from the manual real-CLI schema negative control.

The final membership recheck at `e762411a` completed in a third disposable shared clone: exit 0, zero findings and errors, 85 rules, seven targets, approximately 100 percent parsed lines, and five ignored test paths. This is a verification scan after test membership changed, not another review round.

The final mailbox handoff and worker checkpoint carry the signed exact-tree tidy comparison, publication identity and any remaining gate. Publication is authorized through a ready PR; TOOLING owns merging. The known main fixture failure remains disclosed. No live configuration is changed.
