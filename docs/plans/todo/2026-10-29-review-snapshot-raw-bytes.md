# Review snapshot raw bytes

## Authority and contract

Build through a ready PR for [the snapshot guarantee issue](https://github.com/cboone/agent-harness-plugins/issues/534); TOOLING merges. The 2026-10-29 10:34 AM ET Inbox decision, relayed by TOOLING, keeps staging, unstaging and intent-to-add invalidation and drops the issue's older bucket-invariance request. Existing semantic index coverage already detects the staged-blob instance. The raw-byte instance still reproduces.

Fixed review base: `7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`. Integrating `main` fast-forwarded the unchanged branch; no merge commit was created. All new commits are signed.

## Prior art and representation

Extend the existing collector and Git-tree comparison rather than adding a scanner or dependency. [Git hash-object](https://git-scm.com/docs/git-hash-object) offers `--no-filters`, which bypasses clean filters and EOL conversion. [Git attributes](https://git-scm.com/docs/gitattributes) explains why normalized blobs omit those bytes. Preserve the normalized `tree` API; add a `raw_tree` built from the temporary inventory with unfiltered regular-file blobs and exact current symlink text. Under TOOLING's sparse-checkout call, omit intentionally absent skip-worktree ordinary files and symlinks from the raw tree while preserving normalized tree, index and file inventory compatibility. Present sparse paths are hashed normally. Gitlinks retain pointer metadata with recursively captured child scopes. Existing tree plumbing supports path-safe comparisons and avoids a second custom manifest format.

## Work

1. Add staged-blob, EOL and clean-filter Scrut coverage. Record the staged case as an already-passing regression; reproduce both raw-byte omissions before implementation.
2. Capture and recheck raw trees alongside normalized trees, hash them into snapshots, and compare them in mutation reports recursively. Keep caller indexes untouched and preserve compatibility with older scope artifacts.
3. Specify exactly which inputs change the snapshot and which do not. Retain submodule behavior and intent-to-add lifecycle; leave historical child guidance to [its separate issue](https://github.com/cboone/agent-harness-plugins/issues/674).
4. Plant the old representation and test raw-only outside-scope edits, recursive coverage, symlink boundaries and collection stability. Run Bash 3.2 and affected suites.
5. Complete full local review order at the fixed base, with independent structural and focused counters, then trims, disposable-clone Semgrep baseline, lint-and-fix without push, full tests, versions and signed exact-tree tidy. Push, open ready, observe green CI and report to TOOLING.

Stop at recurrence, required design/scope calls, unavailable baseline/tools, unfixable scoped lint failures or a closed gate. Shell-only Semgrep partial parsing follows the standing coverage/ShellCheck rule. Never answer a Hooks need review picker.
