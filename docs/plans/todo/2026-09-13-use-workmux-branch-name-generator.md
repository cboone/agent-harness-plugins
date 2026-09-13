# Use workmux's branch name generator, with the issue number inserted

## Context

`create-worktree` and `address-issue-in-worktree` do not derive branch names in code. The naming algorithm is prose in both `SKILL.md` bodies, executed by the model: strip a conventional-commit prefix, lowercase and hyphenate, truncate to 50 characters at a word boundary, then drop a dangling filler word if truncation fired. `launch-workmux` receives the finished name as a positional argument and only transforms it once, replacing `/` with `-` for temp files and tmux buffers.

The names that algorithm produces are clunky. They are transliterations of issue titles rather than descriptions of the work, and the rules exist to paper over that: the filler-word trimming and the truncation guard are both repairs for mechanical title slugification, added in commit `b0efd859` after two trial runs produced `-in-bin` and `-before` endings.

`workmux add -A` already generates branch names from the prompt with an LLM, and it produces better ones because it reads the whole prompt rather than transliterating the title. The gap is that it knows nothing about issue numbers, and the `pr` skill's primary issue-linking strategy reads the number straight out of the branch name.

This plan moves naming out of skill prose and into `launch-workmux`, which asks workmux for a name and inserts the issue number into it.

### What the generator produces today

Verified with `workmux add -A -P <file> --dry-run`, which runs the generator and creates nothing:

| Input                            | Generated name                            |
| -------------------------------- | ----------------------------------------- |
| Issue 356 prompt, `maintenance`  | `chore/validate-cross-references`         |
| Issue 358 prompt, `bug`          | `fix/consult-config-before-auto-fix`      |
| Issue 358 prompt, second run     | `fix/consult-agent-config-before-auto-fix` |

Two facts follow. The generator is non-deterministic, so a rerun for the same issue will not reproduce the earlier name. And the type prefix comes from the user's own `auto_name.system_prompt`, not from workmux: the built-in prompt asks for bare kebab-case such as `dark-mode`.

The plugin cannot ship a naming prompt of its own. The only per-invocation config hook, `--config`, replaces a project's `.workmux.yaml` wholesale rather than layering on it, which would discard project panes and hooks.

## The naming contract

Take whatever workmux returns and insert the issue number. Do not invent a prefix, do not re-slugify, do not second-guess the wording.

| Generated                     | Issue | Result                            |
| ----------------------------- | ----- | --------------------------------- |
| `feature/make-things-better`  | 387   | `feature/387-make-things-better`  |
| `fix/fix-the-login-page`      | 42    | `fix/42-fix-the-login-page`       |
| `make-things-better`          | 387   | `387-make-things-better`          |
| `feature/make-things-better`  | none  | `feature/make-things-better`      |

A bare slug stays bare. The `pr` skill's strategy 1 already matches `N-description` alongside `TYPE/N-description`, so linkage holds either way, and a user who wants prefixes configures `auto_name.system_prompt` in workmux.

## Changes

### 1. `launch-workmux`, in both plugins

`plugins/create-worktree/scripts/launch-workmux` and `plugins/address-issue-in-worktree/scripts/launch-workmux` are byte-identical and guarded by two testcases in `tests/scrut/repo-tooling.md`. Change one and copy it to the other.

New usage, with the existing positional form unchanged:

```text
launch-workmux <branch-name> [--base <branch>]
launch-workmux --auto-name [--issue <n>] [--base <branch>]
```

`--issue` requires `--auto-name` and must match `^[0-9]+$`, so `#42` and leading zeros are rejected before anything runs.

Flow when `--auto-name` is given, inside `do_launch`:

