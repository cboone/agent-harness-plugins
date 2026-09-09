# Fix script-locating globs in skills (#323, #326)

## Context

Issues [#323](https://github.com/cboone/agent-harness-plugins/issues/323) and [#326](https://github.com/cboone/agent-harness-plugins/issues/326) report the same defect from two angles. Three skills tell the agent to find their bundled helper script with a glob shaped `**/<plugin-name>/scripts/<script>`. That shape describes this repository's layout, not the installed layout: the plugin cache interposes a version directory, so the installed copy is at `<plugin>/<version>/scripts/<script>` and the documented glob cannot reach it.

The glob does not fail loudly. It silently resolves to some other copy on disk (a marketplace checkout, a `dist/codex/` build artifact, or a stale `.bak` directory), and the agent has nothing to prefer among them. The copies happen to be byte-identical today, so the bug is latent. It stops being latent as soon as a script changes between the marketplace `HEAD` and the released version, which is the normal state mid-development, or on a machine with no marketplace checkout at all, where the glob matches nothing and `resolve-copilot-pr-feedback` has no fallback for any of its GraphQL operations.

Both issues propose `${CLAUDE_PLUGIN_ROOT}`. That is the right fix, and it was verified against Claude Code 2.1.266 rather than assumed. The mechanism is worth stating precisely because it is easy to get wrong:

- `CLAUDE_PLUGIN_ROOT` is **not** a shell environment variable during skill execution. `env | grep CLAUDE_PLUGIN_ROOT` inside the Bash tool returns nothing. The archived plan `docs/plans/done/extract-copilot-graphql-into-script.md:49` records this correctly, and it is why the glob workaround was written in the first place.
- The variable **is** substituted as **prompt text** when a plugin skill loads. The loader runs a global replace over the SKILL.md body before it reaches the model, so the agent sees an already-absolute, already-versioned path and never needs the shell variable. Confirmed by loading `plugin-dev:plugin-structure`, whose body contains the literal: every occurrence arrived expanded to `/Users/…/plugin-dev/517b2fcd1b60`, including occurrences inside fenced code blocks.

The earlier conclusion recorded in the archived plan was literally true but drew the wrong lesson from it: the substitution happens one layer above the shell, so the glob was never necessary.

Two consequences follow, and both are in scope:

1. Substitution is unconditional and global, so a SKILL.md **cannot document the literal variable**. `plugins/create-plugin/skills/create-plugin/SKILL.md` currently has its own guidance corrupted into an absolute path on every load (5 occurrences). This was found while investigating and is not mentioned in either issue.
2. Nothing in CI checks that a script referenced by a skill actually exists, which is why this rotted silently. `bin/validate-plugins` runs 17 checks, none of which look at script references.

## Root cause summary

| Layer                   | `${CLAUDE_PLUGIN_ROOT}` available? | Evidence                                                                   |
| ----------------------- | ---------------------------------- | -------------------------------------------------------------------------- |
| `hooks.json` command    | Yes, substituted by hooks system   | `plugins/notify/hooks/hooks.json:7` works today                            |
| `.mcp.json` server args | Yes, substituted by MCP loader     | Official plugin docs                                                       |
| SKILL.md body text      | Yes, substituted at skill load     | Verified live via `plugin-dev:plugin-structure`                            |
| Bash tool shell env     | No                                 | `env` shows it unset during skill execution                                |
| `references/*.md`       | No, read as a plain file           | Literals survive, which makes them the safe place to document the variable |

## Changes

### 1. Rewrite the locator in the three affected skills

Files:

- `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md:34-40`
- `plugins/create-worktree/skills/create-worktree/SKILL.md:56,58`
- `plugins/create-worktree-from-issue/skills/create-worktree-from-issue/SKILL.md:100,102`

Replace the "locate the script by searching for …" paragraph and its companion placeholder paragraph with a direct path. Keep the `bash "<quoted path>"` invocation form: it is what preserves the existing `Bash(bash …)` allowlist rules, and it keeps the command token stable across versions.

Pattern to apply, adapted per plugin and script name:

````markdown
The script ships with this plugin. Invoke it via `bash` followed by the quoted path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" fetch OWNER REPO PR_NUMBER
```

Claude Code replaces the plugin-root placeholder with the installed plugin's absolute,
version-correct directory before this file reaches you, so there is no search step. Keeping
`bash` as the command prefix keeps the command token stable across plugin versions, which is
what permission allowlist rules match on.

**If the path was not substituted:** the path will still begin with `$` rather than `/`. Codex
CLI substitutes the placeholder only in hook commands, and OpenCode does not substitute it at
all. In that case locate the script with `**/resolve-copilot-pr-feedback/**/scripts/resolve-copilot-threads`,
prefer a match inside the harness's own installed-plugin directory, ignore any match under a
`.bak` or other backup directory, confirm it with `test -x`, and use that absolute path for the
rest of the session.
````

Two constraints on the wording:

- **Do not write the literal variable name in prose.** It would be substituted along with everything else and the fallback sentence would become nonsense. Describe the failure structurally instead ("the path will still begin with `$` rather than `/`"). The literal is safe only inside the code fence, where substitution is exactly what is wanted.
- The fallback glob must use `**/<plugin>/**/scripts/<script>`, with `**` between the plugin name and `scripts`, so it tolerates the version segment.

In `resolve-copilot-pr-feedback/SKILL.md`, the placeholder token `resolve-copilot-threads` is reused unquoted at lines 60, 137, 180, 204, 207, 228, and 285. Leave those as the short placeholder but make the sentence introducing it point at the quoted path form above.

### 2. Fix the convention doc that propagated the bug

`plugins/create-plugin/skills/create-plugin/references/scripts.md:134-147` is the source of the pattern. Its "Skill Integration" section currently instructs:

> 1. Locate the script path at the start of the session (e.g., by globbing for `**/plugin-name/scripts/script-name`)

Rewrite the section to teach the substituted-path form, keep the existing and correct rationale for the `bash` prefix (permission allowlist token stability), and add a short note that the variable is substituted in SKILL.md bodies but is not a shell variable. This file is a reference, read from disk, so literals are safe here.

Also correct the inconsistency the section already carries: line 142 recommends `Bash(bash:*)` while every plugin README ships a narrower `Bash(bash */script-name *)`. Make the doc describe the narrow form the READMEs actually use.

### 3. Stop `create-plugin`'s SKILL.md from corrupting itself

`plugins/create-plugin/skills/create-plugin/SKILL.md` lines 117, 125, 148, 200, and 203 contain the literal variable and are rewritten into an absolute path on every load.

Move the exact spelling into the reference files, which already carry it safely (`references/command-md.md:75-81`, `references/hooks-json.md:61-65`, `references/scripts.md:123-127`). In SKILL.md, refer to it by name without the `${…}` syntax, for example "reference scripts via the plugin-root placeholder documented in `./references/scripts.md`". Line 125 (`Use ${CLAUDE_PLUGIN_ROOT} to reference scripts`) should also be scoped: it currently reads as universal advice, but the substituted-path form and the hook form differ.

### 4. Add a CI guard to `bin/validate-plugins`

Add a section 18 before the `# ─── Summary ───` block, following the existing flat, numbered `for dir in plugins/*/` style. Invoke the `write-bash-scripts` skill before editing.

Two assertions over `plugins/*/skills/*/SKILL.md` only (not `references/`, which legitimately contains examples):

1. Every `${CLAUDE_PLUGIN_ROOT}/scripts/<name>` reference resolves to an existing, executable `plugins/<plugin>/scripts/<name>`.
2. No SKILL.md contains a version-blind locator glob. Match `\*\*/[a-z0-9-]+/scripts/` and reject it; the corrected `**/<plugin>/**/scripts/` form does not match this pattern, so the new fallback text passes.

### 5. Correct the permission examples in the three plugin READMEs

`plugins/*/README.md` ship rules such as `Bash(bash */launch-workmux *)`. Claude Code's documented matcher "match[es] the whole command text, with `*` standing in for any text", and the skills instruct a **quoted** path, so the actual command text is `bash "/abs/…/launch-workmux" "branch"`. The trailing `*` in the rule expects a space immediately after the script name, but the next character is a closing quote, so these rules appear not to match what the skills actually run.

Verify this against a live permission prompt first. If confirmed, update to a quote-tolerant form, for example `Bash(bash "*/launch-workmux" *)` and `Bash(bash "*/compose-issue-prompt")`, in:

- `plugins/resolve-copilot-pr-feedback/README.md:29`
- `plugins/create-worktree/README.md:33`
- `plugins/create-worktree-from-issue/README.md:33`

If it turns out the matcher normalizes quotes, leave the rules alone and note the finding in the PR description.

### 6. Minor: correct a stale README claim

`README.md:211` states that skills use the `@${CLAUDE_PLUGIN_ROOT}/references/…` inclusion pattern and lists eight affected skills. No SKILL.md in `plugins/` uses that pattern; they all use relative `./references/…` paths resolved against the injected skill base directory. Correct or remove the claim while touching this area.

### 7. Versions and generated mirrors

Patch bumps (bug fix in prompt text, per `CLAUDE.md`), in both `plugin.json` and `.claude-plugin/marketplace.json`:

| Plugin                        | From  | To    |
| ----------------------------- | ----- | ----- |
| `create-plugin`               | 1.2.7 | 1.2.8 |
| `create-worktree`             | 1.1.3 | 1.1.4 |
| `create-worktree-from-issue`  | 1.3.4 | 1.3.5 |
| `resolve-copilot-pr-feedback` | 1.4.4 | 1.4.5 |

Catalog state goes from `catalog-M63-m79-p147-n51` to `catalog-M63-m79-p151-n51` (four patch bumps). Recompute with `bin/compute-catalog-state` rather than by hand.

Then regenerate and commit both mirrors:

```bash
bin/build-codex-marketplace
bin/build-opencode-mirror
```

`dist/codex/` holds real copies of these SKILL.md bodies, so every edit above needs a rebuild; `dist/opencode/` is symlinks and needs no rebuild for prose, but CI runs it anyway and asserts `git diff --exit-code dist/`.

## Verification

```bash
# 1. Structural validation, including the new section 18 guard.
bin/validate-plugins
bin/validate-json
bin/version-audit

# 2. Mirrors are current (this is what CI enforces).
bin/build-codex-marketplace && bin/build-opencode-mirror && git diff --exit-code dist/ .agents/

# 3. Shell and Markdown lint.
shellcheck -S warning bin/* plugins/*/scripts/* tests/fixtures/*
shfmt -d bin/* plugins/*/scripts/* tests/fixtures/*
yarn lint

# 4. Existing script behavior is unchanged.
make test-scrut
```

Negative test for the new guard: temporarily point a SKILL.md at a nonexistent script, confirm `bin/validate-plugins` fails, then revert. Do the same with a `**/<plugin>/scripts/<script>` glob to confirm the second assertion fires.

End-to-end check that the actual defect is fixed, which the static checks cannot cover:

1. Install or update the local marketplace so the cache holds the new versions.
2. In a fresh session, run `/resolve-copilot-pr-feedback` against a PR and confirm the first script invocation uses a path under `plugins/cache/…/<version>/scripts/` with no `find` or glob step beforehand.
3. Confirm the same for `/create-worktree` and `/create-worktree-from-issue`, whose `launch-workmux` invocation is the one that would fail most visibly.
4. Confirm `create-plugin`'s SKILL.md no longer renders an absolute path where it means to name the placeholder.

## Out of scope

- Moving `scripts/` to `bin/`. Claude Code does add every enabled plugin's `<plugin-root>/bin` to the Bash tool's `PATH` (verified in this session, and documented in the official plugins guide), which would remove the locating step entirely and give a stable bare-name command token. It is rejected here because it breaks every existing user's `Bash(bash …)` allowlist rules, has no equivalent in Codex CLI or OpenCode, cannot be shipped by plugins distributed through claude.ai organization settings, and would touch the CI globs, `Makefile` script-path variables, and scrut fixtures. Worth a separate issue.
- Adding scrut coverage for `resolve-copilot-threads`, which currently has none while the two worktree scripts do.
