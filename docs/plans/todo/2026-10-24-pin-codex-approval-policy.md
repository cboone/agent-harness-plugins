# Keep scripted Codex runs sandboxed and offline (#631)

## Context

The review and trim skills run `codex exec --sandbox read-only` and set no approval policy, so the user's Codex configuration supplies one. Under `approval_policy = "on-request"` with an automatic approval reviewer, a run can ask to run a command with escalated permissions, the reviewer approves it, and the command runs outside the sandbox with the user's credentials. Every scripted run should set `approval_policy="never"`, so a request to escalate fails inside the sandbox.

Codex's built-in web search is a model tool that reaches the network without running a command, so neither the sandbox nor the approval policy governs it. The scope widened (2026-10-24) to turn it off too: every scripted run also sets `web_search="disabled"`. Codex 0.163.0 names the setting `web_search`, with values `live`, `indexed`, `cached` and `disabled`; it accepts `-c 'web_search="disabled"'` and rejects an unknown value when it loads its configuration.

**Classification:** fix (`fix`). One branch, one PR.

## Changes

1. `review-anti-patterns`'s `references/codex-exec.md`, the shared source of the `trim-comments` and `trim-text` copies: the invocation gains `--config 'approval_policy="never"'` and `--config 'web_search="disabled"'`, and the reasons list says why each is needed.
1. `review-pr-with-codex`: `codex-aspects run` always passes both settings, for every aspect, `simplify` included; it takes no option to remove them. `references/invocation.md` shows them in the invocation and gives their reasons; `SKILL.md` mentions them where it describes `run`.
1. The four plugin READMEs say both settings keep a run's commands and web search offline, and that MCP servers in the user's Codex configuration are not covered. `simplify`'s `workspace-write` run also turns off that sandbox's network access.
1. `bin/validate-plugins` rule 23: every scripted `codex exec` run under `plugins/` must pass both settings, each as a `--config` or `-c` argument, and an error names the settings a run lacks. `docs/plugin-development.md` defines a run and documents the rule; `bin/AGENTS.md` names it.
1. Tests: `tests/scrut/codex-aspects.md` expects both settings in the recorded arguments of a review run, the defaults run and a `simplify` run. `tests/scrut/validate-plugins-codex-exec.md` covers rule 23 with four fixture scenarios: one failing, one passing, and two in which the rule's own search or scan fails. Its own document keeps `validate-plugins-skills.md` from growing.
1. Patch bumps: `review-anti-patterns` 1.1.2, `trim-comments` 2.1.1, `trim-text` 1.1.1, `review-pr-with-codex` 2.1.1. `make build` regenerates the copies and `dist/codex/`.

## Design calls

- **A validator rule rather than a scrut-only scan.** `bin/validate-plugins` is a merge gate and already holds catalog-wide content rules, so a run added later without the settings fails `make validate` as well as CI.
- **Always on in `codex-aspects`, with no opt-out.** `codex-aspects run` passes both settings unconditionally, which covers the issue's request and leaves no way to run without them.
- **`simplify` gets them too.** Its `workspace-write` sandbox still bounds what it may write, and an escalation would let it leave that bound.
- **Settings read as arguments, by line.** The rule counts a setting only where it follows `--config` or `-c`, so a plain mention in a prompt or another command does not satisfy it. It reads lines, not shell words, so flag-shaped text inside a quoted prompt or a trailing comment can satisfy it. Chris chose to record that limitation in `docs/plugin-development.md` rather than parse shell words.

## Out of scope

- The capture directory's removal (a separate issue).

## Manual check

The issue's last item, a run whose prompt needs a network command failing rather than leaving its sandbox, needs a live Codex call against a real account; the stub cannot show what Codex itself does. It goes in the PR as a manual check: under a Codex configuration with `approval_policy = "on-request"`, an automatic approval reviewer and web search on, run a read-only `codex exec` with both settings whose prompt asks for `gh repo view` and a web search, and confirm the command fails inside the sandbox, no escalation is requested or approved, and no web search runs.

## Verification

- `make build`, `make test-all` and the `check-versions` skill.
- Planted defects against the settings in each source and against rule 23 itself, recorded in the local review ledger.
