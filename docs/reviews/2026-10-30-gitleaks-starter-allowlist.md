# Starter secret scanning review ledger

The starter now extends default rules without added exclusions, and the generation guidance requires reviewed, narrowly scoped suppressions.

## Scope and design call

Base: `origin/main`, merge base `5205fada80635f7d9dd4a1967c94a256e60a99cb`.

The starter extends default rules with no added exclusions. TOOLING directed retaining this scope after runtime validation found Gitleaks 8.30.1's inherited lockfile and vendor exclusions. Guidance names those exclusions and the full-configuration alternative. The PR must explain that lockfile acceptance holds only where defaults permit scanning. No full scanner policy, workflow or live configuration is changed.

## Plants and scanner evidence

| Planted defect                                          | Instrument          | Observed result            | Durable coverage                       |
| ------------------------------------------------------- | ------------------- | -------------------------- | -------------------------------------- |
| Add vendor path exclusion to canonical first TOML fence | Scrut starter guard | Exactly one testcase fails | Blanket path exclusion case            |
| Disable defaults in canonical first TOML fence          | Scrut starter guard | Exactly one testcase fails | Disabled defaults case                 |
| Invert the guard's comparison                           | Scrut suite         | Suite fails                | Valid starter and four rejection cases |

Restored canonical files after each plant. Local Gitleaks 8.30.1, using the extracted starter and synthetic GitHub token patterns, detects findings in `Gemfile.lock` and `vendor/sample.txt` in both directory and Git-history scans, including after checkout removal. Its inherited allowlist skips the other four named lockfiles. No provider authentication or verification was performed. An initial synthetic value matched a built-in stopword; the corrected positive control establishes the reported scanner behavior.

The CI regression guard pins the complete active starter TOML and rejects absent or unclosed fences; it does not emulate Gitleaks or claim universal default-rule coverage. Scanner runtime checks are local evidence, not a new CI dependency.

## Review rounds and findings

All review runs used fresh `codex exec` contexts, the read-only sandbox, approval policy `never`, web search disabled and an 872,000-token window. Structural and aspect runs used `gpt-6.1-sol` at high effort; trims used that model at low effort. External metadata and issues were checked by the parent; reviewers could not reach GitHub. Reviewer-local unrun file-writing checks are covered separately by the parent's validation below.

- Structural loop: anti-patterns plus report-only simplify, including independent reuse, simplification, efficiency and altitude angles. Zero findings; clean at Nit. An initial anti-pattern result was superseded because the inherited-coverage clarification landed during its reading pass. The final anti-pattern run covered the corrected documentation. No simplification edits were made; the helper refused an initial invocation from the repository being reviewed, so the installed helper was used instead.
- Aspect loop, Nit round: code, errors and tests returned zero findings; comments returned one Important finding. Reviewer label: `important`. Our severity: Important, because a fingerprint may suppress unrelated same-rule credentials on the same line. Take: yes, fixed in both reference and skill. Review again: yes, because the advice changes suppression behavior.
- Aspect loop, first Important round: code, errors, tests and comments all completed successfully with zero findings; clean at Important. Types was skipped because no types or schemas changed. No further round was warranted. Snapshot comparison found no lasting changes and no scope movement.
- Trims: final comment and prose dry runs completed with no proposals. A preliminary no-proposal trim returned before the fingerprint correction and was superseded by the final pass. Profiles: agent-instructions for skill/reference, none for the plan and test introduction. Generated mirrors were excluded.
- Copilot: paused; not requested or awaited.

The fingerprint finding was confirmed against Gitleaks 8.30.1 source and a local synthetic control: two distinct GitHub-token patterns on the same line produce two findings with one fingerprint; adding it to `.gitleaksignore` suppresses both. Replacing it with a rule-specific anchored content pattern leaves the other finding detectable. The guidance now names content/column and cross-commit limits. This is a manual scanner obligation, documented here; the CI guard tests the emitted starter only.

## Version check

`set-up-secret-scanning`: 3.0.4 to 3.0.5, a patch for prompt and reference fixes. No other plugin changed. No separate canonical Codex manifest exists for this plugin; the generated Codex manifest matches. Marketplace descriptions and registration are unchanged; manifests remain the only version source. Global marketplace coverage and ownership are checked by repository validation.

## Validation

- Baseline Semgrep 1.180.0: disposable shared clone at `9e279a99`, fixed merge base above, `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, `--config p/ci --baseline-commit`. Exit 0, 39 rules, five targets, zero findings and `errors: []`. Ignore policy excluded generated files and tests.
- Final formatting and lint: scoped Markdown fixes and Prettier made no prose changes; shell formatting made no changes. The new Scrut document needed four-backtick outer fences around three cases containing literal TOML fences. Those edits were made manually without changing commands or expected output.
- `make test-all SCRUT_JOBS=2`: exit 2 at the known `bin/check-fixture-environments --review-paths` failure in `tests/fixtures/review-submodule-fixture` (lines 132-134 and 254). That file is unchanged from the merge base. Aggregate status is failed, not clean. An earlier attempt also found the new fence formatting, fixed before the final run.
- Markdown lint, Prettier, ShellCheck and shfmt passed in the final aggregate attempt. Actionlint passed separately because the aggregate stops before reaching it.
- `make validate`: passed, including JSON, fixture environments, manifests, registration, descriptions, mirrors, cross-references and skill inventory.
- `make test-scrut SCRUT_JOBS=2`: completed, exit 2 from make. Fifty-five of 57 documents passed; 1,884 of 1,886 cases passed, two failed and none were skipped. The two failures are detailed below. The starter document passed all five cases. No tests were skipped and no retries ran.
- `lint-and-fix --no-push`: failure solely for the known unrelated fixture check; no required tool was skipped. Its own fence fix is committed.

## Review snapshots

Structural snapshot: `2900eb810cc645995318a69436be0c0eb7b55f1d`. Final Important snapshot: `2f18219a774111544e6b4e06693f672f905ed3ad`, head `9e279a996c49d868d14eea1eb9d27edb0bf69868`, tree `0d20f10284b3c56c596b2679c22157d1e7e1f302`. Final Important review comparison found no lasting changes, no out-of-scope changes and no snapshot movement. The only later change outside process records lengthened three outer test fences.

## Publication decision

TOOLING directed publication after the full suite, with both unrelated failures disclosed, and will file the runner defect separately. The environment-isolation assertion emits exactly the known fixture operand diagnostics (50 of 51 cases passed). The runner stderr-preservation case emits an extra macOS `child setpgid ... Operation not permitted` line before the expected stub error (24 of 25 cases passed). Both affected files and the runner are unchanged from the merge base; neither failure was retried or fixed here.

The full suite used two concurrent documents. It began before TOOLING introduced the shared full-suite lock; the lock was claimed at the end and released by an exit trap. No full-suite rerun was performed.

Local review end states: structural clean at Nit; aspects clean at Important.
