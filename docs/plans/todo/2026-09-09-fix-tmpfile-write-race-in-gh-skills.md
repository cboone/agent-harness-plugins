# Fix the tmpfile + Write + `gh --body-file` race in gh-facing skills

Addresses [#309](https://github.com/cboone/agent-harness-plugins/issues/309).

## Context

Five plugins tell the agent to build long `gh` payloads with the same three-step pattern: run `mktemp` to get a path, populate it with the **Write** tool, then pass it via `--body-file` / `--notes-file`. The pattern has two defects that have repeatedly produced PRs and issues with **empty bodies**, which the user then has to notice and ask the agent to repair.

**Failure mode A — `mktemp` creates the file, so `Write` errors.** `mktemp /tmp/pr-body-XXXXXX` creates a real (empty) file at the path it prints. The Write tool refuses to overwrite an existing file the agent has not Read first, so the Write fails with `File has not been read yet`. The agent has no reason to Read a file it just created empty, so it either bolts on a counterintuitive Read or retries into a racy state.

**Failure mode B — `Write` and the `gh` call get batched in parallel.** The harness actively encourages issuing independent tool calls in one message, and `plugins/use-git/skills/use-git/SKILL.md:24` states that preference as a core principle. The skills present Write and `gh pr create` as two unordered calls, so the agent batches them. `gh` reads the body file at invocation time, so it can run before Write lands (or after Write failed per mode A) and open the PR with a zero-byte body.

These two are not independent calls, and the skills never say so. The fix makes the dependency explicit, removes the file-creation conflict, and adds a post-creation check so the remaining silent failure becomes self-healing.

**Intended outcome:** invoking `/pr` or `/create-issue` reliably produces a fully populated body, with no Write-tool error and no manual `gh pr edit` repair.

## Approach

Adopt this corrected five-step pattern everywhere the tmpfile convention appears:

```text
1. mktemp -u /tmp/<prefix>-XXXXXX     # unique path, nothing created on disk
2. Write TMPFILE                       # its own message
3. gh ... --body-file TMPFILE          # its own message, strictly after step 2
4. verify the stored body is non-empty; recover via `gh ... edit --body-file` if not
5. rm -f TMPFILE                       # separate Bash call, always last
```

`mktemp -u` is portable for this purpose: BSD/macOS creates then unlinks, GNU only prints a name. Both leave nothing on disk, so Write creates the file fresh and its "must Read first" precondition never applies.

Per the scope decision, steps 1, 2, 3, and 5 apply to all five plugins; step 4 (verify and recover) applies only to `pr` and `create-issue`, where an empty body is directly user-visible.

## Changes

### 1. `plugins/use-git` — the canonical reference (patch: 1.1.4 → 1.1.5)

`skills/use-git/references/tmpfile-pattern.md` is the source of truth that the other four skills cross-reference by path. Fix it first, then make the others consistent with it.

- Step 1 (L16-23): change `mktemp /tmp/gh-pr-body-XXXXXX` to `mktemp -u /tmp/gh-pr-body-XXXXXX`; update the `# Returns` comment to state the path does **not** exist on disk. Add a short paragraph explaining why `-u` is required (the Write tool's read-before-overwrite precondition) and noting the BSD/GNU difference. Keep the existing macOS trailing-`X` guidance.
- Add a new section, **Never batch the Write with the command**, between steps 2 and 3: the Write call and the `gh` call must go in separate, sequential messages. State the consequence (`gh` reads the file at invocation time; a parallel batch yields an empty body) and frame it explicitly as an exception to the general parallel-tool-call preference, because these calls are *not* independent.
- Update the three worked examples (L61, L78, L95) to `mktemp -u`.
- Leave the existing zsh `status` cleanup rationale (L37-54) and the anti-patterns section (L101-131) unchanged.

`skills/use-git/SKILL.md:24` states core principle #6, *"Parallel tool calls over chained commands"*. Add a one-clause carve-out so this principle stops licensing failure mode B: independent commands may be parallelized, but a Write feeding a `--body-file` call is a dependency and must be sequential. Cross-reference the new section in `tmpfile-pattern.md`.

### 2. `plugins/pr` (minor: 1.5.5 → 1.6.0)

`skills/pr/SKILL.md`, the "Create the PR" subsection (L268-293):

- L270-275: `mktemp -u /tmp/pr-body-XXXXXX`, with the corrected `# Returns` comment.
- L277-283: add the explicit sequencing directive before `gh pr create`, in the terms above.
- Insert a new **Verify the PR body** block after `gh pr create` and **before** cleanup:

  ```bash
  gh pr view <pr-number> --json body --jq '.body | length'
  ```

  If the length is `0`, re-Write the tmpfile and recover with `gh pr edit <pr-number> --body-file TMPFILE`.

- L287-293: keep the separate-Bash-call cleanup and its zsh rationale verbatim, but state that cleanup must come **after** verification, since recovery needs the file to still exist.

`README.md:32` — the recommended permission allowlist. `Bash(mktemp /tmp/pr-body-*)` will no longer match once the command gains `-u`, so replace it with `Bash(mktemp -u /tmp/pr-body-*)` and add `Bash(gh pr edit *)` for the recovery path. `Bash(gh pr view *)` is already present.

### 3. `plugins/create-issue` (minor: 1.0.5 → 1.1.0)

`skills/create-issue/SKILL.md`, steps 3-5 (L40-79): same treatment as `pr`. `mktemp -u /tmp/gh-issue-body-XXXXXX`, the sequencing directive before `gh issue create`, and a verification block using `gh issue view <n> --json body --jq '.body | length'` with `gh issue edit <n> --body-file TMPFILE` recovery, placed before cleanup.

`README.md:37` — replace `Bash(mktemp /tmp/gh-issue-body-*)` with the `-u` form and add `Bash(gh issue view *)` and `Bash(gh issue edit *)`.

### 4. `plugins/release` (patch: 1.5.10 → 1.5.11)

`skills/release/SKILL.md:886-895`: `mktemp -u /tmp/gh-release-notes-XXXXXX` plus the sequencing directive before `gh release create ... --notes-file TMPFILE`. No verification step. Add the missing `# Returns` comment for consistency with the other skills.

`README.md:41`: replace `Bash(mktemp /tmp/gh-release-notes-*)` with the `-u` form.

### 5. `plugins/resolve-copilot-pr-feedback` (patch: 1.4.4 → 1.4.5)

`skills/resolve-copilot-pr-feedback/SKILL.md` has three call sites:

- L196-208 (reply bodies, `mktemp /tmp/copilot-reply-XXXXXX`)
- L375-383 (summary comment, `mktemp /tmp/copilot-summary-XXXXXX`)
- L398 (Reply Templates prose)

Change all three to `mktemp -u` and add the sequencing directive to the numbered `# Step N` blocks, which already have a natural place for it between Step 2 (Write) and Step 3 (post). No verification step.

`README.md:29`: replace both `Bash(mktemp /tmp/copilot-reply-*)` and `Bash(mktemp /tmp/copilot-summary-*)` with their `-u` forms.

### 6. Regenerate mirrors and recompute catalog state

`dist/codex/` holds real transformed copies and CI fails on drift (`bin/validate-plugins` §16 diffs a fresh rebuild against the committed tree). Run `bin/build-codex-marketplace` and commit the result. `dist/opencode/` is relative symlinks into `plugins/`, so it needs no action; run `bin/build-opencode-mirror` anyway to confirm it stays clean.

Update each `plugin.json` version and its matching `.claude-plugin/marketplace.json` entry (`bin/validate-plugins` §8 fails if they diverge), then recompute `metadata.version` with `bin/compute-catalog-state`. From `catalog-M63-m79-p147-n51`, the two minor bumps (each zeroing a patch component) and three patch bumps give an expected `catalog-M63-m81-p140-n51`. Take the script's output as authoritative rather than this arithmetic.

## Out of scope

Found during exploration, worth separate issues rather than widening this change:

- `plugins/set-up-installers/skills/set-up-installers/SKILL.md:204-211` uses a shell-variable `mktemp` with `trap ... EXIT` and writes the body inside the same shell invocation. The Write-tool precondition never applies, so it is not affected by this bug, though it does diverge from the repo-standard convention.
- `plugins/release/skills/release/SKILL.md:602-604` references `TMPFILE` in the catalog-state release path with no `mktemp` line binding it. A real ambiguity, but a different defect.
- `plugins/scaffold-go-cli/skills/scaffold-go-cli/SKILL.md:242` passes a long multiline inline `--body`, which `tmpfile-pattern.md:114` labels an anti-pattern.
- `mktemp -d` guidance in the scrut/bash/zsh style skills is unrelated to this pattern.

## Verification

1. **Confirm the `-u` premise on this machine**, since the whole fix rests on it:

   ```bash
   p="$(mktemp -u /tmp/pr-body-XXXXXX)"; echo "${p}"; test -e "${p}" && echo "EXISTS (fix invalid)" || echo "absent (correct)"
   ```

1. **Repo validation**, all of which CI also runs:

   ```bash
   yarn lint
   bin/validate-plugins
   bin/validate-json
   ```

1. **Mirror freshness** — must produce no diff after the regeneration commit:

   ```bash
   bin/build-codex-marketplace && bin/build-opencode-mirror && git diff --exit-code dist/ .agents/
   ```

1. **Catalog state matches**:

   ```bash
   bin/compute-catalog-state
   grep -o 'catalog-[A-Za-z0-9-]*' .claude-plugin/marketplace.json
   ```

1. **End-to-end, on this branch.** This branch's own PR is the live test: invoke `/pr` after installing the updated plugin, then confirm the body actually landed rather than trusting the URL:

   ```bash
   gh pr view --json body --jq '.body | length'
   ```

   A non-zero length with no intervening `gh pr edit` means both failure modes are closed. Watch the transcript to confirm the agent issued Write and `gh pr create` in separate messages and hit no `File has not been read yet` error.

1. **Regression check on permissions.** After the allowlist edits, confirm `mktemp -u /tmp/pr-body-XXXXXX` does not trigger a fresh permission prompt for a user who copied the README's recommended `allow` list.
