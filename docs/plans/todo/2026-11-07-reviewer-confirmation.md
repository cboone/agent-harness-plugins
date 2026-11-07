# Report reviewer confirmation

For [the reviewer detection issue](https://github.com/cboone/agent-harness-plugins/issues/501), extend the existing repository inspection and final report. Keep all three installation surfaces and existing checklist pin resolution. Detection adds no network or GitHub CLI calls. No live configuration changes.

## Evidence and design

- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions) uses repository workflows and can perform tasks other than review. Inspect both YAML extensions, action usage, triggers, conditions and review prompts. Report paths and review wiring, without claiming successful execution.
- [Claude Code Review setup](https://code.claude.com/docs/en/code-review-setup) uses the Claude GitHub App and organization repository settings. A missing workflow means "not confirmable from the repository", not disabled.
- [Codex GitHub review](https://learn.chatgpt.com/docs/third-party/github) is enabled in Codex settings outside the tree. Always report it as unverifiable here.
- [Copilot review configuration](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review) uses GitHub settings and rulesets. Installed instructions cannot confirm activation. Qualify the existing report's promise of review.
- Existing step 4 already uses `git ls-remote` and `curl` for checklist pins; preserve that behavior. Reuse the current inspection, report and Scrut instruction-contract suite rather than add a detector tool.

## Implementation and validation

1. Add workflow evidence to step 1; separate confirmed repository wiring from unconfirmed reviewer activation in step 8.
1. Add workflow-present, workflow-absent and Codex instruction contracts. These measure prompt delivery, not model adherence. Plant the old unconditional Codex wording through the checked runner.
1. Patch-bump set-up-review-config and rebuild the Codex mirror. Use the brief's small-change review path: one frozen-SHA Codex round, escalating if required by size or findings.
1. Run lint, versions and the heavy-locked full suite on the current-main PR tree; keep gate environments and evidence outside the checkout. Open a ready PR and report to TOOLING; merging belongs to the conductor.

TOOLING approved the recurring-class audit and the bootstrap summary correction. The full review order applies because retained process artifacts exceed the small-change limit; counts carry forward. Patch-bump bootstrap-project and plant each changed claim site, including the README and bootstrap consumers.
