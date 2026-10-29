# Fixture operand class audit

The source submodule snapshot work merged in [PR 675](https://github.com/cboone/agent-harness-plugins/pull/675). This follow-up preserves its fixture hardening separately.

TOOLING authorized closing option-like operands across this branch's own fixture files. Scope was collected from the diff against actual origin/main merge base a2e56c535ed6326cc8d531d945fbb6c627a9b335. No other fixture was changed.

| Files                                           | Filesystem and Git path policy                                                                   |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| tests/fixtures/environment-isolation            | Filesystem commands use --; Git directory values use fixture_path; Git init/add paths use --     |
| tests/fixtures/review-submodule-fixture         | Same policy, including traps, recursive initialization, replacements and option-like symlinks    |
| tests/scrut/build-shared-references.md          | Setup commands use --                                                                            |
| tests/scrut/codex-aspects.md                    | Setup/copy/removal commands use --; Git path commands use --                                     |
| tests/scrut/environment-isolation.md            | Shared helper is sourced; no added filesystem operand                                            |
| tests/scrut/review-scope-submodule-consumers.md | Shared helper, canonical-string checks and an actual dash-led Git-directory case                 |
| tests/scrut/review-scope-submodules.md          | Shared helper is sourced; fixture owns setup operations                                          |
| tests/scrut/review-scope.md                     | Filesystem and Git path commands use --                                                          |
| tests/fixtures/review-fixture-paths.bash        | One fixture_path helper prefixes ./ only for dash-led values; contract scratch operations use -- |

Relative JSON remains unchanged. Object identifiers, revisions, references, config values and update-index cacheinfo payloads retain Git's metadata syntax; they are not filesystem operands. The test Git wrapper forwards the original argument vector without adding paths. The dynamic reviewer-document snippet remains owned by the earlier shared symlink-discovery implementation; this fixture supplies its absolute captured filenames.

## Enforced contract

The existing check-fixture-environments tool gains a --review-paths mode, invoked by make lint-shell. It uses the already-required shfmt syntax tree and jq. Its manifest covers all branch-owned shell fixtures and Scrut files, including the shared helper. It checks executable statements, nested substitutions and constant trap/bash/sh programs; expected Scrut output and quoted data are not executable statements. Normal command/exec/env prefixes and absolute command names are recognized.

The check requires protected filesystem operand positions, Git directory options and the path-taking Git forms used here. Unclassified Git commands fail, requiring explicit classification. Parsed metadata forms retain their existing semantics. This is a contract for the audited fixture syntax, not a general shell interpreter.

Twenty-two direct/nested omission plants and five wrapper/flag probes failed with the intended rooted-operand diagnostic. Removing the helper's ./ prefix made its Scrut contract fail; restoration passed. Real dash-led ln/cp/mv/mkdir/rm/touch operations passed under both installed BSD and GNU tools with Bash 3.2. A real Git directory named -checkout is exercised through the helper. No software was installed.

## Outside-scope follow-up

The outside audit examined 75 fixture/Scrut files and recorded 608 candidate diagnostics in the adjacent outside-fixture-operand-follow-up JSON. These include unclassified Git forms and intentionally invalid fixtures; adjudicate them before changing anything. No outside file was fixed. Resource-claims remains untouched and separately tracked in issue 656.

## Prior art and retained regression coverage

[ShellCheck SC2035](https://www.shellcheck.net/wiki/SC2035) protects globs whose matches can become options. A local ShellCheck probe with `rm "$path"` and `git -C "$path" status` reports no operand warning. Retain ShellCheck and extend the existing fixture checker for variable operands and Git path positions. The [Semgrep shell-injection rules search](https://semgrep.dev/r?q=shell+injection) and [Bash support documentation](https://semgrep.dev/blog/2021/scanning-shell-scripts-with-semgrep/) did not identify a ready rule implementing this fixture-specific Git classification and recursive constant-program contract. This is a scoped survey, not a claim that no related rule exists.

The `review-path-contract` scenario in the environment-isolation fixture retains 52 omission plants as input data, including all six filesystem commands, substitutions, traps, constant shell programs, wrappers, Git directory options, path commands and unknown Git forms. Every omission plant must return status 1 and the operand diagnostic. Fifteen unsupported or ambiguous syntax samples require status 1 and a named unsupported-form diagnostic. Protected forms and quoted command text must pass. The submodule-consumer document retains the canonical-string and real dash-led Git-directory checks. No plugin source or version changes.

TOOLING's follow-up classifier direction keeps this finite syntax contract. Supported wrappers and constant-program option forms normalize before inspection; unsupported option forms fail explicitly. Git argument shapes distinguish metadata from paths. Checkout paths require an explicit revision followed by `--`; one positional operand without the separator denotes a revision. Branch creation options retain their metadata values. Unclassified Git forms fail. The ledger records the design decision and review evidence.

Wrapper normalization uses one declarative grammar table for supported options, separators, assignments and inner command or program selection. The same table generates a paired wrapper test matrix; an independent inventory and expected case count keep dropped entries visible. Missing grammar fields fail validation. Constant programs recurse through the same normalizer. Dynamic fixture programs keep the audit's explicit opaque-program allowance. The ledger records mutation and structural-review results.

The narrow allowlist requires unquoted constant wrapper and option words and an unquoted env assignment-name prefix. Values remain argument data. Encoded executable command words and program strings are rejected before decoding or opaque-program handling. Regression coverage includes direct encoded cases and a public `--review-paths` rejection/acceptance pair that preserves Scrut source lines and ignores expected output and non-Scrut fences. The ledger records the exact matrix counts and planted guard failures.
