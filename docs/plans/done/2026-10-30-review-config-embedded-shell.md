# Route embedded Bash through review configuration

Issue: [embedded shell routing](https://github.com/cboone/agent-harness-plugins/issues/502).

## Decisions and prior art

- Extend the existing guide detection and templates; no new plugin, parser or live installation.
- [actionlint](https://github.com/rhysd/actionlint/blob/main/docs/checks.md#shellcheck-integration) checks `run:` contents using the effective shell, only invokes ShellCheck when available, and disables some diagnostics. Adopt shell-aware content boundaries; retain review of checklist defects outside the enabled diagnostics.
- [CodeRabbit path instructions](https://docs.coderabbit.ai/configuration/path-instructions) pair path globs with focused prose. Adopt that form, rather than routing entire YAML files as Bash.
- [Actions shell defaults](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstepsshell) distinguish implicit non-Windows Bash, explicit Bash, and other shells. Resolve step, job and workflow defaults, runner and container before selecting a checklist. Do not assume every `run:` is Bash.
- Include Make recipes only when their effective shell is Bash; default POSIX recipes stay unsupported. Tracked git hooks already follow shebang detection. Never inspect or alter untracked live hooks.
- CI suppression stays diagnostic-specific in all three installed surfaces. An enabled ShellCheck diagnostic is suppressed; a missing pipeline-status check remains reviewable with its checklist citation and severity.
- Related [uncited-findings PR](https://github.com/cboone/agent-harness-plugins/pull/692) is open on inspection, despite the brief's merged note. Leave its citation and grouping changes separate; coordinate shared template and version integration with TOOLING.

## Implementation and validation

1. Extend Bash detection and routing, add a shared embedded-shell instruction in entry skill, AGENTS and REVIEW templates, and bump the plugin patch version beyond the related branch's 1.0.4.
1. Regenerate with `make build`. Check representative Bash-only workflows, non-Bash workflows, Bash-selected and POSIX Make recipes, and tracked hooks against the written instructions. Run the affected checklist-generation Scrut file. No executable detection helper exists, so string snapshots would not establish model adherence.
1. Use the small-change path if the final authored diff stays under about 100 lines, outside security: one `review-pr-with-codex` Nit round, then lint, version checks and exact-tree tidy. Otherwise run the full local review order.
1. Run `make test-all` once with `SCRUT_JOBS=2` under the TOOLING full-suite directory lock. Record the known baseline fixture and macOS load failures separately. Push and open a ready PR; TOOLING merges. No live config changes.

Implementation and local review are complete; [validation evidence](../../reviews/2026-10-30-review-config-embedded-shell.md) records the known baseline failures. Publication uses the existing worker go-ahead.
