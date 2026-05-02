# Safety Rules

Conventions that prevent data loss, protect shared repositories, and keep Claude Code running smoothly.

## GPG Sign Every Commit

Always use `git commit -S` to GPG-sign commits. The sandbox cannot access GPG keys, so resort immediately to the unsandboxed Bash command when committing.

```bash
git commit -S -m "$(
  cat << 'EOF'
feat: add user authentication
EOF
)"
```

## Never Amend

Always create new commits. Never use `git commit --amend`.

**Why:** When a pre-commit hook fails, the commit did not happen. Running `--amend` after a hook failure would modify the previous (unrelated) commit, potentially destroying work or losing changes. After a hook failure, fix the issue, re-stage, and create a new commit.

## Never Use Force or Override Flags

Never use these flags without explicit user instruction:

- `git push --force` / `git push -f`
- `--no-verify`
- `--force` on other git commands
- Any flag that bypasses safety checks

**When the user explicitly requests a force push**, use the safer alternative:

```bash
# --force-if-includes requires Git 2.30+; omit it on older versions
git push --force-with-lease --force-if-includes
```

`--force-with-lease` protects against overwriting commits that others have pushed since your last fetch. `--force-if-includes` adds an extra check that your local ref includes the remote tip, but is only available in Git 2.30 and later. If the command fails on an older Git, fall back to `--force-with-lease` alone.

**When a push is rejected**, suggest rebasing instead of forcing:

```bash
git pull --rebase
```

**When a hook fails**, investigate the root cause and fix it rather than bypassing with `--no-verify`.

## Exclude Secret Files from Staging

Never stage files that likely contain secrets. Watch for these patterns:

- `.env`, `.env.local`, `.env.production`
- `credentials.json`, `service-account.json`
- `*.pem`, `*.key`, `*.p12`, `*.pfx`
- `*secret*`, `*token*` (in filenames)
- `.npmrc` with auth tokens
- `id_rsa`, `id_ed25519` (SSH keys)

When these files appear in `git status`, warn the user and exclude them from staging. Stage specific files by name rather than using `git add -A` or `git add .`.

## Parallel Tool Calls over Chained Commands

Use separate Bash tool calls for independent commands instead of chaining with `;` or `&&`.

**Why:** Chained compound commands trigger Claude Code permission prompts, even when each individual command is allowlisted. Separate tool calls run without extra prompts.

**Good:**

Run `git status` and `git diff` as two separate, parallel Bash tool calls.

**Bad:**

```bash
# Triggers a permission prompt because it looks like a compound command
git status && git diff
```

**Exception:** Commands that genuinely depend on each other (where the second must only run if the first succeeds) can be chained. But prefer separate sequential tool calls even then, since the tool framework handles sequencing naturally.
