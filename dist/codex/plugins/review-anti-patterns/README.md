# Review Anti-Patterns

Review a branch or a fix diff against a checklist of defects that survive local review, with read-only reports by default and an explicit edit mode for supported fixes.

**Type:** Skill
**Trigger:** `/review-anti-patterns`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

A general review asks whether a change is right. This skill asks narrower questions that a general review tends to skip: what the sibling of each handled case is and whether it behaves the same way, which other places do the same job and whether they changed too, and which documents describe what just changed. Those questions come from a review of 132 pull requests in which most Copilot findings after the first round were a sibling input form, a parallel path, or a document that the previous fix had left behind.

The checklist has thirteen patterns, and each names the kinds of files it applies to: code, agent prose or docs, so a change touching only docs skips what cannot apply there. Agent prose, such as skills, prompts and agent instruction files, is reviewed as a program: rule order, branches that end nowhere, rules that conflict, and commands that the permission block does not cover. Where an item depends on how a platform behaves, the skill runs a read-only check such as `actionlint` or a validate-only flag, runs project tests and scripts only when you pass `--run-checks`, and reports anything it could not check as unverified rather than passed.

It runs through [Codex](https://github.com/openai/codex) when `codex` is installed and `--run-checks` is off: `codex exec` in a read-only sandbox with `approval_policy="never"` and `web_search="disabled"`, on `gpt-6.1-sol` at `high` effort with an 872k context window, set on the run so your own Codex settings never apply. Otherwise, including when started from a Codex session, or when its run fails a completion check (a non-zero exit, an empty reply, or a reply that does not match the result schema), it falls back to a fresh read-only subagent, then to the current session, and says which ran.

Without `--edit` it never edits. Both review phases in edit mode also stay read-only. On the `codex exec` path, the sandbox enforces that. Otherwise nothing but its instructions does, unless you run it somewhere that cannot write, and `--run-checks` lets project code run, which can write. On that path, the sandbox holds only with `approval_policy="never"`, which stops the run from asking to leave it. `web_search="disabled"` turns off Codex's web search, which the sandbox does not cover. Together they keep the run's commands and web search offline. MCP servers in your Codex configuration are not covered and can still reach the network. The report says which applied and lists anything a check left behind. It returns JSON whose findings have the same fields as [Review Until Clean](../review-until-clean/README.md)'s, each with the case that goes wrong and the evidence, plus whether the review covered the whole scope and what it left unverified. A plain-text report follows, naming the siblings examined for each finding, so a fix can cover the whole class at once.

It is built for your own changes in your own checkout: it trusts your git and SSH configuration and the repository's own tooling, and does not defend against a deliberately malicious diff. Review a contributor's pull request crafted to attack the reviewer with a sandboxed tool instead.

## Edit mode

`--edit` requires a clean working tree, including no staged, unstaged or untracked changes outside ignored files. Otherwise it refuses before review or fixes and asks you to commit or stash first; it does neither. This applies even to changes outside the selected range or paths. Report-only mode keeps its existing scope behavior.

Edit mode also cannot establish cleanliness for tracked files with assume-unchanged, skip-worktree or other nonordinary index flags. It refuses without changing those flags. Repositories with gitlinks are unsupported in edit mode, whether registered, embedded, initialized or not; the refusal names the path. Edit mode rechecks the precondition immediately after the initial capture.

`--edit` performs one initial read-only review, one supported fix pass at the selected severity, validation and one final read-only review of the measured fix diff. The default `nit` fixes Important and Nit findings; `important` fixes Important findings only. Necessary sibling sites and documentation can be included, with their connection recorded. Generated files remain excluded from direct edits. Unsafe or ambiguous fixes remain unresolved; declined findings require evidence and remain visible.

Only the calling session fixes files. Report-only Codex runs keep their read-only sandbox. Checks that execute repository code require `--run-checks` and project authorization; missing checks leave the edit result unverified. The mode stages, commits and pushes nothing and makes no remote writes. It stops if the captured inputs move unexpectedly and preserves any concurrent local work.

The existing JSON shape is unchanged. Its final result aggregates outstanding findings and verification gaps; the following report separates initial findings, fixed, declined and unresolved items, validation and the final review. An incomplete phase or unrun required validation is never clean. [Review Until Clean](../review-until-clean/README.md) owns repeated review/fix rounds and ledgers. Use its reviewer without `--edit` so there is only one fixer.

## Requirements

- A Git repository with an `origin` remote. The skill finds the default branch from `origin/HEAD`, falling back to the [GitHub CLI](https://cli.github.com/). The GitHub CLI also reads the open pull request's body; without it, the report says the body was not reviewed.
- For `--edit`: [Review Until Clean](../review-until-clean/README.md) and [`jq`](https://jqlang.org/), required by its bundled `review-scope` helper for before and after captures. The loop itself does not run.
- For the preferred report-only Codex path: [`codex`](https://github.com/openai/codex), authenticated, and [`jq`](https://jqlang.org/). These are optional for report-only fallback execution.

## Usage

```text
/review-anti-patterns
/review-anti-patterns --range 4f2a9c1..HEAD --run-checks
/review-anti-patterns --files src/redact.ts --severity important
/review-anti-patterns --edit --run-checks --files src/redact.ts
```

| Option                        | Effect                                                                                                                                                                                          |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--range <rev-range>`         | Review this revision range, written with `..` or `...`. The default is the merge base with the default branch through the working tree, including staged, unstaged and untracked changes.       |
| `--files <paths>`             | Limit the scope to these paths or globs. The report lists the changed files this leaves out.                                                                                                    |
| `--severity <important\|nit>` | Lowest severity reported. The default, `nit`, reports everything.                                                                                                                               |
| `--edit`                      | Apply supported fixes once, validate and review the fix diff. Local edits only; checks still need authorization.                                                                                |
| `--run-checks`                | Also run checks that execute repository code: tests, Makefile targets and package scripts. Pass it only for code you trust, such as your own branch; the skill cannot tell from the repository. |
| `--no-codex`                  | Skip Codex, and run in a fresh read-only subagent or the current session.                                                                                                                       |

Two places it fits:

- **Before opening a pull request**, as a targeted re-review after the general review and its fixes.
- **On a fix for review feedback**, with `--range` set to the commits the fix added, before the fix is pushed. Fix code is new code, and it is where most later-round findings come from. Each file the fix touches is reviewed whole, because Copilot re-reviews the whole pull request every round.

## Recommended Permissions

This skill runs read-only Git and GitHub CLI commands to find its scope, every Git command in one hardened form that starts the same way, so one rule covers them. To allow them without prompts, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git --no-pager -c core.fsmonitor=false *)", "Bash(ssh -G *)", "Bash(gh repo view *)", "Bash(gh pr list *)", "Bash(command -v codex)", "Bash(mktemp -d*)", "Bash(bash \"*/check-edit-worktree\")", "Bash(bash \"*/review-scope\" *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. The multi-line `codex exec` command matches no simple permission rule. Approve its prompt or pass `--no-codex`. The mechanical checks run the project's own linters, validators and tests, which depend on the project.

## Examples

- "review anti-patterns on this branch": the whole branch, every applicable item
- "check the fix before pushing it": the fix commits, with `--range`, and the files they touch
- "did this sanitizer change miss a sibling form?": the sanitizer's file, with `--files`

## See Also

- [Review Until Clean](../review-until-clean/README.md): a looping review with fixes, around any one reviewer
- [Resolve Copilot PR Feedback](../monitor-pr/README.md#monitor-prresolve-copilot-feedback): fixes Copilot findings
- [Plant Defects](../plant-defects/README.md): proves a test can fail
- [All plugins](../../../../README.md)
