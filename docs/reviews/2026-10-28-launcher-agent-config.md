# Launcher agent and config flags

## Scope and authority

Implement destination `--config` and `--agent` forwarding for workmux, closing issue 629. Chris (he/him) authorized building through a ready PR in Inbox, 2026-10-27 at 8:54 PM ET; TOOLING merges. TOOLING corrected the version target to installed workmux `0.1.277` and confirmed one canonical launcher plus its generated mirror. Install nothing. Full local review order applies.

## Live config experiment

Installed `/opt/homebrew/bin/workmux --version`: `workmux 0.1.277`.
Scratch record: `/tmp/launcher-629-probe/run.ED3bsQ`. Isolated `XDG_CONFIG_HOME` contained a global config; a throwaway repository contained `.workmux.yaml`. All hooks only touched marker files, and file operations used sample text files. No agent or tmux session was launched: `workmux add --headless --json` performed actual provisioning.

- Control: repository config specified `repo-hook`, copied `repo-copy`, and linked `repo-link`. All three appeared; global hook did not.
- Agent-only alternate profile outside the repository: `--config` omitted all repository operations and ran `global-hook` instead.
- Alternate complete profile inside the repository: its `profile-hook`, copied `global-copy`, and linked `global-link` appeared. Repository entries were absent.
- The same complete profile outside the repository ran its hook but did not copy/link files that existed only in the repository. File source location matters; the probe does not claim arbitrary profiles preserve file sources.
- `--agent selected-probe --dry-run` without `--config` listed the repository hook, copy and symlink. `--agent` with `--headless` was refused as a multi-worktree option. No failed command was treated as live coverage.

Observed: `--config` replaces repository config while merging global config. Both calling skills document this measured boundary and installed version.

## Validation and defect plants

Focused controls passed: original launcher document 79/79 (including the new cases before separating them); destination-options document 15/15. Tests and stubs committed before plants. Removed the stdin guard from validation cases by supplying a valid prompt before the final plant run.

| Planted defect         | Instrument    | Actual result                                    | Permanent coverage                                                     |
| ---------------------- | ------------- | ------------------------------------------------ | ---------------------------------------------------------------------- |
| Drop config forwarding | Focused Scrut | Failed 3/15 cases for each forwarding plant      | Explicit and generated config/agent launches                           |
| Drop agent forwarding  | Focused Scrut | Failed 3/15 cases for each forwarding plant      | Explicit and generated config/agent launches                           |
| Accept invalid config  | Focused Scrut | Failed 3/15 cases; invalid values reached stub   | Missing, empty, absent, directory, unreadable and option-shaped config |
| Accept empty agent     | Focused Scrut | Failed 2/15 cases; empty/whitespace reached stub | Missing, empty, whitespace and option-shaped agent                     |

## Review ledger

Structural Nit round: anti-patterns and report-only simplify ran in parallel through fresh read-only `codex exec`, gpt-6.1-sol, high effort, 872000 context. Both exited 0 with nonempty completed output; anti-pattern schema/check passed and coverage was complete. No lasting changes found. Simplify: clean at Nit, no findings.

| Finding                                               | Reviewer label | Our severity                                                             | Take or record                                                    | Review again  |
| ----------------------------------------------------- | -------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------- | ------------- |
| External config can omit repository-only file sources | `important`    | Important: following the incomplete advice can omit required setup files | Take: preserve measured location caveat in both skills and README | No: docs only |
| README omits both destination options                 | `nit`          | Nit: discoverability gap                                                 | Take: add both options to both tables                             | No: docs only |

Structural loop ended: fixes changed no behavior. Sandbox workmux help/version and GitHub metadata checks were unavailable; parent verified installed version/help and ownership outside that sandbox. Bash syntax, shellcheck, shfmt and manifest parsing passed in the reviewer. Bash 3.2 destination-options control passed 15/15 after restoring plants.

Aspect Nit round: code, errors, tests and comments ran through the installed `codex-aspects` helper, gpt-6.1-sol/high/872000, read-only. Every run exited 0, returned nonempty schema-valid output, and found nothing: clean at Nit. Types skipped because no types changed. Scope tree `2a3ff7b005b2c41c3a2c384f6ba0e6fa84eb925c` stayed identical; no lasting changes found. The in-repository helper refused before launching; the installed copy then ran successfully. No review run was retried.

Trim round: fresh read-only Codex runs, gpt-6.1-sol/low/872000, both exited 0 with complete nonempty proposals. Comment trim found no eligible changed comments. Text trim proposed five meaning-preserving rewrites across both skills and this record, all accepted. The README's changed units were classified locally because the dry-run file list omitted it: retain both option rows and measured setup caveat unchanged. Generated mirrors and Scrut snapshots excluded. No behavior changed.

Semgrep: disposable shared clone of `1fa03fae`; `SEMGREP_REPO_NAME=cboone/agent-harness-plugins semgrep scan --config auto --baseline-commit 4fd00feabdddbfbad2d25966fd01388af1977f26 --json`, metrics at default. Exit 0, 131 rules, 6 targets, zero findings. Gap: Bash `PartialParsing` on launcher lines 3–787 (EOF). Detached baseline checkout scanned with the same auto config: exit 0, zero findings, same `PartialParsing` from line 3 through baseline EOF (760). Shellcheck passed on launcher and stub; diff contains no new suppressions. The brief explicitly accepts this matched parser gap, so scan is complete under that exception, not fully parsed.

Final lint uses documented `make lint` plus `make validate`. Fixers that reach Scrut snapshots are downgraded to check mode under the repository's no-reformatting rule; edited prose was formatted through scoped Prettier and shell through shfmt. No required check is skipped. Full `make test-all` passed: 33 documents, 1390/1390 Scrut cases succeeded, zero failed or skipped, with lint and validation also successful. Version check against actual `origin/main` merge base `4fd00feabdddbfbad2d25966fd01388af1977f26`: workmux 1.0.1 → 1.1.0 is a forward minor capability bump; generated manifest matches, all plugins registered, manifest-only version ownership verified. `origin/main` was confirmed equal to the remote main SHA. Final documentation check aligned option bullets with argument hints; no semantics changed. Scoped Markdown and mirror validation follow that record-only update.

Tidy control before publication: back up to `feature/629-launcher-agent-config-pre-tidy`, reconstruct feature, tests and docs as three signed commits from the merge base, then require `git diff --quiet feature/629-launcher-agent-config-pre-tidy HEAD` to exit 0. PR and CI outcome, the measured tidy result and final head are delivered to TOOLING in the worker's final checkpoint and report. Worker never merges.
