# Codex consumption review

Reviewed on 2026-09-15 against repository revision `340f3192`. This document preserves the original audit findings and reported evidence; consolidation does not constitute a new compatibility evaluation. CLI and documentation claims below describe the audit baseline and must be rechecked when milestone 1 begins.

Tracking: [umbrella issue #434](https://github.com/cboone/agent-harness-plugins/issues/434). Implementation: [four-milestone roadmap](../plans/todo/2026-09-15-codex-consumption-improvements.md). Update these documents in place as work proceeds.

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

**2. Hook setup and capability claims are outdated. Confirmed.**

The README tells users to enable `plugin_hooks`. The installed CLI reports that feature as removed and `hooks` as stable.

The repository also says Codex lacks `PreCompact`, `SubagentStop`, and `SessionEnd`. Current documentation supports those events. It additionally requires review and trust of non-managed hook definitions, including plugin hooks, which the repository’s instructions omit. These errors affect both consumers and future plugin authors. [Official hook documentation](https://learn.chatgpt.com/docs/hooks).

**3. Skill invocation examples are Claude-specific throughout the product. Confirmed.**

The root catalog, plugin READMEs, workflow recommendations, and generated prompts predominantly use `/name`.

Codex uses `$` mentions or its `/skills` selector. Documentation should explain explicit invocation, qualified names shown by the selector, and natural-language activation. A skill mention belongs in the conversation, not in a shell command. [Official skill documentation](https://learn.chatgpt.com/docs/build-skills).

A global replacement would be unsafe: legitimate harness commands such as `/skills` must remain, and dollar signs inside shell strings require correct quoting.

**4. Documentation links break after installation. Reproduced.**

The generator adjusts root README links for the repository’s `dist/codex` depth. Installed plugins have a different directory layout.

In the installed `create-worktree` README, installation links resolve to a nonexistent `~/.codex/plugins/README.md`; sibling-plugin links also resolve to nonexistent paths. Repository link checks do not establish that installed documentation works.

Use repository URLs for documentation outside the package and relative links for files bundled inside it.

**5. Project presentation and authoring guidance still position Codex as secondary. Confirmed.**

Examples include the “Claude Code Plugins” title, marketplace description, and instructions describing rich activation descriptions as something maintained for Claude.

The presentation should match the agreed support policy. Existing Claude-compatible manifest locations can remain where supported; their names alone are not defects.

### Discovery and prompt quality

**6. The Codex build deliberately removes activation information. Confirmed transformation; behavioral impact needs evaluation.**

The [Codex generator](https://github.com/cboone/agent-harness-plugins/blob/340f319211b8ebfd64b0d37abda7768886bbf165/bin/build-codex-marketplace#L197) replaces every skill description with its marketplace summary.

That saves context, but removes useful distinctions. For example:

- `plant-defects` loses its detailed activation conditions.
- `write-markdown` loses its explicit review trigger.
- Workflow descriptions lose user phrases, prerequisites, and scope boundaries.

Marketplace summaries and routing descriptions serve different purposes. Codex should receive concise descriptions written for selection, rather than automatically receiving catalog copy. Actual selection accuracy remains unmeasured.

**7. The context-budget check measures only part of discovery overhead. Confirmed coverage gap.**

The generated descriptions total **6,881 characters**, against a repository limit of 12,000. That calculation excludes names, paths, and surrounding metadata.

Codex’s initial skill list includes paths and may shorten descriptions or omit skills when its budget is exceeded. Therefore, the current check cannot establish that the entire installed catalog remains discoverable. [Official skill documentation](https://learn.chatgpt.com/docs/build-skills).

**8. Codex-specific metadata is unused. Improvement opportunity.**

None of the 56 skills ships `agents/openai.yaml`.

Use this selectively for invocation policy, useful interface metadata, and supported tool dependencies. Preserve natural-language activation as agreed. Do not blanket-disable workflow skills merely because their authorized execution can change files or contact GitHub.

**9. Several entrypoints load substantial material before selecting a relevant path. Confirmed structure; improvement needs evaluation.**

Seven skill bodies exceed 500 lines. `release` has 965 lines; `set-up-installers` contains multiple language-specific workflow templates.

Move conditional reference material behind explicit selection steps. Preserve the workflow’s requirements while reducing irrelevant material loaded for a particular task. Several existing style guides already demonstrate this approach.

### Workflow execution and composition

**10. Workflow chains require Claude’s `Skill` tool. Confirmed instruction mismatch.**

Examples include `pr`, `bootstrap-project`, `monitor-pr`, `pin-everything`, and `refresh-project-scaffolding`.

Codex needs instructions for resolving a skill through its advertised location, loading it through the available mechanism, passing the requested options, and continuing the parent workflow. A `$skill` mention is not a substitute tool call.

The existing `lint-and-fix` parent-continuation contract is a useful foundation and should be preserved.

**11. Fallbacks confuse a missing Claude tool with a missing capability. Confirmed.**

Examples:

- Dependabot skills fall back from `AskUserQuestion` directly to plain numbered text.
- `address-issue` distinguishes Claude’s plan tools from an “otherwise Codex” path without handling an already-active Codex Plan Mode.
- Monitoring skills direct Codex toward blocking shell sleeps.
- Report-board instructions associate artifact availability with harness identity.

Adapters should inspect available capabilities. Use structured questions, interruptible waiting, and supported artifact or browser tools when present. Provide a documented fallback when they are absent.

This does not imply that every Codex environment has every capability.

**12. Approval instructions do not adequately distinguish workflow approval from harness restrictions. Confirmed gap.**

“No prompts” and `--no-approval` can describe workflow behavior, but cannot override active Plan Mode, sandbox restrictions, hook trust, or higher-priority instructions.

At the same time, adapters should preserve previously granted authorization and avoid inserting repeated confirmation steps into an authorized workflow.

**13. Selective installation exposes undeclared skill dependencies. Confirmed design gap.**

Plugins such as `pr` and `bootstrap-project` require other skills, while users can install plugins individually. Existing cross-reference checks establish that a referenced plugin exists in this repository, not that it is installed and available to the consuming session.

Distinguish required dependencies from optional recommendations. Detect missing required skills before consequential steps and provide an actionable installation instruction. Do not silently substitute a different workflow.

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
