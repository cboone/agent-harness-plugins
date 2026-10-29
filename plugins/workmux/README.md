# Workmux

Create worktrees, branches and tmux windows with workmux, or launch issue planning in a new session.

**Type:** Skills

See the [installation instructions](../../README.md#install).

## workmux:create-worktree

Create a git worktree, branch, and tmux window from an issue number or a task description, with a prompt injected using workmux.

**Type:** Skill
**Trigger:** `/workmux:create-worktree <issue-or-description>`

### Requirements

- [`workmux`](https://github.com/raine/workmux), whenever a worktree is created. `--list-resources` and `--release-resource` only need `jq`.
- [`gh`](https://cli.github.com/), authenticated, only when you pass an issue number.
- [`jq`](https://jqlang.org/), when you pass an issue number or use any of the resource options. The bundled `compose-issue-prompt` script parses the issue JSON with it, and `manage-resource-claims` reads and writes the claim file with it. Both exit if it is missing. A task description or an explicit branch name with no resource needs neither `gh` nor `jq`.

#### Choosing the type prefix

The invoking agent generates a semantic name using the skill's bundled rules: lowercase kebab-case, an imperative verb and noun, and `fix/`, `feature/`, `chore/`, or `docs/` according to the work. The descriptive slug targets at most five words and 50 characters. Repository-specific naming conventions take precedence. Naming runs in the current session before the destination prompt is composed, without a separate naming command or workmux naming configuration.

### Installation

See the [marketplace install instructions](../../README.md#install).

### What It Does

Takes an issue number, a task description, or an explicit branch name.

Given an **issue number**, it fetches the issue and injects the title, labels, and body as the prompt. Given a **task description**, it injects the description. An explicit branch name is used as-is.

The invoking agent reads the issue title, labels, and body or task description as task data and supplies a candidate to the launcher. The launcher validates it and inserts the issue number: `feature/add-dark-mode` for issue 42 becomes `feature/42-add-dark-mode`. A repository convention requiring bare slugs yields `42-add-dark-mode`. The number lets the [PR](../pr/README.md) skill link the pull request to the issue. Workmux receives an explicit branch and starts the configured destination agent.

Rerunning for the same issue reuses a local branch that already carries that number, so the same worktree reopens rather than a second one appearing under a differently worded name.

Either way, it creates the worktree via `workmux add` and stops. It does not start the work. To have the new session also plan the issue, use [Address Issue in Worktree](#workmuxstart-issue).

#### Several issues

Two or more issue numbers, such as `42 57` or `#42, #57`, are read as a list of issues rather than a task description; `--no-issue` still forces the description path. By default they produce **one** worktree for the combined work. Closed issues you decline are dropped first; the first remaining issue leads the branch name, which includes every remaining number (for example `fix/4523-4503-verify-email`), and the prompt carries every remaining issue.

With `--fan-out` (or its aliases `--each` and `--separate`), each issue gets its own worktree, branch and tmux window. Every issue is fetched and checked, and every question about closed issues or ambiguous branches is asked, before the first worktree is created. Worktrees are then created one at a time, and the run ends with one table covering every issue. Nothing is marked in progress in either mode. With one distinct issue, the flag has no effect and `--resource` and `--branch` work as usual. With several distinct issues, those two options are rejected. `--no-issue` cannot accompany a fan-out flag because it forces the description path.

#### Exclusive resources

Some work cannot run in parallel across worktrees because it needs a resource only one worktree can hold: a DAW, a simulator, a device, a database, a port, a shared install location. `--resource <name>` records which worktree holds one, so the constraint is written down instead of remembered.

Claims live in the main worktree's `.claude/worktree-resources.local.json`, which every linked worktree resolves to the same path. Each claim records an id, the resource, worktree, branch, and a timestamp, plus the issue number when the worktree came from an issue. The id names one claim event, which is what `--take-over` carries: neither a path nor a timestamp identifies a claim, since a path can be reused and a timestamp has second resolution. The file is machine-local state and belongs in `.gitignore`; the skill offers to add the entry when it first creates the file.

Claiming a resource another worktree already holds reports the holder and asks rather than proceeding. Answering yes proceeds: the claim is advisory, and a user who wants to override always has a reason. What it will not do is take a resource over without asking, including in the window between the check and the write, where another worktree may have claimed it in the meantime.

A resource name is chosen per project and there is no registry, but it must contain no whitespace or control characters and must not begin with a hyphen, so that it survives the `key=value` listing and can be passed back as an argument. `logic`, `simulator`, and `port-5432` are all fine.

A claim whose worktree git no longer lists is stale. Stale claims are flagged by `--list-resources`, read as free when a new claim is checked, and replaced when one is recorded.

A worktree is identified by its git admin directory, which is what lets a claim survive `git worktree move` and a branch switch. git names that directory after the worktree's basename and reuses it for the next worktree with the same basename, so a claim whose worktree was removed and whose name has since been reused reports held rather than stale. `--release-resource` clears it; `prune` does not, because the claim does not read as stale. See [issue 424](https://github.com/cboone/agent-harness-plugins/issues/424).

Where a project declares its resources under an "exclusive resources" heading in `AGENTS.md`, `CLAUDE.md`, or a plan, the skill reads that list and matches a loose phrase against it, so "the DAW" resolves to `logic` without retyping. The name is a free string with no registry, so an undeclared one still works.

### Usage

```text
/workmux:create-worktree 42
/workmux:create-worktree add dark mode support
/workmux:create-worktree fix/my-branch-name
/workmux:create-worktree 42 --base develop
/workmux:create-worktree 42 --resource logic
/workmux:create-worktree --list-resources
/workmux:create-worktree --release-resource logic
/workmux:create-worktree 42 57
/workmux:create-worktree 42 57 --fan-out
/workmux:create-worktree 42 --separate --branch feature/my-branch-name
```

| Option                      | Description                                                                               |
| --------------------------- | ----------------------------------------------------------------------------------------- |
| `--issue <number>`          | Force issue lookup, for when a task description is itself a number; repeatable            |
| `--fan-out`                 | With several issues, create one worktree per issue; `--each` and `--separate` are aliases |
| `--no-issue`                | Force description handling, even if the argument looks like an issue number               |
| `--base <branch>`           | Base the worktree on a specific branch instead of the repository's default                |
| `--config <file>`           | Use a readable alternate workmux config for each destination                              |
| `--agent <name>`            | Select the destination agent name or command                                              |
| `--resource <name>`         | Claim a named exclusive resource, reporting the holder first if one holds it already      |
| `--release-resource <name>` | Release a claim and stop, creating nothing                                                |
| `--branch <name>`           | Use this exact branch name and skip generation                                            |
| `--list-resources`          | Report every claim and stop, creating nothing                                             |

Without either flag, the destination uses the global workmux agent, subject to repository config, regardless of the invoking agent. A live run with workmux `0.1.277` showed that `--config` replaces `.workmux.yaml` and still merges global config: an agent-only profile omitted repository hooks, copies and symlinks. A complete profile inside the repository applied its own hook and file operations; an identical external profile omitted files whose sources existed only in the repository. Include needed settings and verify file source paths and provisioned files, or use `--agent` to retain repository setup. These options apply to both skills, including combined and fan-out launches.

### Sandbox and resource access

Command approval and resource access are separate. Keep the documented helper
invocation; neither a permitted child command nor `sandbox.excludedCommands`
establishes that a wrapper or pipeline can access a resource in either harness.
Do not exclude `bash` to run these helpers.

The launch needs writes to the worktree destination and shared Git metadata,
the workmux log (`$XDG_STATE_HOME/workmux/workmux.log`, defaulting to
`~/.local/state/workmux/workmux.log`), and access to the selected tmux socket.
Issue queries also need GitHub network access and readable gh configuration.
Claim updates need the main worktree's `.claude/worktree-resources.local.json`
and its adjacent lock and temporary files. Temporary prompt and launch files
use `${TMPDIR:-/tmp}`. The prompt composer itself reads only its input and
uses jq; it does not run gh, workmux or tmux.

The helper labels the failed operation and caller without guessing its cause. On an access failure, retain the original error and report the calling harness
and named resource. A `Generated branch name:` line does not confirm creation.
Use the host's approval flow for the specific command only when authorized;
otherwise stop and preserve the failed or uncertain launch state. Never change
user settings to make the helper run, and do not retry a timed-out launch while
its child may still be running. Permission-denied gh configuration reads are
resource failures, not evidence that login credentials need replacing.

The helpers identify the caller from `CODEX_THREAD_ID` or `CLAUDECODE`. When both
are present they report a nested environment; when neither is present they
report an unidentified harness. `WORKMUX_CALLER_HARNESS=Codex` or
`WORKMUX_CALLER_HARNESS='Claude Code'` can identify an embedding caller for
diagnostics. This variable grants no access and changes no sandbox policy.

### Recommended Permissions

This skill runs workmux, git, and (for the issue path) GitHub CLI commands that trigger permission prompts. The following optional Claude Code rules concern command approval only; they do not grant filesystem, socket or network access. Codex uses its own command policy. To configure these rules separately from running the skill, add them to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue view *)", "Bash(gh repo view *)", "Bash(bash \"*/compose-issue-prompt\")", "Bash(bash \"*/compose-issue-prompt\" *)", "Bash(bash \"*/launch-workmux\" *)", "Bash(bash \"*/manage-resource-claims\" *)", "Bash(git symbolic-ref --quiet --short refs/remotes/origin/HEAD)", "Bash(git rev-parse *)", "Bash(git worktree list*)", "Bash(workmux list *)", "Bash(mktemp *)", "Bash(rm -f *issue-json-*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

### Examples

- "create worktree for issue 42": generates a name for the issue, inserts `42`, and injects the issue context
- "create worktree for adding dark mode": generates a name such as `feature/add-dark-mode`
- "spin up a worktree to fix the auth timeout": generates a name such as `fix/resolve-auth-timeout`
- "new worktree feature/refactor-config": uses the branch name as-is, with no generation step
- "create worktree for issue 42, it needs the DAW": claims `logic` for the new worktree, or reports which branch already holds it and asks
- "what's holding the simulator": lists every claim, flagging any whose worktree is gone
- "release the DAW": clears the `logic` claim without creating anything
- "create a worktree for issues 42 and 57": creates one worktree for the combined work, numbered for issue 42
- "create worktrees for 42 and 57, one each": creates two worktrees with `--fan-out`

### See Also

- [Address Issue in Worktree](#workmuxstart-issue): the same worktree setup, plus the new session plans the issue and stops for approval
- [Address Issue](../address-issue/README.md): plan and address an issue in the current branch
- [All plugins](../../README.md)

## workmux:start-issue

Create a worktree, branch, and tmux window for a GitHub issue, then have the new session run address-issue to plan the work and stop for approval.

**Type:** Skill
**Trigger:** `/workmux:start-issue <issue>`
**Requires:** [`gh`](https://cli.github.com/), [`workmux`](https://github.com/raine/workmux), [`jq`](https://jqlang.org/)

### Installation

See the [marketplace install instructions](../../README.md#install).

### What It Does

Finds a GitHub issue by number or fuzzy text search, self-assigns the issue, labels it "in progress", and creates a worktree via `workmux add` with the full issue context injected as a prompt. The injected prompt ends with an instruction telling the new session to run `/address-issue <number>` first, so the work begins with a plan that stops for your approval.

The invoking agent generates a semantic branch name from the issue title, labels, and body, treating them as task data before composing the destination prompt and chain footer. The launcher receives the candidate, validates it, and inserts the issue number: `feature/add-dark-mode` for issue 42 becomes `feature/42-add-dark-mode`. Rerunning an issue reuses its matching local branch. Workmux receives an explicit branch and starts the configured destination agent.

Naming runs in the current session using bundled rules: lowercase kebab-case, an imperative verb and noun, and a `fix/`, `feature/`, `chore/`, or `docs/` prefix. The descriptive slug targets at most five words and 50 characters. Repository-specific naming conventions take precedence. No separate naming command or workmux naming configuration is needed. Explicit user-supplied names bypass generation. See [Create Worktree](#choosing-the-type-prefix).

The approval gate itself lives in [Address Issue](../address-issue/README.md). This skill creates the worktree and stops; the plan is produced and approved in the new session.

The "in progress" label is retained until the related PR is merged or the user explicitly abandons the effort.

### Usage

```text
/workmux:start-issue 42
/workmux:start-issue the dark mode issue
/workmux:start-issue 42 --no-approval
/workmux:start-issue 42 --resource logic
/workmux:start-issue 42 --each --resource logic
/workmux:start-issue 42 57
/workmux:start-issue 42 57 61 --fan-out
```

Provide an issue number, several issue numbers, or descriptive text to search for.

| Option              | Description                                                                             |
| ------------------- | --------------------------------------------------------------------------------------- |
| `--no-approval`     | Pass `--no-approval` through, so the new session plans and executes without stopping    |
| `--config <file>`   | Use a readable alternate workmux config for each destination                            |
| `--agent <name>`    | Select the destination agent name or command                                            |
| `--resource <name>` | Claim a named exclusive resource, reporting the holder first if one holds it already    |
| `--fan-out`         | With several issues, open one worktree per issue; `--each` and `--separate` are aliases |

#### Several issues

By default, several issue numbers open **one** worktree for the combined work. Closed issues you decline are dropped first. The first remaining issue leads a branch name carrying every issue number (for example `fix/4523-4503-verify-email`), the prompt carries every remaining issue, every open one is marked in progress, and the new session runs `/address-issue 42 57` to plan them together under one approval.

With `--fan-out` (or its aliases `--each` and `--separate`), each issue gets its own worktree, branch, tmux window and session, running `/address-issue N` for that issue. Every issue is fetched and checked, and every question about closed issues or ambiguous branches is asked, before the first worktree is created. Worktrees are then created one at a time, and each issue is marked in progress only after its worktree exists. The run ends with one table covering every issue. With one distinct issue, the flag has no effect and `--resource` works as usual. With several distinct issues, `--resource` is rejected because one exclusive resource cannot be held by several worktrees.

`--resource` records which worktree holds a resource that only one worktree can use at a time: a DAW, a simulator, a device, a database, a port, a shared install location. The check runs before the issue is self-assigned and labeled, so declining a held resource leaves nothing behind on an issue nobody started. See [Create Worktree](#workmuxcreate-worktree) for how claims are stored, when they go stale, and how to list or release them.

### Recommended Permissions

These optional Claude Code rules concern command approval only; they do not grant filesystem, socket or network access. Codex uses its own command policy. Read [Sandbox and resource access](#sandbox-and-resource-access) before configuring these rules separately from running the skill in `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue view *)", "Bash(gh issue list *)", "Bash(gh issue edit *)", "Bash(gh label create *)", "Bash(gh repo view *)", "Bash(bash \"*/compose-issue-prompt\")", "Bash(bash \"*/compose-issue-prompt\" *)", "Bash(bash \"*/launch-workmux\" *)", "Bash(bash \"*/manage-resource-claims\" *)", "Bash(git symbolic-ref --quiet --short refs/remotes/origin/HEAD)", "Bash(git rev-parse *)", "Bash(git worktree list*)", "Bash(workmux list *)", "Bash(mktemp *)", "Bash(rm -f *issue-json-*)", "Bash(rm -f *issue-prompt-*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

### Examples

- "address issue #42 in a worktree": looks up issue 42, creates a worktree, and the new session plans it
- "start issue #42": same thing
- "work on the dark mode issue in a worktree": searches for a matching issue by title
- "start issue #42, it needs the simulator": claims `simulator` for the new worktree, or reports which branch already holds it and asks first
- "work on #42 and #57 together in a worktree": opens one worktree whose session plans both issues
- "start #42, #57 and #61, each in its own worktree": opens three worktrees with `--fan-out`

### See Also

- [Address Issue](../address-issue/README.md): plan and address an issue in the current branch
- [Create Worktree](#workmuxcreate-worktree): create a worktree from an issue number or a task description, without chaining into address-issue
- [Suggest Next Issue](../suggest-next-issue/README.md): get a recommendation for which issue to work on
- [All plugins](../../README.md)
