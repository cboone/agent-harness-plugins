# Installed checklist drift review ledger

## Scope and authority

TOOLING's brief extends validator rule 20 and permits work through a ready PR.
The complete diff takes the full local order. No plugin source or mirrored file
changes, so no plugin bump or mirror rebuild is planned.

## Structural Nit round

Frozen head: 382c13e91384cdd78486222ed7e4bbbfd19d7612.
Read-only standalone Codex: `gpt-6.1-sol`, `high`, window `872000`.
Anti-patterns and the four cleanup angles ran in parallel. Prompts and schema
existed before launch, with SHA-256 records under `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/structural/`.
No fallback was used. The scope comparison found no lasting
changes. Artifact validation and the checked post are recorded at
`/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/structural/gate/receipt.json`.

| Finding                                                                    | Reviewer's label | Our severity                                                           | Take or record                      | Review again                         |
| -------------------------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------- | ----------------------------------- | ------------------------------------ |
| Duplicate absent-directory validator run, reported by reuse and efficiency | suggestion       | Nit: repeated fixture copying and validation without distinct coverage | Take: use the existing catalog case | No: test removal changes no behavior |

The anti-patterns result has no findings. Its mechanical ShellCheck diagnostic
SC2249 is handled as ordinary lint: add the inner case's no-op default arm.
Structural loop ended: fixes changed no behavior.

## Plant and reproduction evidence

Owned plant-defects copy: `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/plant-defects`, version `1.3.0`.
Manifest SHA-256: `4835a585c07d9770d608a95f190e81e2127d34ae7ecd809a8ce8a4385f3bbad2`. Membership, file hashes and modes are
verified before helper use. The copied-load preflight sources the actual Bash
library and runs the unchanged baseline before the gate. A pre-launch self-audit replaced the plant callback with the validator's actual
error function, preserving its diagnostic contract. The fixture contains no
DEBUG trap, BASH_COMMAND instrumentation or test double. Its verdict
checks the error count. The manifest requires the exact stale-file message.
Generated shell sections are checked for nonempty content before sourcing.

Plant gate: `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/plants-gate/receipt.json`.
Reproduction gate: `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/reproduction/receipt.json`.
The latter runs `make build` after renaming the source Markdown rule, then
asserts that `make validate` rejects the stale installed filename.
These receipts describe the frozen pre-cleanup tree; final-tree evidence remains
required before the PR handoff. The installed bodies needed no refresh.

The provisional plant receipt above is superseded: its substitute callback did
not preserve the diagnostic prefix. It must not appear in the merge registry.
Final checked-plant output will be rendered outside the checkout and registered
with a final-tree checked-gate receipt.

## Focused Nit round

Frozen head: 208de7360de9192a79668877242064700e6eb5be.
Code, errors, tests and comments ran read-only through standalone Codex on
`gpt-6.1-sol`, `high`, window `872000`. Types were skipped because no type
definitions changed. No findings; clean at Nit. No subsequent round is due.
Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/focused-review-1/gate/receipt.json`.

## Trimming

The shared trim-text workflow covered prose and the trim-comments alias's
code-comments scope in one read-only pass on `gpt-6.1-sol`, `low`, window
`872000`. All proposals were taken as text-only edits; none were declined.
Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/trim/gate/receipt.json`.

## Callback class audit

A complete diff and touched-file search follows the self-audit correction.
The actual error function replaces the substitute, so its prefix and error
counter remain the production implementation. No other callback copy remains.
Search evidence: `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/callback-site-audit.txt`.

