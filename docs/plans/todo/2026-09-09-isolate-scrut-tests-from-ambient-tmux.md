# Isolate scrut tests from the ambient environment

Addresses [#330](https://github.com/cboone/agent-harness-plugins/issues/330).

## Context

`make test-scrut` fails for anyone who runs it from inside a tmux session, which is the normal working environment for this repository's own users, since `workmux` puts every worktree in a tmux window. CI never catches it: GitHub runners have no tmux session, so `TMUX` is unset there and the tests take the intended path.

Two testcases supply a fixture socket through `WORKMUX_TMUX` but never unset the ambient `TMUX`. `resolved_tmux_env()` (`plugins/create-worktree-from-issue/scripts/launch-workmux:142-151`) checks `TMUX` before `WORKMUX_TMUX`, so the developer's real session wins over the fixture. The tmux stub then derives a socket that never matches `STUB_TMUX_PANES`, no pane is found, `${state}/tmux-log` is never written, and the trailing `sed` fails.

That precedence is correct for the script: a real session should win over a configured default. Nothing in `plugins/` needs to change. The defect is that the test suite inherits the developer's shell instead of controlling it.

Investigating the reported failure showed it is one instance of a broader class. Measured on this branch, exporting a single variable before `make test-scrut`:

| Exported variable                         | Failures (of 22) | Realistic for a workmux user? |
| ----------------------------------------- | ---------------- | ----------------------------- |
| `TMUX`                                    | 2                | Yes, always inside tmux       |
| `WORKMUX_TMUX`                            | 6                | Yes                           |
| `WORKMUX_TERM`                            | 10               | Yes                           |
| `STUB_CAPTURE_TERM` + `STUB_CAPTURE_TMUX` | 3                | No, but structurally exposed  |
| `TMUX_TMPDIR`                             | 0                | Harmless today, still read    |

`WORKMUX_TERM` is the worst of these: `run_workmux_command` reads it unconditionally at `launch-workmux:273-274`, ahead of the `TERM=dumb` fallback, and no testcase guards it. Any workmux user who has set it sees 10 failures with no obvious cause.

Intended outcome: the suite produces identical results regardless of the developer's shell, and no future testcase can reintroduce this by forgetting.

## Approach

Three layers, so no single omission can resurrect the bug:

1. **Per-testcase** `env -u TMUX`, matching the convention already used in 8 of the 15 testcases. Keeps intent visible where a reader is looking.
2. **Shared helper** `unset` in `prepare_stubs`, so isolation is the default for anything that uses it.
3. **Make target** guard, so the whole suite is ambient-independent regardless of how any individual testcase is written, and so `test-scrut-update` cannot bake bad expectations into the file.

Layer 3 also closes a hazard the issue did not mention: `Makefile:16-25` defines `test-scrut-update`, which has the identical leak. Running it inside tmux rewrites the two affected testcases' expectations to match the broken behavior, committing the bug as "correct."

## Changes

### 1. `tests/scrut/launch-workmux.md`

**a. Fix the two reported failures.** Add `-u TMUX` to the `env` invocation at line 133 (`resends existing worktree prompt`) and line 159 (`ignores prompt resend failure`):

```diff
-    | env PATH="${stub_dir}:${PATH}" STUB_GIT_WORKTREE_PORCELAIN="${porcelain}" ...
+    | env -u TMUX PATH="${stub_dir}:${PATH}" STUB_GIT_WORKTREE_PORCELAIN="${porcelain}" ...
```

**b. Make the three latent testcases explicit**, so every testcase in the file states its position on `TMUX` rather than leaving readers to work out which ones are ambient-safe by accident. These pass today only because they never assert on tmux output:

- Line 43, `escapes stdin and passes base`: `env PATH=...` → `env -u TMUX PATH=...`
- Line 301, `rejects empty stdin`: `env WORKMUX_LAUNCH_WAIT_SECONDS=0` → `env -u TMUX WORKMUX_LAUNCH_WAIT_SECONDS=0`
- Line 310, from-issue `rejects empty stdin`: same edit

**c. Harden the shared helper.** `prepare_stubs` (lines 8-15) currently sets no defaults and unsets nothing. Add an `unset` as its first statement:

```diff
 $ function prepare_stubs() {
+>   unset TMUX TMUX_TMPDIR WORKMUX_TMUX WORKMUX_TERM
 >   state="$(mktemp -d)"
```

Safe for every existing testcase: the two `keeps existing TMUX` cases (lines 94, 110) set `TMUX=` on their own `env` line after calling `prepare_stubs`, and the four discovery cases set `TMUX_TMPDIR=` the same way, so both override the unset. Scrut persists shell state across blocks in a document, so the unset also covers the later testcases that never call `prepare_stubs`.

Deliberately not unsetting `STUB_*` here, to keep the helper readable. No human exports those; layer 3 covers them.

Do **not** remove the existing `-u TMUX` from lines 62, 78, 181, 203, 225, 247, 268, and 287. Those are semantically load-bearing, not redundant hygiene: they were added by `f3dd5c6` and `9572163` specifically to exercise the no-tmux code path, and the testcase names (`uses WORKMUX_TMUX`, `continues without tmux`) depend on it.

### 2. `Makefile`

Both targets duplicate the same 7-line variable block, which is what let the guard be missing from one of them. Introduce a single list so the guard cannot drift between them:

```make
SCRUT_TEST_DIR := tests/scrut/

# Ambient variables the launcher scripts and stubs read. Unset them so results do
# not depend on the developer's shell; every testcase that needs one sets it
# explicitly on its own env line. See issue #330.
SCRUT_UNSET := -u TMUX -u TMUX_TMPDIR -u WORKMUX_TMUX -u WORKMUX_TERM \
	-u WORKMUX_LAUNCH_WAIT_SECONDS -u WORKMUX_CODEX_PROMPT_SUBMIT_DELAY_SECONDS \
	-u STUB_CAPTURE_TERM -u STUB_CAPTURE_TMUX -u STUB_GIT_WORKTREE_PORCELAIN \
	-u STUB_STATE -u STUB_TMUX_FAIL_COMMAND -u STUB_TMUX_LOG -u STUB_TMUX_PANES
```

Then prefix the existing variable block in **both** `test-scrut` (line 7) and `test-scrut-update` (line 18):

```diff
-	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/..." \
+	env $(SCRUT_UNSET) \
+	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/..." \
```

`env` accepts `VAR=value` operands after its `-u` flags, so the existing assignments continue to apply to `scrut` unchanged.

## Explicitly out of scope

- **No script changes.** `resolved_tmux_env()` precedence is correct as written. Since nothing under `plugins/` changes, the `dist/codex/` and `dist/opencode/` mirrors stay in sync and need no regeneration.
- **No version bumps.** No plugin source changes, so no `plugin.json` or `marketplace.json` edits and no catalog state tag recompute. Precedent: `a81a4a4` (`test: clean up tmux socket fixture directories`) changed this same file with no version bump.
- **`.github/workflows/ci.yml` is not changed.** CI does not go through `make test-scrut`; it calls the pinned external reusable workflow `cboone/gh-actions/.github/workflows/run-scrut-tests.yml@v3.0.0` with its own duplicated `scrut-env` list (`ci.yml:48-60`). A runner has none of these variables set, so the guard is unnecessary there, and the workflow lives in another repository. Worth noting as a standing gap: the env list is now maintained in three places, and only two of them get the guard.

## Verification

Run all of these from inside a tmux session, which is the environment that exposes the bug.

1. **The regression.** This is the command that fails today with `20 succeeded, 2 failed`:

   ```bash
   make test-scrut          # expect: 22 succeeded, 0 failed
   ```

2. **No behavior change without tmux**, matching what CI sees:

   ```bash
   env -u TMUX make test-scrut          # expect: 22 succeeded, 0 failed
   ```

3. **The guard actually strips what it claims.** Each of these fails today by the count in the Context table and must pass after the change:

   ```bash
   WORKMUX_TERM=xterm-256color make test-scrut                  # today: 10 failed
   WORKMUX_TMUX="/tmp/tmux-501/leak,999,%9" make test-scrut     # today: 6 failed
   STUB_CAPTURE_TERM=1 STUB_CAPTURE_TMUX=1 make test-scrut      # today: 3 failed
   ```

4. **The per-testcase and helper layers work independently of the Makefile.** Bypass the make guard entirely and confirm layers 1 and 2 still hold:

   ```bash
   COMPOSE_ISSUE_PROMPT_BIN="$(pwd)/plugins/create-worktree-from-issue/scripts/compose-issue-prompt" \
   CREATE_WORKTREE_LAUNCH_WORKMUX_BIN="$(pwd)/plugins/create-worktree/scripts/launch-workmux" \
   CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN="$(pwd)/plugins/create-worktree-from-issue/scripts/launch-workmux" \
   GIT_WORKTREE_STUB_BIN="$(pwd)/tests/fixtures/git-worktree-stub" \
   TMUX_STUB_BIN="$(pwd)/tests/fixtures/tmux-stub" \
   UNIX_SOCKET_FIXTURE_BIN="$(pwd)/tests/fixtures/create-unix-socket" \
   WORKMUX_STUB_BIN="$(pwd)/tests/fixtures/workmux-stub" \
   scrut --shell bash test tests/scrut/
   ```

   Expect `22 succeeded`. The `TMUX` cases pass via layers 1 and 2; `WORKMUX_TERM` is not stripped on this path, which is the accepted limit of the per-testcase layers.

5. **Expectations are genuinely unchanged**, confirming the fix restores the intended path rather than editing assertions to match broken output:

   ```bash
   make test-scrut-update && git diff --stat    # expect: no diff
   ```

6. **Lint**, since a Markdown file changed (`ci.yml:29`):

   ```bash
   yarn lint
   ```

   `shellcheck` and `shfmt` (`ci.yml:31,35`) cover `bin/*`, `plugins/*/scripts/*`, and `tests/fixtures/*` only, none of which change.

## Commits

Two commits, using the `test:` prefix per repository precedent (`a81a4a4`). Not `fix:`, since no shipped plugin behavior changes and the issue is entirely test infrastructure:

1. `test: isolate scrut launcher tests from ambient tmux (#330)` — the `tests/scrut/launch-workmux.md` changes
2. `test: strip ambient launcher variables in scrut make targets (#330)` — the `Makefile` changes
