# Codex consumption review

Reviewed on 2026-09-15 against repository revision `340f3192`. This document preserves the original audit findings and reported evidence; consolidation does not constitute a new compatibility evaluation. The findings' CLI and documentation claims describe the audit baseline; the [milestone 1 baseline](#milestone-1-baseline) supersedes them where they differ.

Tracking: [umbrella issue #434](https://github.com/cboone/agent-harness-plugins/issues/434). Implementation: [four-milestone roadmap](../plans/todo/2026-09-15-codex-consumption-improvements.md). Update these documents in place as work proceeds.

## Milestone 1 baseline

Captured on 2026-09-19 against repository revision `046f1389`; the milestone branch head at capture, `3267c0ae`, added only plan documents. Each claim is marked by its source:

- **Observed:** run locally on macOS (Darwin 25.6.0) with a temporary `$CODEX_HOME` outside the repository, leaving the real Codex home untouched.
- **Documented:** OpenAI's official documentation, read on 2026-09-19: [plugins](https://learn.chatgpt.com/docs/plugins), [skills](https://learn.chatgpt.com/docs/build-skills), [hooks](https://learn.chatgpt.com/docs/hooks), [CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security), and [sandboxing](https://learn.chatgpt.com/docs/sandboxing).
- **Upstream source:** `openai/codex` at `be2951ea34f0`, the commit tagged `rust-v0.155.1`, mainly `codex-rs/ext/skills/src/render.rs`. `main` at `36b84c81ec01` (2026-09-17) renders identically and differs only in suppressing the warning about shortened descriptions.

The support policy targets the current stable Codex CLI. These constants record the release used for the baseline; they are not a minimum version.

### CLI commands

**Observed.** `codex --version` printed `codex-cli 0.155.1`. The milestone plan anticipated `0.155.0`; `0.155.1` was installed at capture time.

`codex plugin --help` lists `add`, `list`, `marketplace`, and `remove`. `codex plugin marketplace --help` lists `add`, `list`, `upgrade`, and `remove`:

| Command                                               | Observed interface                                                                                        |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `codex plugin marketplace add <SOURCE>`               | A local path, `owner/repo[@ref]`, or an HTTPS or SSH Git URL; `--ref` and repeatable `--sparse`, `--json` |
| `codex plugin marketplace list`                       | Configured marketplaces and their roots; `--json`                                                         |
| `codex plugin marketplace upgrade [MARKETPLACE_NAME]` | "Refresh configured Git marketplace snapshots"; all Git marketplaces when the name is omitted             |
| `codex plugin marketplace remove <MARKETPLACE_NAME>`  | Removes a configured marketplace source by name                                                           |
| `codex plugin add <PLUGIN[@MARKETPLACE]>`             | Installs one plugin; `--marketplace` replaces the `@MARKETPLACE` suffix                                   |
| `codex plugin list`                                   | Plugins from configured marketplaces; `--marketplace`, `--json`, `--available`                            |
| `codex plugin remove <PLUGIN[@MARKETPLACE]>`          | Uninstalls a plugin and removes its local cache                                                           |

A `file://` Git URL is rejected: "invalid marketplace source format; expected owner/repo, a git URL, or a local marketplace path".

`codex features list` rows for hooks, plugins, and skills:

| Feature                           | Stage             | Enabled |
| --------------------------------- | ----------------- | ------- |
| `hooks`                           | stable            | true    |
| `plugin_hooks`                    | removed           | false   |
| `plugin_sharing`                  | stable            | true    |
| `plugins`                         | stable            | true    |
| `recommended_plugins`             | stable            | false   |
| `remote_plugin`                   | stable            | true    |
| `skill_env_var_dependency_prompt` | removed           | false   |
| `skill_mcp_dependency_install`    | stable            | true    |
| `skill_search`                    | stable            | true    |
| `skip_host_skill_discovery`       | under development | false   |

`skill_search` was enabled while observing the skill list below and did not change it.

### Plugin installation and refresh

**Observed.** Registering a marketplace installs nothing: `codex plugin list` reported every plugin as `not installed` until `codex plugin add` installed it. Installed plugins land at `$CODEX_HOME/plugins/cache/<marketplace>/<plugin>/<version>/`, with `<version>` taken from the plugin manifest for both local-path and Git marketplaces. The [plugin build documentation](https://developers.openai.com/plugins/build/plugins#how-local-marketplaces-work) says local plugins use `local` as the version segment; the CLI install observed here did not.

Whether `codex plugin marketplace upgrade` refreshes an installed plugin whose version is unchanged:

- **Git marketplace: yes.** The marketplace was added as `cboone/agent-harness-plugins --ref <9d79cb29~1>` and `bootstrap-project` 1.3.1 was installed. With the configured ref changed to `9d79cb29`, which alters `references/overlap-rules.md` at the same version, `upgrade` replaced both the marketplace snapshot and the installed cache copy of that file.
- **Local-path marketplace: no.** `upgrade` exits with "marketplace `probe-marketplace` is not configured as a Git marketplace". After an edit to the local source at an unchanged version, the installed cache kept its old content through `upgrade` and through a new `codex debug prompt-input` session. Running `codex plugin add` again replaced the cached files. A version bump in the local source was not picked up by a new `codex debug prompt-input` session either; an interactive restart was not observed.

### Skill discovery

**Observed.** `codex debug prompt-input` renders the model-visible prompt without authentication or a model call. With all 62 plugins installed from this worktree as a local-path marketplace, the skill list held 66 entries, the 5 bundled system skills followed by all 61 plugin skills, none shortened or omitted:

```text
### Skill roots
- `r0` = `$CODEX_HOME/skills/.system`
- `r1` = `$CODEX_HOME/plugins/cache/agent-harness-plugins`
### Available skills
- imagegen: Generate or edit raster images when ... (file: r0/imagegen/SKILL.md)
...
- add-cobra-version:add-cobra-version: Add a version subcommand ... (file: r1/add-cobra-version/1.0.2/skills/add-cobra-version/SKILL.md)
```

- **Name form:** plugin skills render as the qualified `plugin:skill`; system skills render bare.
- **Path form:** Codex replaced the shared roots with the aliases `r0` and `r1`. Without aliasing, a plugin skill's path is `$CODEX_HOME/plugins/cache/agent-harness-plugins/<plugin>/<version>/skills/<skill>/SKILL.md`, and `$CODEX_HOME` defaults to `~/.codex`.
- **Reference model:** the default model rendered identically to `-c model=gpt-6-astra`, the highest-priority listed model in `codex debug models --bundled`. Its `context_window` is 272,000 tokens, as is every listed model's, so the budget is 5,440 tokens.
- **Framing:** the `## Skills` heading, the introduction, the `### Skill roots` table, and the `### Available skills` heading surround the entries. `gpt-6-astra` sets `include_skills_usage_instructions` to false; `gpt-5.5`, which sets it to true, adds a `### How to use skills` section.
- **Bundled system skills:** `imagegen`, `openai-docs`, `plugin-creator`, `skill-creator`, and `skill-installer`. Their lines cost 524 tokens as rendered and 567 tokens with unaliased paths under a 15-character home directory.
- **Current catalog:** as rendered with aliasing, the 61 plugin lines cost 3,618 tokens.

**Upstream source.** `render.rs` explains the observed list:

- Each entry renders as `- {name}: {description} (file: {path})`. A description longer than 1,024 characters is cut to 1,021 characters plus `...`.
- The budget is 2 percent of the model's `context_window`, falling back to `max_context_window`. A configured `skills.max_context_tokens` replaces it, capped at 10,000 tokens. With neither, the budget is 8,000 characters.
- A token budget charges each entry `ceil(bytes / 4)` for the line plus its newline. A character budget charges its characters.
- Only entries are charged. The framing and usage instructions are outside the budget, except that an aliased render also charges its roots table.
- When the full entries exceed the budget, Codex keeps every name and path and distributes the remaining budget across descriptions one character at a time, shortening them from the end. When names and paths alone exceed it, Codex omits entries from the end of the list. The observed list puts system skills first and plugin skills in name order, so the `write-*` skills would be omitted first.
- Codex aliases shared path roots whenever that includes more skills, shortens fewer description characters, or costs less.
- The extension-compatible render policy, used for host skills in turn input, prints an entry's `interface.short_description` from `agents/openai.yaml` in place of its `description`.

### Skill metadata and invocation

**Documented.**

- Codex invokes a skill explicitly through `$` mentions or the `/skills` selector, and implicitly "when your task matches the skill description."
- The skills documentation confirms the 2 percent and 8,000-character budgets, and that Codex "shortens skill descriptions first" and "may omit some skills from the initial list and show a warning."
- `agents/openai.yaml` configures interface metadata, invocation policy (`policy.allow_implicit_invocation`), and tool dependencies (`dependencies.tools` with `type: "mcp"`). The documentation describes no skill-to-skill dependency field.
- No page describes the qualified `plugin:skill` name; the render above is the evidence for it.

### Hooks

**Observed.** `hooks` is stable and enabled; `plugin_hooks` is removed. `plugins/notify/hooks/codex.hooks.json` wires `Stop`, `UserPromptSubmit`, `PreToolUse` matching `request_user_input`, and `PreCompact` matching `auto`.

**Documented.**

- Hooks are enabled by default, and `codex_hooks` remains a deprecated alias of `hooks`.
- The events are `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`, `Interrupt`, `SessionStart`, and `SessionEnd`. `Interrupt` and `SessionEnd` do not run for subagents.
- `PreCompact` matches its trigger, `manual` or `auto`. The documentation does not name `request_user_input` as a `PreToolUse` target; it says other local function tools match by function name.
- "Codex records trust against the hook's current hash, so new or changed hooks are marked for review and skipped until trusted." `/hooks` reviews and trusts them, and "Installing or enabling a plugin doesn't automatically trust its hooks." `--dangerously-bypass-hook-trust` skips the requirement for one run.
- Plugin hook commands receive `PLUGIN_ROOT` and `PLUGIN_DATA`, plus `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` for compatibility.

### Host constraints

**Documented.** The OS-enforced sandbox and the approval policy decide when Codex must stop and ask. When a plugin capability runs through a Codex host, "the host's sandbox and approval policy applies." Codex loads a project's `.codex/config.toml` only for trusted projects. `/plan` enters Plan mode, and hooks receive `permission_mode`, whose values include `plan`. The documentation does not state that skill instructions cannot override these controls; that is this repository's design rule, derived from the host enforcing them.

### Other documentation changes

**Documented**, outside milestone 1:

- The preferred plugin manifest is now a root `plugin.json` using the Agent Plugins schema, with `.codex-plugin/plugin.json` supported as a compatibility fallback.
- Codex reads `.claude-plugin/marketplace.json` as a "legacy-compatible marketplace."
- The IDE extension does not support plugins.
- `approval_policy = "untrusted"` is retired, which bears on finding 19.

### Differences from the 2026-09-15 audit

- The installed CLI moved from `0.154.0` to `0.155.1`, and the catalog from 57 plugins and 56 skills to 62 plugins and 61 skills.
- **Finding 2:** `plugin_hooks` is removed rather than required, hooks run once trusted through `/hooks`, and Codex supports twelve hook events.
- **Finding 7:** Codex budgets 2 percent of the context window, 5,440 tokens for the reference model, not a repository character limit. Names and paths cost about 10,000 bytes of it before any description.
- **Finding 17:** its premise is outdated. `notify` already wires four Codex events: `Stop`, `UserPromptSubmit`, `PreToolUse` for `request_user_input`, and `PreCompact` for `auto`. The claim that it wires only `Stop` came from the README's stale known-limitations section. Reassessing further events remains open.

### Limits of this baseline

- Everything observed ran on macOS; Linux was not checked.
- The skill list came from `codex debug prompt-input`. No model call was made, so the baseline shows what Codex offers the model, not how the model selects from it.
- Hook trust in `/hooks`, hook execution, and `PreToolUse` matching of `request_user_input` need an authenticated interactive session and were not observed at capture; the [milestone 1 verification](#milestone-1-verification) later observed hook review and trust.
- Git marketplace refresh was observed by editing a pinned ref in the temporary `config.toml`, not by a branch ref advancing.

### Validation constants

These constants define the Codex inventory budget that repository validation models:

| Constant                     | Value                                                                                                   | Source                                         |
| ---------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Reference model              | `gpt-6-astra`                                                                                           | Observed default model                         |
| Context window               | 272,000 tokens                                                                                          | `codex debug models --bundled`                 |
| Primary budget               | 5,440 tokens, 2 percent of the context window                                                           | Upstream source and documentation              |
| Bytes per token              | 4, rounded up per entry                                                                                 | Upstream source                                |
| Fallback budget              | 8,000 characters, when the context window is unknown                                                    | Upstream source and documentation              |
| Framing reserve              | None; framing is outside the budget, and the check ignores aliasing                                     | Upstream source                                |
| Bundled system skill reserve | 2,400 bytes, or 600 tokens; 567 tokens observed                                                         | Observed                                       |
| Name form                    | `plugin:skill`                                                                                          | Observed                                       |
| Path form                    | `/Users/username/.codex/plugins/cache/agent-harness-plugins/<plugin>/<version>/skills/<skill>/SKILL.md` | Observed layout, 15-character home placeholder |
| Description warning          | Over 150 characters                                                                                     | Derived below                                  |

The warning threshold is the primary budget's average share per skill at the baseline. After the reserve, 4,840 tokens is 19,360 bytes, or 317 bytes for each of 61 skills. Names, paths, and line syntax average 164 bytes of each line, which leaves 153 characters for a description, rounded down to 150.

Rule 17 of `bin/validate-plugins` records these constants. It fails when the catalog exceeds the primary budget less the reserve, prints the catalog's cost against both budgets on every run, and applies the fallback as its gate when `CODEX_REFERENCE_CONTEXT_WINDOW` is set empty. Measured this way at `046f1389`, the catalog-summary inventory cost 4,472 of 4,840 available tokens; with canonical descriptions it would have cost 10,966.

Revisit these constants only when the reference model changes or a Codex release changes its bundled system skills, which the reserve measures, and record the change here.

## Milestone 1 verification

Run on 2026-09-19 at `d1693ba7`, the milestone branch head carrying every implementation change, with Codex CLI `0.155.1` on macOS.

### Deterministic checks

- `make test-all` passed: Markdown and shell linting reported no issues, `make validate` passed, and `make test-scrut` passed all 458 cases in 9 documents.
- Rule 17 at this revision: the 61 skills cost 4,689 of the 4,840 available tokens, and 18,676 characters against the 5,600 the fallback leaves. No description exceeds 150 characters.
- `make build` followed by `git status --porcelain -- .agents dist` printed nothing.
- The `check-versions` skill found every one of the 62 plugins with canonical or generated changes bumped forward once from `046f1389`, `notify`'s Codex manifest in step, and a marketplace that covers all 62 plugins and holds no version state.

### Codex smoke checks

Every Codex command used a temporary `$CODEX_HOME` in the session's scratch directory, outside the repository. It was authenticated with an interactive `codex login` inside that home; no credential file was copied. This worktree was registered as a local-path marketplace so the branch content was tested.

```text
$ codex plugin marketplace add <worktree>
Added marketplace `agent-harness-plugins` from <worktree>.
$ codex plugin add commit@agent-harness-plugins
Added plugin `commit` from marketplace `agent-harness-plugins`.
Installed plugin root: $CODEX_HOME/plugins/cache/agent-harness-plugins/commit/1.3.1
$ codex plugin add notify --marketplace agent-harness-plugins
Added plugin `notify` from marketplace `agent-harness-plugins`.
$ codex plugin list
commit@agent-harness-plugins  installed, enabled  1.3.1  <worktree>/dist/codex/plugins/commit
notify@agent-harness-plugins  installed, enabled  2.3.1  <worktree>/dist/codex/plugins/notify
```

- **Discovery:** `codex debug prompt-input` listed `commit:commit` with its canonical routing description. With all 62 plugins installed, all 61 plugin lines matched their canonical descriptions exactly, none shortened, at 3,835 tokens as rendered with aliasing.
- **Explicit invocation:** `codex exec -s workspace-write '$commit'` ran in a disposable repository with one staged change. Codex announced the `commit` and `use-git` skills, read both `SKILL.md` files from the installed cache, and inspected the staged diff. It then stopped without attempting the commit: "Commit blocked: the sandbox prevents writing `.git/index.lock`. The staged changes remain intact", followed by the exact `git commit -S` command to run.
- **Natural-language activation:** `codex exec -s workspace-write 'Please commit the staged changes.'` selected and read the same two skills and stopped the same way: "Couldn’t commit: the sandbox blocks writes to `.git/index.lock`, and escalation is disabled. Your changes remain staged." Both runs reported the host restriction and the command to run instead of working around it, as the authority adapter describes.
- **Hook trust:** Codex opened with "Hooks need review" and "4 hooks are new or changed." `/hooks` listed `PreToolUse`, `PreCompact`, `UserPromptSubmit`, and `Stop` as installed, inactive, and awaiting review. The `PreToolUse` entry showed matcher `request_user_input`, source `Plugin - notify@agent-harness-plugins`, and the resolved `notify codex-question` command. Once trusted, all four were active, recorded as `trusted_hash` entries under `[hooks.state]` in `config.toml`. After a timeout was added to the cached `PreCompact` definition, a relaunch reported "1 hook is new or changed", with only `PreCompact` awaiting review.
- **Teardown:** `codex plugin remove` removed `commit` and `notify`, then every other installed plugin. `codex plugin marketplace remove agent-harness-plugins` left "No plugin marketplaces in scope." `codex logout` removed the credentials, and the temporary home was deleted.

### Claude Code and OpenCode

- `claude plugin validate --strict` passed for all 62 plugin directories and for the marketplace, with Claude Code `2.1.278`.
- A headless `claude -p --plugin-dir plugins/commit` session reported the branch's `commit` description verbatim, so Claude Code loads the canonical skill.
- `make build` regenerated the OpenCode mirror without changes, and its skills link to the canonical sources.

### Limits of the verification

- The authenticated session defaulted to `gpt-5.6-sol` rather than the `gpt-6-astra` of the unauthenticated render. Both have a 272,000-token context window, so the recorded budget stands.
- While logged in, `codex plugin list` still counted four installed plugins after this marketplace's plugins were removed and its cache emptied. They were not identified, and none was listed after logout.
- Each model-backed check ran once and stays informational until the roadmap's repeatability requirement is met. Hook payloads and notification delivery were not exercised, and Linux was not checked.

## Assessment and agreed direction

**The repository has a useful distribution foundation, but Codex support needs a behavioral compatibility layer.** Generated files remain consistent with their sources, yet those sources often encode Claude-specific tools, installation behavior, and workflow assumptions. Codex must currently reinterpret those instructions to complete the intended task.

The `/skill` versus `$skill` mismatch is one part of this larger problem.

The interview established these decisions:

- **Primary target:** Codex CLI on macOS and Linux, supporting the current stable release.
- **Support standard:** equal support for Claude and Codex, using each harness’s capabilities where available.
- **Architecture:** shared workflows with explicit harness adapters.
- **Activation:** preserve both natural-language activation and explicit skill invocation.
- **Catalog:** preserve existing names and plugin boundaries initially.
- **Priority:** improve and evaluate the Git and review workflow chain first.
- **Validation:** deterministic CI checks plus real-Codex evaluations for releases and selected changes.
- **Other harnesses:** preserve OpenCode support; desktop, IDE, and cloud differences remain documented secondary considerations.
- **Delivery:** one umbrella issue and four milestone checklists, with focused, GPG-signed commits. Additional issues are reserved for independently shippable work, deliberate deferrals, or discoveries outside this scope.

## Review findings

### Installation and documentation

**1. Installation guidance describes an obsolete CLI interface. Confirmed.**

The [Codex installation guide](https://github.com/cboone/agent-harness-plugins/blob/340f319211b8ebfd64b0d37abda7768886bbf165/README.md#L194) describes marketplace-level management using Codex `0.128.0`. The installed CLI is `0.154.0` and exposes individual `plugin add`, `plugin list`, and `plugin remove` commands.

Users need instructions that distinguish registering a marketplace from installing, inspecting, and removing its plugins. Current documentation also needs selective installation and troubleshooting examples. The current [official command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli) documents these interfaces.

**Milestone 1: resolved.** The README separates registering the marketplace from installing, listing, refreshing, and removing plugins with `codex plugin add`, `list`, and `remove`, and adds selective installation and troubleshooting guidance checked against CLI `0.155.1`.

**2. Hook setup and capability claims are outdated. Confirmed.**

The README tells users to enable `plugin_hooks`. The installed CLI reports that feature as removed and `hooks` as stable.

The repository also says Codex lacks `PreCompact`, `SubagentStop`, and `SessionEnd`. Current documentation supports those events. It additionally requires review and trust of non-managed hook definitions, including plugin hooks, which the repository’s instructions omit. These errors affect both consumers and future plugin authors. [Official hook documentation](https://learn.chatgpt.com/docs/hooks).

**Milestone 1: resolved.** The root and `notify` READMEs drop the removed `plugin_hooks` flag, describe `/hooks` review and trust, including review again after an upgrade changes a hook, and list the four Codex events `notify` wires. The [milestone 1 verification](#milestone-1-verification) observed that review, trust, and review again after a change.

**3. Skill invocation examples are Claude-specific throughout the product. Confirmed.**

The root catalog, plugin READMEs, workflow recommendations, and generated prompts predominantly use `/name`.

Codex uses `$` mentions or its `/skills` selector. Documentation should explain explicit invocation, qualified names shown by the selector, and natural-language activation. A skill mention belongs in the conversation, not in a shell command. [Official skill documentation](https://learn.chatgpt.com/docs/build-skills).

A global replacement would be unsafe: legitimate harness commands such as `/skills` must remain, and dollar signs inside shell strings require correct quoting.

**Milestone 1: contract established; adoption pending in milestone 3.** The invocation adapter in `docs/plugin-development.md` renders `/name` for Claude Code, `$name` or `/skills` for Codex, and a request by name for OpenCode, and keeps skill identity and arguments separate in generated prompts. The README notes the Codex form. Catalog-wide examples and generated handoffs remain for milestone 3.

**4. Documentation links break after installation. Reproduced.**

The generator adjusts root README links for the repository’s `dist/codex` depth. Installed plugins have a different directory layout.

In the installed `create-worktree` README, installation links resolve to a nonexistent `~/.codex/plugins/README.md`; sibling-plugin links also resolve to nonexistent paths. Repository link checks do not establish that installed documentation works.

Use repository URLs for documentation outside the package and relative links for files bundled inside it.

**5. Project presentation and authoring guidance still position Codex as secondary. Confirmed.**

Examples include the “Claude Code Plugins” title, marketplace description, and instructions describing rich activation descriptions as something maintained for Claude.

The presentation should match the agreed support policy. Existing Claude-compatible manifest locations can remain where supported; their names alone are not defects.

**Milestone 1: authoring and distribution wording corrected.** The plugin development guide, the `create-plugin` skill, and the README's Codex section describe one shared workflow and one routing description for every harness, and no longer present Codex's description as a shorter copy. The "Claude Code Plugins" title and the marketplace metadata description remain for milestone 3's authoring and presentation updates.

### Discovery and prompt quality

**6. The Codex build deliberately removes activation information. Confirmed transformation; behavioral impact needs evaluation.**

The [Codex generator](https://github.com/cboone/agent-harness-plugins/blob/340f319211b8ebfd64b0d37abda7768886bbf165/bin/build-codex-marketplace#L197) replaces every skill description with its marketplace summary.

That saves context, but removes useful distinctions. For example:

- `plant-defects` loses its detailed activation conditions.
- `write-markdown` loses its explicit review trigger.
- Workflow descriptions lose user phrases, prerequisites, and scope boundaries.

Marketplace summaries and routing descriptions serve different purposes. Codex should receive concise descriptions written for selection, rather than automatically receiving catalog copy. Actual selection accuracy remains unmeasured.

**Milestone 1: resolved.** `bin/build-codex-marketplace` copies `SKILL.md` files unchanged, and rule 16b of `bin/validate-plugins` fails when a generated copy differs from its source. The canonical descriptions were rewritten as routing descriptions that fit Codex's budget. Selection accuracy remains unmeasured until milestone 2's real-Codex evaluation. Shortening dropped trigger phrasings the old descriptions carried, such as "watch the pr" and "keep an eye on the pr" for `monitor-pr`, asking what can be worked on in parallel for `suggest-next-issue`, and "who has the DAW" for `create-worktree`. The activation checks in milestones 2 and 4 should include phrasings like these, so any routing lost to shortening is measured rather than assumed.

**7. The context-budget check measures only part of discovery overhead. Confirmed coverage gap.**

The generated descriptions total **6,881 characters**, against a repository limit of 12,000. That calculation excludes names, paths, and surrounding metadata.

Codex’s initial skill list includes paths and may shorten descriptions or omit skills when its budget is exceeded. Therefore, the current check cannot establish that the entire installed catalog remains discoverable. [Official skill documentation](https://learn.chatgpt.com/docs/build-skills).

**Milestone 1: resolved.** Rule 17 of `bin/validate-plugins` renders each skill's full inventory line, name and installed path included, and budgets it against 2 percent of the reference model's context window less a system-skill reserve, reporting the 8,000-character fallback on every run. The catalog costs 4,689 of the 4,840 tokens available.

**8. Codex-specific metadata is unused. Improvement opportunity.**

None of the 56 skills ships `agents/openai.yaml`.

Use this selectively for invocation policy, useful interface metadata, and supported tool dependencies. Preserve natural-language activation as agreed. Do not blanket-disable workflow skills merely because their authorized execution can change files or contact GitHub.

**Milestone 1: policy decided.** Add `agents/openai.yaml` only for supported interface metadata, an invocation-policy override, or an MCP tool dependency, and never set `interface.short_description`, which Codex prints in place of the routing description. No skill needs one yet.

**9. Several entrypoints load substantial material before selecting a relevant path. Confirmed structure; improvement needs evaluation.**

Seven skill bodies exceed 500 lines. `release` has 965 lines; `set-up-installers` contains multiple language-specific workflow templates.

Move conditional reference material behind explicit selection steps. Preserve the workflow’s requirements while reducing irrelevant material loaded for a particular task. Several existing style guides already demonstrate this approach.

### Workflow execution and composition

**10. Workflow chains require Claude’s `Skill` tool. Confirmed instruction mismatch.**

Examples include `pr`, `bootstrap-project`, `monitor-pr`, `pin-everything`, and `refresh-project-scaffolding`.

Codex needs instructions for resolving a skill through its advertised location, loading it through the available mechanism, passing the requested options, and continuing the parent workflow. A `$skill` mention is not a substitute tool call.

The existing `lint-and-fix` parent-continuation contract is a useful foundation and should be preserved.

**Milestone 1: contract established; adoption pending in milestones 2 and 3.** The composition and continuation adapters define how a parent loads a child skill in each harness, passes a continuation block, and resumes. Every composition reference now uses the canonical "Invoke the `NAME` skill" phrase without naming Claude's `Skill` tool. The Git and review chain adopts the adapters in milestone 2 and the rest of the catalog in milestone 3.

**11. Fallbacks confuse a missing Claude tool with a missing capability. Confirmed.**

Examples:

- Dependabot skills fall back from `AskUserQuestion` directly to plain numbered text.
- `address-issue` distinguishes Claude’s plan tools from an “otherwise Codex” path without handling an already-active Codex Plan Mode.
- Monitoring skills direct Codex toward blocking shell sleeps.
- Report-board instructions associate artifact availability with harness identity.

Adapters should inspect available capabilities. Use structured questions, interruptible waiting, and supported artifact or browser tools when present. Provide a documented fallback when they are absent.

This does not imply that every Codex environment has every capability.

**Milestone 1: contract established; adoption pending in milestones 2 and 3.** The capabilities adapter selects behavior by the capability a session offers, with a documented fallback when it is absent. The examples above remain until their skills adopt it.

**12. Approval instructions do not adequately distinguish workflow approval from harness restrictions. Confirmed gap.**

“No prompts” and `--no-approval` can describe workflow behavior, but cannot override active Plan Mode, sandbox restrictions, hook trust, or higher-priority instructions.

At the same time, adapters should preserve previously granted authorization and avoid inserting repeated confirmation steps into an authorized workflow.

**Milestone 1: contract established; adoption pending in milestones 2 and 3.** The authority and permissions adapter preserves prior user authorization while leaving Plan mode, sandbox roots, network policy, hook trust, and tool approval to the host.

**13. Selective installation exposes undeclared skill dependencies. Confirmed design gap.**

Plugins such as `pr` and `bootstrap-project` require other skills, while users can install plugins individually. Existing cross-reference checks establish that a referenced plugin exists in this repository, not that it is installed and available to the consuming session.

Distinguish required dependencies from optional recommendations. Detect missing required skills before consequential steps and provide an actionable installation instruction. Do not silently substitute a different workflow.

**Milestone 1: declarations resolved; preflight adoption pending.** Thirteen skills declare their required and optional dependencies, and `bin/check-cross-references` rejects an undeclared composition and a malformed, unresolved, repeated, or unused declaration. The adapter contract defines the preflight, the missing-dependency stop, and the skip-and-report behavior for selection-driven candidates. Applying them in each workflow body is milestone 2 for the Git and review chain and milestone 3 elsewhere.

### Scripts, worktrees, and hooks

**14. Script lookup can select the wrong installed copy. Confirmed ambiguity; wrong-version execution not reproduced.**

Five script-backed skills recommend recursive searches such as `**/plugin/**/scripts/helper`, with preferences for installed directories and exclusions for backups.

Multiple versions can still satisfy those rules. Resolve helpers from the loaded skill’s own location, accounting for symlinks. Each package should identify its own scripts and assets without searching unrelated caches.

**15. Worktree handoffs embed the wrong invocation syntax. Confirmed.**

The [issue-worktree handoff](https://github.com/cboone/agent-harness-plugins/blob/340f319211b8ebfd64b0d37abda7768886bbf165/plugins/address-issue-in-worktree/skills/address-issue-in-worktree/SKILL.md#L232) injects `/address-issue NUMBER`, including when the destination session is Codex.

The destination harness matters, not merely the harness creating the worktree. Carry skill identity and arguments separately from their rendered invocation, and preserve literal dollar signs through shell and prompt transport.

The launcher already contains Codex-specific pane recovery. Retain and test that behavior.

**16. Writable-location assumptions need explicit handling. Confirmed design gap.**

Examples include report boards under the user cache, resource claims in the main worktree, and creation of sibling worktrees. Those locations can fall outside a Codex session’s writable roots.

Check the actual destination and available permissions before dependent side effects. Use an appropriate permitted location where the workflow allows it, and explain the precise limitation otherwise.

**17. Notification support can use more of Codex’s current capabilities. Improvement opportunity.**

`notify` currently wires only `Stop`. Reassess compaction and lifecycle notifications against the supported baseline, while preserving meaningful notification semantics.

Do not map every permission-policy event to “the user needs to respond.” Verify event timing, payloads, notification grouping, and trust behavior. Add coverage for missing dependencies and installation paths containing spaces.

**Milestone 1: premise corrected; expansion deferred to milestone 3.** On Codex, `notify` already wires `Stop`, `UserPromptSubmit`, `PreToolUse` for `request_user_input`, and `PreCompact` for `auto`. The claim that it wires only `Stop` came from a stale README section, now corrected. Reassessing further events remains milestone 3.

### Configuration and validation

**18. A shipped Codex configuration example has incorrect TOML structure. Reproduced.**

In the [configuration reference](https://github.com/cboone/agent-harness-plugins/blob/340f319211b8ebfd64b0d37abda7768886bbf165/plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-config-files.md#L209), these settings occur after `[sandbox_workspace_write]`:

- `web_search`
- `project_doc_max_bytes`
- `project_doc_fallback_filenames`

Parsing the example confirms that they become members of that table rather than root settings. The example is valid TOML but does not express the intended configuration.

**19. Other configuration guidance also needs correction. Confirmed.**

The cleanup skill claims that configuring a `CLAUDE.md` fallback alongside an `AGENTS.md` symlink causes duplicate ingestion. Codex selects at most one instruction file per directory, so that explanation is incorrect. [Instruction discovery documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Profile examples and approval-policy guidance also need updating. Current documentation describes separate profile files and rejects `approval_policy = "untrusted"`. [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

Scaffolding should generate configuration for the harnesses a project uses and retain shared guidance in `AGENTS.md`.

**20. Existing checks validate repository consistency more strongly than consumer behavior. Confirmed.**

The repository has valuable checks for manifests, versions, generated output, script references, and shell behavior. Missing coverage includes:

- Installed-package discovery and documentation.
- `$skill` and qualified skill references.
- Partial installation and dependency resolution.
- Natural-language activation.
- Parent-workflow continuation.
- Current hook schemas, trust, and payloads.
- Executable configuration examples.
- Real Codex behavior.

A fresh mirror can faithfully reproduce incompatible instructions.

**Milestone 1: initial checks added; remaining coverage deferred.** Deterministic checks now cover routing preservation (rule 16b), the Codex inventory budget (rule 17), and dependency declarations (`bin/check-cross-references`). Installed-package discovery, partial installations, activation, continuation, hook payloads, configuration examples, and real Codex behavior remain for milestones 2 through 4.

## Validation and acceptance

### Deterministic checks

Run on macOS and Linux:

- Install and inspect packages in an isolated test configuration.
- Validate generated metadata and supported hook/configuration schemas.
- Resolve every shipped script, asset, reference, and documentation link in the installed layout.
- Exercise partial installations, multiple cached versions, symlinks, and paths containing spaces.
- Verify that dollar-prefixed skill mentions survive prompt transport unchanged.
- Test missing dependencies, unavailable capabilities, and restricted destinations.
- Preserve existing mirror, version, cross-reference, and Scrut checks.

### Real-Codex evaluations

Start with the Git and review chain in disposable fixture repositories:

- Explicit invocation and equivalent natural-language requests.
- Appropriate non-activation for adjacent, out-of-scope requests.
- Successful continuation from linting to the authorized parent task.
- Correct stopping on failed or unavailable required checks.
- Respect for active Plan Mode and existing user authorization.
- Correct behavior when only some required plugins are installed.
- Current-package helper selection despite another cached version.
- Worktree handoff, hook trust, and notification behavior.

Use controlled fixtures for GitHub effects. Record CLI and model versions, configuration, results, and relevant transcripts. Do not introduce model-backed checks as mandatory gates until their results are sufficiently repeatable.

### Completion criteria

A user following the Codex guide can install the intended plugins, discover and invoke them, and complete the evaluated workflows without translating Claude instructions manually. Claude behavior remains covered, OpenCode remains functional, and unsupported cases receive accurate explanations.

## Evidence, limitations, and follow-through

The audit covered the repository’s **57 plugins and 56 skill entrypoints**, generated distributions, authoring guidance, configuration examples, helper scripts, and test structure through repository-wide searches and targeted inspection.

Verification results:

- `make validate`: **passed**.
- `make test-scrut`: **392 passed, 10 failed**.
- The failing cases use a fixture that hardcodes `/usr/bin/git`; that executable refuses to run because the local Xcode license is unaccepted. The normal `PATH` Git accepts the tested branch names.
- Installed README link failures and the TOML table-placement defect were directly reproduced.
- Real-agent execution of every skill was **not performed**. Activation and completion risks remain evaluation targets.

Existing related issues, including test portability, configuration budgets, catalog categories, and worktree handoff problems, should be linked or extended where appropriate rather than duplicated.
