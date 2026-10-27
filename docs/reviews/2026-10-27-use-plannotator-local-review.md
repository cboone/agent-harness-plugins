# Use Plannotator local review

## Scope and authority

Add the portable `use-plannotator` plugin on `main` at `9aa57802`.
The relayed Inbox go-ahead dated 2026-10-27, 7:19 PM ET authorizes building
through a PR ready for review. Merging remains with Chris (he/him), with an
additional confirmation in TOOLING's window because the change adds agent instructions.

Sources: installed `plannotator inbox --help`, including the current
`send_message`, `read_thread` and `wait_for_reply` documentation, and the
project's existing Inbox reference. No live messages or project-rule edits.
Board cards and project-specific waiting, identity and launch mechanisms are excluded.

## Structural review

One Nit round: anti-pattern review and report-only simplify in parallel, in
fresh standalone Codex contexts using `gpt-6.1-sol`, high effort, window 872000,
read-only sandbox, approval policy `never`, web search disabled and stdin closed.
Both exited zero and returned nonempty completed reports; anti-pattern JSON
passed its supplied schema check. All five canonical changed files were read.
Generated mirrors were excluded. No lasting review edits were observed.

- Anti-pattern findings: none. End state: clean at Nit.
- Simplify finding: reviewer label `suggestion`; our severity Nit because
  “one choice” could mean either one available option or one permitted selection.
  Take: use “single selection” and “multiple selections”. Review again: no,
  wording alone changed. Combined loop ended: fixes changed no behavior.
- Author check: added inline-code formatting to the root README trigger and
  removed a blank line splitting its external-tool list.

Repository validation passed. Live Inbox interactions were not exercised;
the skill relies on the connected tools' current field descriptions.

## Focused review

Nit round: code and comments aspects ran in parallel through the installed
`codex-aspects` helper with the structural review's model and read-only settings.
Both completed successfully and passed schema and snapshot validation.
The before/after scope check found no lasting changes or scope movement.
Errors, tests and types aspects were omitted because no executable logic,
tests, error handling or type definitions changed.

- Code findings: none.
- Comments finding: reviewer label `important`; our severity Important because
  waiting on explicitly closed questions could block progress indefinitely.
  Take: distinguish the explicit “Set aside for now; don't wait on these” reply,
  which closes listed questions, from marking a thread read for later, which
  leaves them pending. Review again: yes, the instruction changes waiting behavior.

First Important round: both code and comments aspects completed successfully
with no findings. Schema checks passed, and the before/after scope was unchanged.
End state: clean at Important. No recurrence or design decisions were needed.

## Trims

One read-only `trim-text` and `trim-comments` pass through fresh Codex,
`gpt-6.1-sol`, low effort, window 872000. The run exited zero and returned
the required file classifications and proposal tables. Accepted three wording
shortenings, preserving requirements: “avoid depending on”, “When a message”
and “no lasting changes or scope movement”. No in-scope code comments changed.
No behavior changed; no further review round was required.

## Semgrep baseline scan

The required baseline scan ran in a disposable shared clone of signed head
`7e48ece6`, comparing with merge base `9aa57802` and setting
`SEMGREP_REPO_NAME=cboone/agent-harness-plugins`. The invocation used
`semgrep scan --config auto --metrics off --baseline-commit <merge-base>`.
It exited 2 before scanning: “Cannot create auto config when metrics are off.
Please allow metrics or run with a specific config.” No findings or coverage
were established by that attempt. Reported to TOOLING at the required stop.

TOOLING subsequently authorized dropping `--metrics off` within the original
go-ahead. The completed scan used:

```bash
SEMGREP_REPO_NAME=cboone/agent-harness-plugins \
  semgrep scan --config auto \
  --baseline-commit 9aa57802460a2f20e1a14be0ece929a99d5565cc \
  --json-output /tmp/use-plannotator-review.udP2SB/semgrep.json
```

Result: exit 0, 128 rules on 7 changed files, 0 findings and an empty JSON
`errors` array. Reported parsed lines: about 100 percent. Three generated
mirror files were skipped by ignore patterns. No new boundary tests were added,
so no planted-defect run applies to this documentation-only plugin.

## Test run

`make test-all` passed Markdown/Prettier, ShellCheck, shfmt, actionlint, JSON
and plugin validation. Scrut completed: 30 of 31 documents passed. Only
`launch-workmux.md` failed, exit 50, with 40 of 62 cases succeeding and 22 failing;
`make test-all` exited 2. The launcher and tests are unchanged by this branch.

TOOLING authorized treating this sole failure as passing the local gate and
required green PR CI. TOOLING reproduced the launcher failure independently on
this machine, with 17 of 62 cases failing, and reported passing main CI at
`9aa57802`. Existing load/flakiness tracking:
[launcher timing](https://github.com/cboone/agent-harness-plugins/issues/439),
[launcher test reliability](https://github.com/cboone/agent-harness-plugins/issues/397)
and [generated branch cases](https://github.com/cboone/agent-harness-plugins/issues/435).
No investigation or changes to the launcher were made.

## Version check

The `check-versions` skill comparison with `origin/main` at `9aa57802` found
only the new `use-plannotator` plugin, correctly starting at `1.0.0`.
All 60 plugin directories have catalog entries and valid manifest-owned versions;
present Codex manifests match, and catalog entries and metadata contain no versions.
Result: all clear.

## Final lint and tidy

`lint-and-fix --no-push` used `make format`, then `make lint`, `make validate`
and `make build` with a generated-output drift check. Every command passed.
The formatter left no additional changes. There were no policy downgrades,
skipped required tools or unresolved findings. Lint status: success.

The unpublished branch is tidied into a feature commit and a review-record
commit, with backup branch `feature/add-use-plannotator-skill-pre-tidy`.
The tidy must preserve the backup tree exactly. PR CI must pass before handoff.