1. Write the escaped prompt file first, as today, so empty stdin fails before the generator runs. The branch name is unknown at `mktemp` time, so use a provisional `safe_name` of `issue-<n>` or `auto-name` for that template only.
1. With `--issue <n>`, look for an existing local branch before generating:

   ```bash
   git for-each-ref --format='%(refname:short)' refs/heads/ 2>/dev/null || true
   ```

   Match `^([^/]+/)?<n>(-|$)`. On exactly one match, reuse it and print `Reusing branch <name> for issue <n>`. On more than one, print the candidates and exit non-zero rather than guessing which worktree to reopen. This is what makes a rerun of `/create-worktree 42` reopen the existing worktree despite the generator being non-deterministic.

1. Otherwise generate:

   ```bash
   workmux add -A -P "${prompt_file}" --dry-run < /dev/null
   ```

   Pass neither `--base` nor `--open-if-exists`: neither affects the name, and a `--base` that is not present locally fails the dry run. The `< /dev/null` redirect is required, because workmux treats readable stdin as multi-worktree mode.

1. Parse the name from stdout. workmux prints two matching lines, `  Branch: <name>` from the generator and `Branch:   <name>` from the dry-run summary, so take the last line matching `^[[:space:]]*Branch:[[:space:]]+(.+)$`. Keep the pattern in a variable for `[[ =~ ]]`, and avoid `${x,,}`, `mapfile`, and `declare -A`, since macOS ships Bash 3.2.
1. Normalize and insert the number. Trim trailing whitespace and `\r`, lowercase with `tr`, split on the first `/` only, and replace any remaining `/` in the slug with `-`. Strip a leading `issue-<n>-`, `issue<n>-`, or `<n>-` the generator may already have produced, and a trailing `-issue-<n>`. Do not strip a bare trailing `-<n>`: for issue 3 that would turn `migrate-to-python-3` into `3-migrate-to-python`. Rebuild as `<prefix>/<n>-<slug>`, or `<n>-<slug>` with no prefix, falling back to `<prefix>/<n>` if the slug empties. Exit non-zero on an empty result.
1. Print one line, `Generated branch name: <name>`, then compute the real `safe_name`, call `worktree_path_for_branch`, and continue into the existing backgrounded launch path unchanged.

Generation runs in the foreground before the detached launch. On failure, remove the prompt file, print workmux's stderr, and exit non-zero. Use the script's existing `set +e; …; status=$?; set -e` idiom around every capture, because a `grep` in a command substitution under `set -euo pipefail` exits the script silently and strands the temp file.

The real `workmux add` still runs without `-A`, so it makes no second LLM call, and `auto_name.background` no longer applies to it.

### 2. Test fixtures

- `tests/fixtures/workmux-stub`: parsing currently assumes `add <branch>` and dies on any unknown argument, so it misreads `add -A --dry-run`. Make the positional branch optional, accept `-A` and `--dry-run`, and on a dry run print `  Branch: ${STUB_AUTO_NAME}` followed by the summary block and exit 0. Add `STUB_AUTO_NAME_FAIL=1` to write an error to stderr and exit 1. Record the naming input under `${STUB_STATE}/auto_name_input`, leaving `prompt_path` for the real invocation.
- `tests/fixtures/git-worktree-stub`: it dies on anything but `worktree list --porcelain`. Add a `for-each-ref` branch printing `STUB_GIT_BRANCHES` one entry per line. No conflict with `worktree_path_for_branch`, which already tolerates stub failures.

### 3. Test coverage

Add `STUB_AUTO_NAME`, `STUB_AUTO_NAME_FAIL`, and `STUB_GIT_BRANCHES` to `SCRUT_UNSET` in the `Makefile`. No new `SCRUT_ENV` entries are needed, since no new binary is involved.

New testcases in `tests/scrut/launch-workmux.md`:

- a generated name with a prefix, with and without `--issue`
- a bare generated name, which stays bare
- a generated name that already carries `issue-42-`, normalized to one number
- reuse of an existing branch, asserting no `auto_name_input` file was written
- ambiguous reuse, asserting the candidates and a non-zero exit
- generator failure, asserting stderr, exit code, and prompt-file cleanup
- `--issue` without `--auto-name`, and a non-numeric `--issue`
- an auto-name variant of the empty-stdin cleanup case, using the provisional glob

