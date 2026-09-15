# Issue #413: Generate worktree names within the invoking skill

## Approved design

Classification: bug fix. Preserve AI naming by embedding matching naming instructions in `create-worktree` and `address-issue-in-worktree`. The invoking agent generates a semantic candidate from the issue title, labels, and body or task description, treating that content as data, before composing the destination prompt and chain footer. User-supplied names bypass generation.

Use lowercase kebab-case, an imperative verb and noun, and a `fix/`, `feature/`, `chore/`, or `docs/` prefix. Repository conventions take precedence. Target at most five words and 50 characters for the descriptive slug; the launcher inserts the issue number. Adapt the naming instructions from [workmux v0.1.262](https://github.com/raine/workmux/blob/v0.1.262/src/llm.rs).

## Implementation

- Replace `--auto-name` with `--generated-name <candidate>`, optionally accepting `--issue <positive integer>` and `--base <branch>`. Preserve positional exact branch names. Reject conflicting modes, empty or invalid candidates, invalid issue numbers, and obsolete calls with migration guidance.
- Preserve issue branch reuse, ambiguous-match reporting, number insertion and deduplication, meaningful numbers, case, nested paths, Git validation, and selected-branch output.
- Remove the naming subprocess, dry-run parser, and capture files. Preserve literal prompt composition, template escaping, detached launch, and existing-pane delivery. Keep bundled launcher copies byte-identical.
- Update both skills and READMEs, remove naming CLI and naming-specific workmux version requirements, and correct prefix attribution in `use-git` and `pr`.
- Set versions to `create-worktree` 1.6.0, `address-issue-in-worktree` 2.3.0, `use-git` 1.2.4, and `pr` 1.8.5. Recompute the catalog state and rebuild both mirrors.

## Verification

- Convert naming snapshots to supplied candidates and retain normalization, reuse, ambiguity, and script parity coverage.
- Test invalid arguments and empty prompt cleanup. Reject naming invocations in the workmux stub and require exactly one explicit-branch call on successful launches.
- Verify issue content containing `---`, template delimiters, shell-like text, and the chain footer reaches the destination literally without naming execution.
- Review semantic naming examples and repository overrides. Run `lint-and-fix`, cross-reference validation, `make test-all`, and `git diff --check`.

## Delivery and boundaries

Create small GPG-signed conventional commits referencing (#413). Workmux continues starting the configured destination agent. Leave workmux configuration untouched and keep issue #414 timeout and signal-cleanup work outside this change.
