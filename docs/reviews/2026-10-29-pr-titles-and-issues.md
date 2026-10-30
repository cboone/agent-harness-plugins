# Title and issue fixes: validation ledger

Status: local review and validation complete. Signed-commit tidy and exact-tree confirmation precede publication.

## Scope and implementation

Base: `7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`. Both issues and all comments were read. Both already carry the `in progress` label. Repository ownership was checked: cboone/agent-harness-plugins, active, not a fork.

The base already satisfies the PR creation and remediation title requirements and the issue-only guards for both detection strategies. The remaining unsafe examples live in use-git's create-issue skill. All three now single-quote titles and document apostrophe escaping. Supporting tmpfile examples use the same quoting. Use-git is patch-bumped from 1.3.6 to 1.3.7; generated mirrors were rebuilt.

## Checks

- `make build`: passed.
- `make test-scrut SCRUT_TEST_DIR=tests/scrut/github-skill-examples.md`: passed, 3 cases. Exercises five documented title commands, the apostrophe example, and both issue-detection filters with issue and PR URL fixtures.
- ShellCheck initially reported SC2016 for deliberate literal substitution syntax and SC2154 for the fixture environment input. Added a scoped annotation and a required-environment check. ShellCheck and shfmt then passed.
- Required formatter attempt: `corepack yarn prettier --write` with the three edited Markdown paths failed with `Couldn't find the node_modules state file - running an install might help (findPackageLocation)`. `node_modules` is absent. Global prettier and markdownlint-cli2 exist, but the required project commands use Yarn and cannot pass in this dependency state.
- TOOLING clarified that restoring locked worktree dependencies is permitted. `YARN_ENABLE_NETWORK=0 YARN_ENABLE_SCRIPTS=false corepack yarn install --immutable` passed from cache without lockfile changes. Required formatting and the three regression cases then passed.
- Planted double-quoted issue titles, permissive issue filters and an unescaped apostrophe independently. The checks returned 1, 1 and 2 respectively, then passed after each restoration.
- Initial `make test-all` passed Markdown/Prettier, shell lint and JSON checks, then stopped at fixture validation: the textual suffix pattern for jq extraction resembled a diagnostics redirect. Extracting through the closing quote removes that ambiguity.
- Initial standalone anti-patterns and report-only simplify runs used gpt-6.1-sol, high effort, 872000 context and read-only sandboxes. Both failed code-mode host negotiation before reading files. Recorded PIDs 15901 and 15902 were stopped and reaped with exit 143. No findings or clean outcome were inferred. Fresh Codex subagents are the prescribed fallback; their read-only restriction is by instruction, with inherited host guidance and context window.
- Version checks passed against the verified default branch `origin/main`: only use-git has canonical plugin changes, with a forward patch bump; marketplace coverage and manifest-only version ownership passed. The full validator also passed during `make test-all`.
- Final `make test-all`: passed, including Markdownlint, Prettier, ShellCheck, shfmt, actionlint, JSON and plugin validation, fixture environment validation, and all 53 Scrut documents. No skipped or failed documents. The final ledger-only edit was checked with the project Markdownlint and Prettier commands.

## Review rounds

Structural loop: one completed Nit round at `fb473ac9`, compared with the fixed base above. Anti-patterns read all eight canonical changed files and walked all thirteen applicable checklist items, including sibling forms, command input, test validity and prose control flow. Report-only simplify read the same files and completed reuse, simplification, efficiency and abstraction-level angles in one fallback pass. Both returned complete, schema-validated success with no findings. Generated mirrors were excluded. No lasting changes were found: clean worktree and tree `10f6b119faba858a2eaa1f260ad92d5474976d0e` before and after. End state: **clean at Nit**. TOOLING accepted this round with the instruction-only read-only limitation disclosed.

The focused code, tests and comments aspects started through native subagents before TOOLING's subsequent sandbox instruction arrived. All three were interrupted. Their output is not review evidence and consumes no completed round. Errors and types were not run. No more reviews will use this fallback.

Review artifacts and failed standalone logs remain in the session-owned `/tmp/pr-title-review.dyTXfN` directory. Failed runs are not clean results. The non-review checks above supply execution and plant evidence that the reading reviewers deliberately did not reproduce.

Focused loop: one completed Nit round at `b7f5c78b`, using the installed review-pr-with-codex helper through `codex exec`. Code, errors, tests and comments all exited 0 with schema-validated results. Model gpt-6.1-sol, effort high, window 872000, built-in read-only sandbox, approvals never and web search disabled. Types skipped because no types changed; simplify was already covered by the structural loop. No timestamped runtime host ERROR appeared. Scope comparison found no lasting changes and no snapshot change, tree `379fbdbf5db986070d731ebb97a532fb96231552` before and after. Code reported one Important finding; other aspects reported none. This round is not clean. Artifacts: `/tmp/pr-title-focused.iuWtNw`.