| File                                                                                    | Sites checked, including unchanged sites                                                                                      |
| --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `bin/validate-plugins`                                                                  | Real error function, rule 19/20/22 annotation relays, installed-body loop; no callback replacement                            |
| `tests/fixtures/validate-plugin-fixture`                                                | Installed scenarios, generator wrappers and grep/awk error doubles; no error callback; tool error exits remain contract-valid |
| `tests/scrut/validate-plugins-skills.md`                                                | Existing and added exact diagnostic prefixes; absent-directory coverage stays in the catalog case                             |
| `docs/reviews/2026-11-07-installed-checklist-drift-plants/check.bash`                   | Real error-function and rule extraction, nonempty guards, explicit verdict                                                    |
| `2026-11-07-installed-checklist-drift-plants.json`                                      | Exact green diagnostic and assertion marker, red assertion marker, complete input list                                        |
| `docs/reviews/2026-11-07-installed-checklist-drift-plants/remove-body-comparison.patch` | Only the production body comparison is removed                                                                                |
| `docs/plans/todo/2026-11-07-installed-checklist-drift.md`                               | Filename mapping and current/absent/stale/pin/orphan claims map to fixture scenarios                                          |
| `docs/plugin-development.md`                                                            | Installed-body and repair claims map to the same fixture scenarios                                                            |
| `docs/reviews/2026-11-07-installed-checklist-drift.md`                                  | Superseded callback evidence withdrawn; final-tree proof remains required                                                     |

The changed production comparison is the committed plant target. Prose claims
about stale bodies map to `installed-stale` and the comparison-removal plant;
optional installation, ignored pins and orphan reporting map to the existing
catalog `valid` case, `installed-stale-pin` and `installed-orphan` respectively.

## Semgrep baseline

The disposable shared clone ran the native baseline invocation against the
actual merge base. Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/semgrep/gate-config-corrected/receipt.json`.
The initial incompatible auto/metrics-off command is retained as a failed run
at `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/semgrep/gate/receipt.json`; it provides no scan evidence.

The completed invocation reports no findings but has PartialParsing in unchanged
rule 17 code. Every reported span matches the merge base and overlaps no changed
line, as `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/semgrep/coverage-proof.json` records. This is an existing parser
limitation, not a clean full-file scan. TOOLING accepted this bounded coverage
as the branch's Semgrep step in mailbox message `000002-20261107T112705Z`.
No parser workaround or rule 17 change was made.

## Lint and fix without push

Receipt: `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/lint/gate/receipt.json`.
The project-prescribed `make lint`, `make validate` and `git diff --check`
completed. Check-only mode applies by project policy because `make format`
reaches protected Scrut files. No fixer ran, no required local tool was skipped,
and no files needed changing. With no edits during this check-only run, it is
also the final lint verification for that recorded tree. Fresh final-tree lint
and validation evidence is required after this record changes.

## Final evidence contract

Signed tidy must preserve the complete tree. The final non-heavy gate checks
that comparison, current-main ancestry, versions, lint and validation, the real
callback plant, the exact issue reproduction and the bounded Semgrep result.
Its spec, environment and receipt belong under `/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/final-nonheavy`.

TOOLING's heavy-suite hold is active at this record's freeze. No heavy run was
queued or acquired here. After TOOLING lifts it, fetch current main, incorporate
any moved base and run `make test-all` through `suite-lock run heavy` on the
resulting head. Preserve its spec, environment and receipt under
`/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/final-heavy`. The external précis records actual gate states, the parser
limitation and CI state; missing or stale evidence cannot authorize a merge.
The worker stops at the ready PR report and never merges.

## Full-suite fixture contract correction

The refreshed-head full-suite receipt is retained at
`/Users/ctm/.local/state/codex-mailboxes/tooling/499-installed-checklist-drift/evidence/final-heavy/gate/receipt.json`.
Its `make test-all` check exited 2. The failures were the plant
manifest's missing normal-verdict compatibility rows and its undeclared shell
detector wait, not a lock wait or load issue.

The compatibility inventory now contains captured baseline, red and restored
rows from the real-callback plant result. A Python entry declares the Bash
detector's bounded wait; the shell launcher delegates to it. The assertion,
mutation patch and production validator behavior are unchanged. The targeted
checked-plant and checked-timeout-budgets documents, lint and validation must run
before another tidy and final gate. Review counts remain unchanged under
TOOLING's message `000007-20261107T133407Z`.