### 4. Skill bodies

Both `SKILL.md` files lose the naming algorithm from their main path and gain a fallback section.

- `plugins/create-worktree/skills/create-worktree/SKILL.md`, step 2 and step 4: the issue path calls `launch-workmux --auto-name --issue NUMBER --base BASE_BRANCH`, the description path calls `launch-workmux --auto-name --base BASE_BRANCH`, and an explicit `type/slug` argument keeps the positional form. Step 3 currently embeds `Branch: [BRANCH_NAME]` in the description prompt; drop that line, since the name does not exist yet.
- `plugins/address-issue-in-worktree/skills/address-issue-in-worktree/SKILL.md`, step 3 becomes the same call with `--issue NUMBER`.
- Keep today's slugify rules in both files, moved under a "If the generator is unavailable" heading: when the launcher exits non-zero reporting a generation failure, build `TYPE/N-SLUG` by those rules and re-run with the positional form. This is the only remaining use of label-derived `TYPE`.
- Both "Report Success" sections read the branch from the launcher's `Generated branch name:` or `Reusing branch` line rather than from a name the model computed. `create-worktree`'s error-handling bullet about `--open-if-exists` gains the reuse case.

### 5. Documentation

- `plugins/create-worktree/README.md` and `plugins/address-issue-in-worktree/README.md`: replace the title-derived slug descriptions with the generator contract, and state the requirement that workmux can reach a naming command (an agent profile, `auto_name.command`, or the `llm` CLI). Add the recommended `auto_name.system_prompt` snippet for users who want type prefixes.
- `plugins/use-git/skills/use-git/references/common-operations.md` line 98 says `feature/` is "what the create-worktree and address-issue-in-worktree skills emit". Reword: the prefix now comes from the user's workmux naming prompt, and the skills preserve whatever it returns.
- Root `README.md`: the two table rows mirror `marketplace.json` descriptions verbatim, so they change only if those descriptions change. The `**External tools:**` bullets stay accurate.

### 6. Versions and mirrors

Minor bump for both plugins, since the naming behavior changes: `create-worktree` to `1.3.0`, `address-issue-in-worktree` to `2.1.0`. Update each `plugin.json` and its `.claude-plugin/marketplace.json` entry, recompute `metadata.version` with `bin/compute-catalog-state`, then regenerate both mirrors with `bin/build-codex-marketplace` and `bin/build-opencode-mirror`.

## Verification

```bash
make test-all
```

Then confirm the byte-identical copies and the cross-reference rules still hold, which `make validate` covers via rules 18 and 19.

End-to-end, against a real issue in this repository:

1. `/create-worktree 42` produces a worktree whose branch leads with `42-` after any prefix, and the launcher reports the generated name.
1. Rerunning `/create-worktree 42` reports `Reusing branch` and reopens the same worktree instead of generating a second name.
1. `/create-worktree Fix the login page` produces a name with no number.
1. `/address-issue-in-worktree 42` produces the same shape, and the new session's `.workmux/PROMPT-*.md` ends with `/address-issue 42`.
1. Temporarily renaming the naming command out of reach makes the launcher exit non-zero with workmux's error, leaving no stray file under `/tmp/workmux-prompt-*`.

Check `~/.local/state/workmux/workmux.log` for the `resolved auto-name command` line to confirm which generator ran.

## Note on this machine's configuration

`~/.config/workmux/config.yaml` sets `auto_name.model: "gemini:gemini-2.0-flash-lite"`, but that field applies only to the `llm` CLI path. With `agent: claude` and no `auto_name.command`, workmux resolves the Claude profile, and the log confirms `effective_command="claude --model haiku -p"`. The `llm` wrapper at `/Users/ctm/Development/workmux-llm-wrapper/bin/llm` is not on `PATH`, and would be bypassed even if it were. Setting `auto_name.command: "llm"` would restore it. This is configuration, not a code change, and is out of scope here.