## Remaining required work

Next step: tidy with exact-tree comparison, push and one ready PR closing both issues. TOOLING merges; the worker never merges. Review counts persist: structural loop completed one Nit round, clean at Nit; focused loop completed one Nit round with an Important take, followed by one Important round, clean at Important.

## Findings ledger

The completed structural round had no findings or reviewer-label, severity, disposition or re-review decisions to record. ShellCheck and fixture-validator diagnostics above were local validation findings, fixed before handoff. No design change or recurrence decision was made.

### Focused Nit round: fixture executes extracted commands

- **Reviewer's label:** `important`, confidence 100. Title: `write-bash-scripts: No eval forbids executing extracted Markdown commands.` Code aspect, `tests/fixtures/github-skill-examples`, both eval calls.
- **Our severity:** Important. The Bash checklist explicitly prohibits eval. The capturing gh function does not constrain the substitutions and shell operators executed before or around that function.
- **Take or record:** taken. TOOLING chose the proposed disposable-script design: materialize each example as a Bash script, run with only a committed gh capture stub on PATH, and refuse execution unless gh resolves to that stub. Both eval calls were removed. A regression case confirms that an inherited gh function cannot bypass the guard. Commands still execute real shell quoting against synthetic title data.
- **Review again:** behavioral test-fixture changes require another focused round at Important. No downgrade. TOOLING's design call arrived on 2026-10-30, mailbox sequence 000004, and authorizes continuing through the ready PR.

### Focused Important round

Code, errors, tests and comments all exited 0 with validated results at `3bd3a383`. Same model, effort, window and built-in read-only sandbox as the Nit round. No runtime host ERROR, lasting tree changes or scope changes. Code, errors and tests had no findings. Types remained inapplicable. End state: **clean at Important**.

- **Reviewer's label:** `suggestion`, confidence 100. `write-markdown: Factual accuracy, remove the resolved design gate.` Comments aspect, this ledger's remaining-work paragraph.
- **Our severity:** Nit. The paragraph repeated an already-resolved gate, while the fixture and finding disposition correctly described the implemented design.
- **Take or record:** taken as a local documentation correction. The remaining-work paragraph now names the actual next steps and preserved round counts.
- **Review again:** no; documentation-only correction changes no behavior.

After the fixture change, all four regression cases passed. Repeated plants for double quotes, permissive issue filtering and unescaped apostrophes failed with exits 1, 1 and 2; removing the stub guard caused the Scrut document to fail. Restoring the source returned all four cases to passing. Artifacts: `/tmp/pr-titles-finish.NFFOTV`.

## Final validation

Both trim skills completed through sandboxed gpt-6.1-sol runs at low effort with an 872000 context window. Comment trimming proposed no changes. Text trimming proposed four wording-only edits, all taken; exact requirements, evidence and round counts were preserved. Mirrors were rebuilt, and all four affected regression cases passed afterward. No behavior changed, so no extra review round was needed.

The full `make test-all` run after the fixture redesign passed: all 53 Scrut documents, lint and validation. The subsequent trims changed prose only; the affected regression document was rerun successfully.

Semgrep baseline scan passed in a disposable `git clone --shared` of `8b0134c6`, with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, baseline `7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`, and `p/default`: 131 rules on all twelve changed targets, zero findings, no parsing errors and approximately 100 percent parsed lines. The initial default-ignore scan omitted fixtures; adding an empty `.semgrepignore` only in the disposable clone included both Bash fixtures in the completed scan. JSON and logs are retained under the artifact directory. The source worktree was not used for baseline checkout. ShellCheck also passed for both fixtures.

Final lint follows the lint-and-fix skill with `--no-push`. Global Markdown fix commands would include protected Scrut snapshots, so Markdownlint and Prettier use project check commands; snapshots are not reformatted. ShellCheck, shfmt, actionlint and validators remain required checks. No required lint tool is skipped.

Final project lint and validation passed with no fixer changes needed. Lint status: success; check-only by project policy: global Markdown fixers; unresolved or skipped: none. The caller continues to tidy and publication. Version checks passed against the verified default `origin/main`: use-git 1.3.6 to 1.3.7, matching generated mirror, complete marketplace coverage and manifest-only version ownership. The completed plan is archived under `docs/plans/done/2026-10-29-pr-titles-and-issues.md`.
