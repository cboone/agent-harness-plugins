# Codex consumption improvements

Tracking: [umbrella issue #434](https://github.com/cboone/agent-harness-plugins/issues/434). Evidence: [Codex consumption review](../../reviews/codex-consumption.md).

This is one coordinated workstream. The four milestone checklists replace the proposed 13-issue execution breakdown. Update this roadmap and the review in place; use focused, GPG-signed commits at logical boundaries. Milestone 1 is complete, as its [implementation plan](../done/2026-09-18-finish-codex-compatibility-milestone-1.md) and the review's [milestone 1 verification](../../reviews/codex-consumption.md#milestone-1-verification) record. Milestones 2 through 4 remain.

## Objective

Make Codex CLI a fully supported consumer of the plugin catalog. Users should be able to install, discover, invoke, and complete supported workflows without translating Claude-specific instructions manually.

Use shared workflows with harness-specific adapters. Preserve each harness’s capabilities, existing plugin names, and natural-language activation.

## Support policy

- Target the current stable Codex CLI on macOS and Linux.
- Give Claude and Codex equal support while preserving OpenCode functionality.
- Treat desktop, IDE, and cloud differences as documented secondary considerations.
- Prioritize the Git and review workflow chain.
- Use deterministic CI checks and real-Codex evaluations for releases and selected changes.

## Milestone 1: Establish the baseline and adapter design

- [x] Record the supported CLI baseline and correct installation, plugin-management, and hook-trust guidance.
- [x] Establish shared authoring conventions and harness adapters for invocation, tools, capabilities, permissions, and continuation.
- [x] Separate activation descriptions from catalog summaries and define required versus optional skill dependencies.
- [x] Add initial compatibility checks alongside the design.

## Milestone 2: Prove the design on the Git and review chain

- [ ] Apply the design to commit, linting, PR creation, branch review, review resolution, and Copilot-feedback handling.
- [ ] Preserve options, existing authorization, parent continuation, and accurate failure reporting.
- [ ] Verify explicit invocation, natural-language activation, partial installations, and package-relative helper resolution.
- [ ] Evaluate connected workflows with real Codex in disposable repositories.

## Milestone 3: Apply the design across the catalog

- [ ] Correct invocation examples, generated handoffs, cross-references, and installed documentation links.
- [ ] Make worktree prompts destination-aware and handle writable-location requirements explicitly.
- [ ] Correct Codex configuration examples and downstream scaffolding guidance.
- [ ] Update monitoring and notification behavior against available capabilities.
- [ ] Improve conditional reference loading and update plugin-authoring guidance.
- [ ] Add regression coverage with each change and preserve OpenCode behavior.

## Milestone 4: Verify the complete distribution

- [ ] Run package and configuration checks on macOS and Linux.
- [ ] Cover multiple cached versions, symlinks, paths containing spaces, missing dependencies, and restricted destinations.
- [ ] Verify hook trust and payload handling, prompt transport, activation, and workflow continuation.
- [ ] Check Claude behavior and OpenCode functionality.
- [ ] Record evaluation versions, results, limitations, and any deliberately deferred work.
- [ ] Complete repository validation, version checks, and generated-mirror checks.

## Related work

Coordinate with existing issues rather than duplicating their scope:

- [#358: Respect project linter constraints](https://github.com/cboone/agent-harness-plugins/issues/358), relevant to milestone 2.
- [#413: Separate worktree chaining instructions from naming input](https://github.com/cboone/agent-harness-plugins/issues/413), relevant to milestone 3.
- [#373: Configuration-budget tooling](https://github.com/cboone/agent-harness-plugins/issues/373), related context measurement work, not a prerequisite.
- [#394: Catalog recategorization](https://github.com/cboone/agent-harness-plugins/issues/394), independently tracked and outside the initial compatibility changes.

Create additional issues only for independently shippable work, deliberate deferrals, or discoveries outside this scope.

## Acceptance and evidence

A user following the Codex guide can install, discover, invoke, and complete evaluated workflows without manually translating Claude-specific instructions. Preserve existing user-facing options and plugin boundaries. Record unsupported cases accurately.

Use the deterministic checks and real-Codex evaluation scenarios in the review. Record CLI and model versions, configuration, results, and relevant transcripts. Use controlled GitHub fixtures and disposable repositories. Model-backed checks become mandatory gates only after sufficient repeatability is established.

The original audit reported `make validate` passing and `make test-scrut` reporting **392 passed, 10 failed**. The failing cases were associated with a fixture that hardcodes `/usr/bin/git` and the local unaccepted Xcode license. Installed README link failures and TOML table placement were reproduced. Real-agent execution of every skill was not performed. These historical results do not establish a fully passing baseline suite.
