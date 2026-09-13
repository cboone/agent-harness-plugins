# create-worktree: record and respect an exclusive-resource claim

Addresses [#357](https://github.com/cboone/agent-harness-plugins/issues/357).

## Context

Some work cannot run in parallel across worktrees because it needs an exclusive resource: a DAW, a simulator, a device, a database, a port, a shared install location. Nothing records which worktree currently holds one, so the constraint lives in the user's head and has to be restated. In the fosforo transcripts the same sentence was sent three times, growing each time, and the questions it was meant to answer ("are there any open issues that can be done in parallel with the other work?") went unanswered because no skill had anything to read.

The consequence is concrete rather than theoretical. fosforo installs its plugin to a single shared location, so a second worktree installing over the first silently invalidates the first's verification run.

Three facts about the current code shape the design:

1. Neither `plugins/create-worktree/skills/create-worktree/SKILL.md` nor `plugins/address-issue-in-worktree/skills/address-issue-in-worktree/SKILL.md` ever computes a worktree path. Both delegate placement entirely to `workmux add` and then verify with `git worktree list`. There is no existing seam that knows where a worktree landed except that verification step.
1. No plugin in this repository reads or writes any state file under a project's `.claude/`. This introduces the first one, so it sets the precedent.
1. `plugins/suggest-next-issue/skills/suggest-next-issue/SKILL.md` step 2 treats worktrees purely as an exclusion signal (an issue is in progress if a branch or worktree names it). It has no notion that two issues that are both free might still conflict with each other.

The issue is explicit that this is advisory, not a lock: it should make the constraint visible, not enforce it, "because a user who wants to override always has a reason."

Note that the issue names `create-worktree-from-issue`, which was renamed to `address-issue-in-worktree` by `docs/plans/done/2026-09-10-gate-issue-skills-on-plan-approval.md`. That is the skill meant.

## Design decisions

- **The claim file is `<main worktree>/.claude/worktree-resources.local.json`.** Worktrees do not share a working tree, so the path is resolved from the first record of `git worktree list --porcelain`, which is always the main worktree. The `.local.json` suffix matches the existing `settings.local.json` convention, which already signals "personal, gitignored", so the intent is legible without a comment. Storing it inside `.git/` was rejected: it would be shared by construction and impossible to commit by accident, but it is invisible to a working-tree grep, and greppability is half of what the issue asks for.

- **One new bundled script, `manage-resource-claims`, owns all reading and writing.** Doing the JSON surgery in skill prose would put `jq` pipelines in a Markdown file that no test can reach. A script gets shellcheck, shfmt, and scrut coverage for free, matching how `compose-issue-prompt` and `launch-workmux` are already handled.

- **`suggest-next-issue` reads the file directly instead of shipping a third copy of the script.** Rule 18 of `bin/validate-plugins` requires every `${CLAUDE_PLUGIN_ROOT}/scripts/NAME` reference to resolve inside its own plugin, so a reference from `suggest-next-issue` would force a third byte-identical copy plus a third `cmp` guard. That plugin only needs to read, and it already runs `git worktree list`, so it resolves the path in prose and opens the file with the Read tool. The cost is that the path-resolution rule is stated in two places; the benefit is one fewer duplicated script.

- **Staleness is derived, never stored.** A claim is stale when its `worktree` path is absent from `git worktree list --porcelain`. Nothing has to hook worktree removal, which neither skill performs (`workmux remove` and `workmux merge` do), and a claim can never outlive its worktree. `list` flags stale entries, `claim` drops a stale entry for the same resource as it writes, and `prune` clears them all.

- **`check` reports but does not mutate.** A read that silently rewrites the file would surprise anyone who ran it to look. Clearing happens on `claim` and on `prune`, both of which the user has asked for.

- **Writes are atomic (temp file plus `mv`) but not locked.** Two worktrees claiming at the same instant can still race. Building file locking would contradict "advisory, not a lock", but a half-written JSON file would break every reader, and atomic replacement costs one line.

- **The catalog descriptions do not change.** `--resource` is an option on the existing job, like `--base`, which is also absent from the description. Changing it would require the `marketplace.json` entry, the root README cell, and the plugin README's first paragraph to move in lockstep for no gain. The SKILL.md frontmatter `description` does gain the new trigger phrasing, because that is what drives skill activation in Claude Code.

## Changes

### 1. `plugins/create-worktree/scripts/manage-resource-claims` (new)

A Bash script following the conventions already established in `compose-issue-prompt`: `#!/usr/bin/env bash`, `set -euo pipefail`, `SCRIPT_NAME="$(basename "$0")"; readonly SCRIPT_NAME`, and `die() { echo "${SCRIPT_NAME}: ${1}" >&2; exit "${2:-1}"; }` so every error reads `manage-resource-claims: message` on stderr. `command -v jq` is checked after argument parsing so `--help` works without it.

Subcommands:

| Subcommand                                                    | Behavior                                                                            |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `list [--json]`                                               | One `key=value` line per claim, `stale=yes` on claims whose worktree is gone         |
| `check <resource>`                                            | Silent exit 0 when free; holder line and exit 3 when held; stale reported as free    |
| `claim <resource> --worktree PATH --branch NAME [--issue N]`  | Records the claim, replacing any stale claim on the same resource                    |
| `release <resource>` or `release --worktree PATH`             | Removes the named claim, or every claim held by one worktree                         |
| `prune`                                                       | Drops every stale claim and reports what it dropped                                  |
| `-h`, `--help`                                                | Usage                                                                                |

Exit codes: 0 success, 1 usage or environment error, 3 resource held. The distinct code is what lets the skill branch without parsing prose.

The claim file path comes from `WORKTREE_RESOURCES_FILE` when set, otherwise `<main worktree>/.claude/worktree-resources.local.json`, with the main worktree read from the first `worktree ` record of `git worktree list --porcelain`. The override exists so scrut can exercise the script against a temp file; it is why `SCRUT_UNSET` grows an entry.

A missing file means no claims, which is not an error. An unparseable file is an error rather than a silent reset, because overwriting a file the user may have hand-edited is worse than stopping.

Record shape, matching the issue's `{resource, worktree path, branch, timestamp}`:

```json
{
  "version": 1,
  "claims": [
    {
      "resource": "logic",
      "worktree": "/Users/ctm/Development/fosforo__worktrees/128-eq-curve",
      "branch": "feature/128-eq-curve",
      "issue": 128,
      "claimed_at": "2026-09-12T18:04:11Z"
    }
  ]
}
```

`issue` is omitted rather than null when absent. The top-level `version` exists so a later format change has something to branch on.

### 2. `plugins/address-issue-in-worktree/scripts/manage-resource-claims` (new)

A byte-identical copy, per the rule-18 constraint recorded in `AGENTS.md`. Change one and copy it to the other.

### 3. `plugins/create-worktree/skills/create-worktree/SKILL.md`

Frontmatter `description` gains resource phrasing so "claim the DAW" and "what holds the simulator" route here.

`## Options` gains three entries: `--resource <name>`, `--release-resource <name>`, `--list-resources`.

The workflow goes from five steps to seven. The two new ones, and the edits to the existing ones:

- **New step 1, "Handle a Claim-Only Request".** `--list-resources` and `--release-resource` short-circuit before any classification: run the script, report, stop. No worktree is created.
- Existing steps 1 and 2 become steps 2 and 3, unchanged.
- **New step 4, "Check the Resource Claim".** Skipped entirely when `--resource` is absent, which keeps the common path untouched. Otherwise: resolve the resource name against the project's declared list (step 4a below), run `check`, and on exit 3 report the holding branch, worktree, and timestamp and ask whether to proceed anyway. Proceeding is allowed, because the claim is advisory; the skill must not refuse. Placing this before prompt composition means a blocked claim stops before any work is done.
- **Step 4a, resolving the name.** Read whichever of `CLAUDE.md` and `AGENTS.md` exist in the repository root, and `copilot-instructions.md` under `.github/`, following the symlink target rather than treating it as a second source, plus any plan under `docs/plans/todo/`. Look for a heading containing "exclusive resource" and take the backticked names under it as the declared list. This copies the "consult project agent config" paragraph already used in `plugins/commit/skills/commit/SKILL.md` and `plugins/pr/skills/pr/SKILL.md`. Use the list to map a loose phrase ("the DAW") onto a declared name, and to note when a name is undeclared. Never refuse an undeclared name: the issue is explicit that the resource name is a free string with no registry.
- Existing steps 3 and 4 become steps 5 and 6. Step 6 gains a final paragraph: after `git worktree list` confirms the worktree, read its path from that output and run `claim` with the resource, path, branch, and issue number.
- Step 5 becomes step 7 and reports the claim alongside the branch and window name.
- `## Error Handling` gains two bullets: the resource is held and the user declined, and the claim file is unwritable (report it and continue, since the worktree exists and the claim is advisory).

Add a short note that the skill offers to add `.claude/worktree-resources.local.json` to the project's `.gitignore` when it creates the file and no entry covers it.

### 4. `plugins/address-issue-in-worktree/skills/address-issue-in-worktree/SKILL.md`

The same treatment, minus the claim-only flags, which live on `create-worktree` alone. `## Options` gains `--resource <name>` beside `--no-approval`.

Six steps become seven. The new "Check the Resource Claim" goes in as step 2, ahead of "Mark Issue In Progress", so a declined claim does not leave a self-assignment and an "in progress" label behind on an issue nobody started. Steps 2 through 6 shift down by one, and the new step 6 ("Create the Worktree") records the claim after `git worktree list` confirms the path, exactly as in `create-worktree`.

### 5. `plugins/suggest-next-issue/skills/suggest-next-issue/SKILL.md`

- `## Options` gains `--parallel-only`, which restricts recommendations to issues that need no held resource.
- Step 1 gains the claim read beside `git worktree list`: resolve `<main worktree>/.claude/worktree-resources.local.json` from the first record of `git worktree list --porcelain` and open it with the Read tool. A missing file means no claims. Cross-reference each claim's `worktree` against the `git worktree list` output already gathered to spot stale claims, and treat a stale claim as free.
- Step 1's closing line about reading the README and roadmap documentation extends to the project's declared exclusive-resource list, in the same places step 4a of `create-worktree` looks.
- Step 3's signal table gains a row: **Resource conflict**, sourced from the issue body and the project's resource declarations matched against held claims, weight High. An issue whose verification needs a held resource is not a good next pick even when everything else about it is.
- Step 4 gains a category, **Safe to Parallelize**, for issues that need no held resource, and the existing per-item "Blockers or considerations" field carries the holder when one applies.
- Step 5 gains a "who holds what" line per held resource: resource, branch, worktree, and whether the claim is stale.
- `## Example Output` is updated in lockstep, since it is a full worked example including the `**Already in progress:**` list.

### 6. `tests/scrut/manage-resource-claims.md` (new)

Covers both copies through `MANAGE_RESOURCE_CLAIMS_BIN` and `CREATE_WORKTREE_MANAGE_RESOURCE_CLAIMS_BIN`, following the paired-case style of `tests/scrut/launch-workmux.md`. Staleness cases drive `git worktree list --porcelain` through the existing `tests/fixtures/git-worktree-stub` and its `STUB_GIT_WORKTREE_PORCELAIN` variable; every other case sets `WORKTREE_RESOURCES_FILE` to a temp path.

Cases: claim then list; check on a free resource (silent, exit 0); check on a held resource (holder line, exit 3); two resources held at once; a claim whose worktree is gone is flagged `stale=yes` by `list` and reported free by `check`; `prune` drops it; `claim` replaces a stale claim on the same resource; `release <resource>`; `release --worktree PATH` clearing several at once; `list --json`; a missing file listing nothing; an unparseable file erroring; and the usage errors (unknown subcommand, missing resource name, `claim` without `--worktree` or `--branch`, unknown option, `--help` without jq on PATH).

### 7. `tests/scrut/repo-tooling.md`

A third `cmp` guard beside the two that already keep `compose-issue-prompt` and `launch-workmux` byte-identical across the two plugins.

### 8. Test wiring

- `Makefile`: `SCRUT_ENV` gains `MANAGE_RESOURCE_CLAIMS_BIN` (the `address-issue-in-worktree` copy) and `CREATE_WORKTREE_MANAGE_RESOURCE_CLAIMS_BIN` (the `create-worktree` copy), matching the existing naming convention for duplicated scripts. `SCRUT_UNSET` gains `-u WORKTREE_RESOURCES_FILE`, per the hand-maintained-list comment citing issue #330.
- `.github/workflows/ci.yml`: the same two entries in the `scrut-env` block, each value prefixed `./`, with no comment lines inside the block.

### 9. READMEs and repository docs

- `plugins/create-worktree/README.md`: the options table gains the three new flags; `## Requirements` notes that `jq` is also needed when `--resource` is passed, not only on the issue path; `## Recommended Permissions` gains `Bash(bash "*/manage-resource-claims" *)`; `## Examples` gains a claim-and-conflict example.
- `plugins/address-issue-in-worktree/README.md`: `--resource` in the usage section, the same permission rule, one example.
- `plugins/suggest-next-issue/README.md`: `--parallel-only` and a sentence on the claim read. No new permission rule, because the file is opened with the Read tool.
- Root `README.md`: the `_Create Worktree:_` external-tools bullet changes, since `jq` is now needed for `--resource` as well as for an issue number. The catalog table rows are untouched.
- `AGENTS.md`: the "Plugin layout" section says the two plugins ship byte-identical copies of "both scripts" and that "two testcases" guard them. Both become three. The `plugins/create-worktree/` tree and the sentence naming each script by its plugin-root path grow the new entry.
- `.gitignore`: add `.claude/worktree-resources.local.json`. This repository runs many worktrees and is a plausible user of the feature.

### 10. Versioning and generated trees

| Plugin                      | Version         | Reason                                    |
| --------------------------- | --------------- | ----------------------------------------- |
| `create-worktree`           | 1.2.4 -> 1.3.0  | New capability: claim, check, release     |
| `address-issue-in-worktree` | 2.0.3 -> 2.1.0  | New capability: claim and check           |
| `suggest-next-issue`        | 1.1.7 -> 1.2.0  | New capability: parallel-safety reasoning |

Each bump lands in both `plugins/<name>/.claude-plugin/plugin.json` and its `.claude-plugin/marketplace.json` entry, which rule 8 requires to match.

Recompute `metadata.version` with `bin/compute-catalog-state`. Expected `catalog-M65-m92-p155-n52` -> `catalog-M65-m95-p141-n52`: three minor bumps add 3, and patch components 4, 3, and 7 reset to 0. Take the script's output as authoritative rather than this arithmetic.

Regenerate both mirrors with `bin/build-codex-marketplace` and `bin/build-opencode-mirror` and commit the result. The new script appears under `dist/codex/plugins/{create-worktree,address-issue-in-worktree}/scripts/`; `dist/opencode/` is unaffected, since it symlinks only skill directories.

## Out of scope

- **Claims that span repositories.** A DAW or a simulator is a host-wide resource, not a per-repository one, so two projects can still collide. The issue scopes the file to one repository and this follows it. A host-wide store is a separate design.
- **Locking.** The issue rules it out directly.
- **Hooking worktree removal.** Derived staleness covers the requirement without one.
- **The gitignore templates in `scaffold-new-repo` and `refresh-project-scaffolding`.** They ship `.claude/settings.local.json` and would plausibly grow the new entry, but that is two more plugins and two more version bumps for something the skill already offers to do per project. Worth a follow-up issue.
- **`review-project-status` (#349) and `write-phased-build-plan` (#347).** Both are unwritten skills. They are named as consumers and will read the file this change creates.

## Verification

1. `make lint` passes, including shellcheck at default severity with the optional checks in `.shellcheckrc` and `shfmt -d` against `.editorconfig`.
1. `make validate` passes: rule 8 (version agreement), rule 9 (alphabetical order), rule 10 (catalog tag), rule 16 (generated-tree freshness), rule 17 (skill description length), rule 18 (the new script resolves and is executable in both plugins), rule 19 (cross-references).
1. `make test-scrut` passes, including the new suite and the third `cmp` guard.
1. `make test-all` passes as a whole.
1. `/check-versions` reports the three bumps and the catalog tag as consistent.
1. `bin/check-cross-references` run on its own reports nothing for the three edited `SKILL.md` files. `.claude/...` is not among the resolved prefixes, so the claim-file path needs no ignore comment; confirm that rather than assuming it.
1. End to end, by hand, in this repository:
   - `/create-worktree --list-resources` on a repository with no claim file reports no claims and creates nothing.
   - `/create-worktree 999 --resource logic` records a claim, and the file appears at the main worktree's `.claude/worktree-resources.local.json` with the worktree path that `git worktree list` reports.
   - A second `/create-worktree ... --resource logic` reports the holding branch, worktree, and timestamp, and asks rather than proceeding. Answering yes proceeds.
   - `workmux remove` on the holding worktree, then `/create-worktree --list-resources`, flags the claim stale; `--release-resource logic` clears it.
   - `/suggest-next-issue` lists the held resource and its holder, and `--parallel-only` drops any issue whose verification needs it.
